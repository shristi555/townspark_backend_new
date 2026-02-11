from django.db import models
from django.conf import settings

class Notification(models.Model):
    """
    Model to store user notifications/activity logs.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="User who triggered or receives the notification"
    )
    event = models.CharField(max_length=255, help_text="Event type e.g., 'user_updated', 'issue_created'")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # extra_id is used to store the id of the object that triggered the notification
    related_id = models.IntegerField(blank=True, null=True)
    # it can be null if user releted notifications

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"
 