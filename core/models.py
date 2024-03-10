import datetime

from django.db import models
from django.utils import timezone


class Email(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} ({self.name})"

    class Meta:
        ordering = ["-created_at"]
        get_latest_by = "created_at"


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
    scheduler = models.ForeignKey(Scheduler, related_name="dispatches", on_delete=models.SET_NULL, null=True,
                                  blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sent_at = models.DateTimeField(null=True, blank=True, editable=False)

    def send(self) -> None:
        raise NotImplementedError

    def is_due(self) -> bool:
        """ This must be substituted by celery / celery-beat """
        """Check if the dispatch is scheduled to be sent now."""
        if not self.scheduler:
            return False

        now = timezone.now()
        if self.last_sent_at:
            last_sent = self.last_sent_at.astimezone(timezone.utc)
        else:
            # For new dispatches, use the date part of the current time and the scheduled time to determine if it's due
            last_sent = None

        # Set the initial scheduled time for today or the day of last sent if available
        scheduled_date = last_sent.date() if last_sent else now.date()
        scheduled_time = datetime.datetime.combine(scheduled_date, self.scheduler.time_of_day, tzinfo=timezone.utc)

        if last_sent:  # Adjust scheduled_time based on the frequency and last_sent for existing dispatches
            if self.scheduler.frequency == 'daily':
                next_due = scheduled_time
            elif self.scheduler.frequency == 'weekly':
                next_due = scheduled_time + datetime.timedelta(
                    days=7 * ((now.date() - scheduled_time.date()).days // 7))
            elif self.scheduler.frequency == 'monthly':
                # Handle monthly frequency with potential for refinement
                month_increment = ((now.year - scheduled_time.year) * 12 + now.month - scheduled_time.month)
                next_due_year = scheduled_time.year + ((scheduled_time.month + month_increment) // 12)
                next_due_month = (scheduled_time.month + month_increment) % 12 or 12
                next_due_day = min(scheduled_time.day, [31,
                                                        29 if next_due_year % 4 == 0 and next_due_year % 100 != 0 or next_due_year % 400 == 0 else 28,
                                                        31, 30, 31, 30, 31, 31, 30, 31, 30, 31][next_due_month - 1])
                next_due = scheduled_time.replace(year=next_due_year, month=next_due_month, day=next_due_day)
        else:
            next_due = scheduled_time

        tolerance = datetime.timedelta(minutes=5)
        is_due = next_due <= now <= (next_due + tolerance)

        return is_due

    def get_recipient_count(self) -> int | None:
        if not self.send_list:
            return None
        return len(self.send_list.emails.all())

    class Meta:
        ordering = ["-created_at"]
        get_latest_by = "created_at"
        verbose_name_plural = "Dispatches"
