from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class AIAgent(models.Model):
    """A specialised pedagogical personality (KODEX, KORA, NOVA, PIXEL…)."""

    code = models.SlugField(unique=True)
    name = models.CharField(max_length=64)
    specialty = models.CharField(max_length=160)
    personality = models.TextField(blank=True)
    system_prompt = models.TextField(blank=True)
    teaching_rules = models.JSONField(default=list, blank=True)
    expertise = models.CharField(max_length=64, default="intermediate")
    color = models.CharField(max_length=16, default="#7C5CFF")
    model = models.CharField(max_length=64, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class AISession(TimeStampedModel):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = [(STATUS_OPEN, "Ouverte"), (STATUS_CLOSED, "Fermée")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ai_sessions", on_delete=models.CASCADE)
    agent = models.ForeignKey(AIAgent, related_name="sessions", on_delete=models.CASCADE)
    course = models.ForeignKey(
        "courses.Course", related_name="ai_sessions", on_delete=models.SET_NULL, null=True, blank=True
    )
    lesson = models.ForeignKey(
        "courses.Lesson", related_name="ai_sessions", on_delete=models.SET_NULL, null=True, blank=True
    )
    title = models.CharField(max_length=200, blank=True, default="")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OPEN)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user} ↔ {self.agent}"


class AIMessage(TimeStampedModel):
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_SYSTEM = "system"

    ROLE_CHOICES = [
        (ROLE_USER, "Utilisateur"),
        (ROLE_ASSISTANT, "Assistant"),
        (ROLE_SYSTEM, "Système"),
    ]

    session = models.ForeignKey(AISession, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.session_id} [{self.role}]"


class AIMemory(TimeStampedModel):
    """Pedagogical memory attached to a learner (difficulties, preferences…)."""

    CATEGORY_PEDAGOGIC = "pedagogic"
    CATEGORY_PREFERENCE = "preference"
    CATEGORY_HISTORY = "history"

    CATEGORY_CHOICES = [
        (CATEGORY_PEDAGOGIC, "Pédagogique"),
        (CATEGORY_PREFERENCE, "Préférence"),
        (CATEGORY_HISTORY, "Historique"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ai_memories", on_delete=models.CASCADE)
    agent = models.ForeignKey(AIAgent, on_delete=models.CASCADE)
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES, default=CATEGORY_PEDAGOGIC)
    key = models.CharField(max_length=120)
    value = models.JSONField(default=dict)

    class Meta:
        unique_together = ["user", "agent", "category", "key"]

    def __str__(self):
        return f"{self.user} / {self.agent} / {self.key}"


class AIContext(TimeStampedModel):
    """Knowledge base (RAG source) attached to a course."""

    course = models.ForeignKey("courses.Course", related_name="ai_contexts", on_delete=models.CASCADE)
    source = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return f"{self.course} ← {self.source}"


class Recommendation(TimeStampedModel):
    """A suggestion produced by the adaptive engine / recommender agent."""

    REASON_ADAPTIVE = "adaptive"
    REASON_SKILL = "skill"
    REASON_GOAL = "goal"
    REASON_NEXT = "next_step"

    REASON_CHOICES = [
        (REASON_ADAPTIVE, "Adaptatif"),
        (REASON_SKILL, "Compétence"),
        (REASON_GOAL, "Objectif"),
        (REASON_NEXT, "Étape suivante"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="recommendations", on_delete=models.CASCADE)
    course = models.ForeignKey("courses.Course", related_name="recommendations", on_delete=models.CASCADE)
    reason = models.CharField(max_length=32, choices=REASON_CHOICES, default=REASON_NEXT)
    score = models.FloatField(default=0.5)
    rationale = models.TextField(blank=True)
    is_dismissed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-score"]

    def __str__(self):
        return f"{self.user} → {self.course}"