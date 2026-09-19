from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Notification(TimeStampedModel):
    TYPE_PEDAGOGIC = "pedagogic"
    TYPE_AI = "ai"
    TYPE_COMMERCIAL = "commercial"
    TYPE_SYSTEM = "system"

    TYPE_CHOICES = [
        (TYPE_PEDAGOGIC, "Pédagogique"),
        (TYPE_AI, "IA"),
        (TYPE_COMMERCIAL, "Commerciale"),
        (TYPE_SYSTEM, "Système"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE
    )
    notification_type = models.CharField(max_length=16, choices=TYPE_CHOICES, default=TYPE_SYSTEM)
    title = models.CharField(max_length=160)
    message = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} — {self.title}"