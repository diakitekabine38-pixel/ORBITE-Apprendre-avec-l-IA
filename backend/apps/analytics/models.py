from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Event(TimeStampedModel):
    """Analytics events: lesson_started, lesson_completed, course_purchased…"""

    EVENT_CHOICES = [
        ("lesson_started", "Leçon démarrée"),
        ("lesson_completed", "Leçon terminée"),
        ("quiz_completed", "Quiz terminé"),
        ("exercise_submitted", "Exercice soumis"),
        ("ai_session_started", "Session IA"),
        ("course_purchased", "Formation achetée"),
        ("certificate_issued", "Certificat délivré"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    event_type = models.CharField(max_length=40, choices=EVENT_CHOICES, db_index=True)
    context = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["event_type", "-created_at"])]

    def __str__(self):
        return f"{self.event_type} @ {self.created_at}"