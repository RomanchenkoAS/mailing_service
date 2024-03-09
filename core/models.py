from django.db import models


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

    class Meta:
        verbose_name = "Emails send list"
        verbose_name_plural = "Emails send lists"


class Footer(models.Model):
    text = models.CharField(max_length=255, blank=True, null=True)


class Dispatch(models.Model):
    title = models.CharField(max_length=255, unique=True)
    send_list = models.ForeignKey(SendList, related_name="dispatch", on_delete=models.PROTECT, blank=True, null=True)
    subject = models.CharField(max_length=255, help_text="Letter subject")
    text = models.TextField()
    footer = models.ForeignKey(Footer, related_name="dispatch", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)

    def send(self) -> None:
        raise NotImplementedError

    def is_due(self) -> bool:
        """Check if the dispatch is scheduled to be sent now."""
        raise NotImplementedError

    def get_recipient_count(self) -> int | None:
        if not self.send_list:
            return None
        return len(self.send_list.emails.all())

    class Meta:
        ordering = ["-created_at"]
        get_latest_by = "created_at"
        verbose_name_plural = "Dispatches"
