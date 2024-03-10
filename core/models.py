import datetime

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
        if not self.scheduler:
            self.next_due_at = None
            return

        n = now()
        scheduled_time_today = make_aware(datetime.datetime.combine(n.date(), self.scheduler.time_of_day))
        next_due = scheduled_time_today  # Default to today for daily

        match self.scheduler.frequency:
            case 'daily':
                next_due = scheduled_time_today
            case 'weekly':
                next_due += datetime.timedelta(days=(7 - scheduled_time_today.weekday()))
            case 'monthly':
                month = (scheduled_time_today.month % 12) + 1
                year = scheduled_time_today.year + (scheduled_time_today.month + 1 > 12)
                day = min(scheduled_time_today.day, [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
                next_due = make_aware(
                    datetime.datetime(year, month, day, scheduled_time_today.hour, scheduled_time_today.minute))

        # Adjust for dispatches that should have already been sent
        if next_due <= n:
            match self.scheduler.frequency:
                case 'daily':
                    next_due += datetime.timedelta(days=1)
                case 'weekly':
                    next_due += datetime.timedelta(weeks=1)
                case 'monthly':
                    next_due = next_due.replace(month=(next_due.month % 12) + 1)
                    if next_due.month == 1:
                        next_due = next_due.replace(year=next_due.year + 1)

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
