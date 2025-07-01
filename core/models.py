import datetime
import calendar

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now, make_aware


class Email(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} ({self.name})"

    def send_email(self, subject: str, message: str, footer_text: str = "") -> None:
        """Sends an email to this Email address instance."""
        full_message = f"{message}\n\n{footer_text}" if footer_text else message
        send_mail(
            subject=subject,
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email],
            fail_silently=False,
        )

    class Meta:
        ordering = ["-created_at"]
        get_latest_by = "created_at"
        verbose_name = "Email address"
        verbose_name_plural = "Email addresses"


class SendList(models.Model):
    title = models.CharField(max_length=255, unique=True)
    emails = models.ManyToManyField(Email, related_name="send_list")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Emails send list"
        verbose_name_plural = "Emails send lists"


class Footer(models.Model):
    title = models.CharField(max_length=255, unique=True, help_text="Identifier, is not included into email.")
    text = models.CharField(max_length=255, blank=True, null=True, help_text="Email footer text.")

    def __str__(self):
        return self.title


class Scheduler(models.Model):
    FREQUENCY_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='daily')
    time_of_day = models.TimeField(help_text="Time of day to send the emails (HH:MM:SS format).")

    def __str__(self):
        return f"{self.frequency} at {self.time_of_day}"


class Dispatch(models.Model):
    title = models.CharField(max_length=255, unique=True)
    send_list = models.ForeignKey(SendList, related_name="dispatch", on_delete=models.PROTECT, blank=True, null=True)
    subject = models.CharField(max_length=255, help_text="Letter subject")
    text = models.TextField()
    footer = models.ForeignKey(Footer, related_name="dispatch", on_delete=models.PROTECT, blank=True, null=True)
    scheduler = models.ForeignKey(Scheduler, related_name="dispatches", on_delete=models.PROTECT, null=True,
                                  blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sent_at = models.DateTimeField(null=True, blank=True, editable=False)
    next_due_at = models.DateTimeField(null=True, blank=True)
    sent_times = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def is_active(self) -> bool:
        return True if self.next_due_at else False

    def get_absolute_url(self):
        return reverse('dispatch-detail', args=[self.pk])

    def toggle_activation(self):
        if self.next_due_at is None:
            self.update_next_due_at(save=True)
        else:
            self.next_due_at = None
            self.save(update_fields=['next_due_at'])

    def send(self) -> None:
        """Composes and sends dispatch to each user in the send list."""
        if not self.send_list:
            return

        footer_text = self.footer.text if self.footer else ""
        for email in self.send_list.emails.filter(active=True):
            email.send_email(subject=self.subject, message=self.text, footer_text=footer_text)

        self.last_sent_at = timezone.now()
        self.sent_times += self.get_recipient_count()
        self.update_next_due_at()
        self.save()

    def update_next_due_at(self, save: bool = False) -> None:
        """
            Calculate and set field next_due_at depending on chosen scheduler frequency.
        """
        if not self.scheduler:
            self.next_due_at = None
            return

        current_time = now()
        today = current_time.date()
        scheduled_time = self.scheduler.time_of_day

        # Create today's scheduled datetime
        scheduled_datetime_today = make_aware(
            datetime.datetime.combine(today, scheduled_time)
        )

        match self.scheduler.frequency:
            case 'daily':
                # If today's time has passed, schedule for tomorrow
                if current_time >= scheduled_datetime_today:
                    next_due = scheduled_datetime_today + datetime.timedelta(days=1)
                else:
                    next_due = scheduled_datetime_today

            case 'weekly':
                # If today's time has passed, schedule for next week same day
                if current_time >= scheduled_datetime_today:
                    next_due = scheduled_datetime_today + datetime.timedelta(days=7)
                else:
                    next_due = scheduled_datetime_today

            case 'monthly':
                # Calculate next month's date
                if current_time >= scheduled_datetime_today:
                    # Move to next month
                    if today.month == 12:
                        next_year = today.year + 1
                        next_month = 1
                    else:
                        next_year = today.year
                        next_month = today.month + 1

                    # Handle month length differences
                    max_day_in_next_month = calendar.monthrange(next_year, next_month)[1]
                    next_day = min(today.day, max_day_in_next_month)

                    next_due = make_aware(
                        datetime.datetime(
                            next_year, next_month, next_day,
                            scheduled_time.hour, scheduled_time.minute, scheduled_time.second
                        )
                    )
                else:
                    next_due = scheduled_datetime_today
            case _:
                raise ValueError(f"Misconfigured scheduler: {self.scheduler.frequency}")

        self.next_due_at = next_due
        if save:
            self.save(update_fields=['next_due_at'])

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if this is a new instance
        scheduler_changed = False

        if not is_new:
            # Fetch the current Dispatch from the database to check if the Scheduler has changed
            current_dispatch = Dispatch.objects.get(pk=self.pk)
            scheduler_changed = self.scheduler_id != current_dispatch.scheduler_id

        if is_new or scheduler_changed:
            # Recalculate next_due_at for new instances or if the scheduler has changed
            self.update_next_due_at()

        super().save(*args, **kwargs)

    def is_due(self) -> bool:
        if not self.next_due_at:
            return False
        return now() >= self.next_due_at

    def get_recipient_count(self) -> int | None:
        if not self.send_list:
            return None
        return len(self.send_list.emails.all()) if self.send_list else None

    def get_last_sent(self) -> str:
        if self.last_sent_at is not None:
            return self.last_sent_at.strftime("%Y-%m-%d %H:%M:%S")
        return "Was never sent yet."

    class Meta:
        ordering = ["-created_at"]
        get_latest_by = "created_at"
        verbose_name_plural = "Dispatches"
