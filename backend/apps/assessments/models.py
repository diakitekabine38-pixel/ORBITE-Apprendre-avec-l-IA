from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel


class Quiz(TimeStampedModel):
    """Assessment grouped by a lesson, can be quiz / exercise / project / final."""

    TYPE_QUIZ = "quiz"
    TYPE_PROJECT = "project"
    TYPE_FINAL = "final_assessment"
    TYPE_MINI = "mini_assessment"

    TYPE_CHOICES = [
        (TYPE_QUIZ, "Quiz"),
        (TYPE_MINI, "Mini-évaluation"),
        (TYPE_PROJECT, "Projet"),
        (TYPE_FINAL, "Évaluation finale"),
    ]

    lesson = models.ForeignKey(
        "courses.Lesson", related_name="quizzes", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    quiz_type = models.CharField(max_length=24, choices=TYPE_CHOICES, default=TYPE_QUIZ)
    pass_score = models.PositiveSmallIntegerField(default=60, help_text="Score minimum (0-100)")
    max_attempts = models.PositiveSmallIntegerField(default=3)
    instructions = models.TextField(blank=True)
    time_limit_minutes = models.PositiveSmallIntegerField(default=15)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def total_points(self):
        return self.questions.aggregate(t=models.Sum("points"))["t"] or 0


class Question(TimeStampedModel):
    TYPE_MCQ = "mcq"
    TYPE_TRUE_FALSE = "true_false"
    TYPE_MULTIPLE = "multiple"
    TYPE_OPEN = "open"
    TYPE_ASSOCIATION = "association"
    TYPE_ORDERING = "ordering"

    TYPE_CHOICES = [
        (TYPE_MCQ, "Choix multiple"),
        (TYPE_TRUE_FALSE, "Vrai / Faux"),
        (TYPE_MULTIPLE, "Réponses multiples"),
        (TYPE_OPEN, "Question ouverte"),
        (TYPE_ASSOCIATION, "Association"),
        (TYPE_ORDERING, "Classement"),
    ]

    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    question_type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    text = models.TextField()
    options = models.JSONField(default=list, blank=True)
    correct = models.JSONField(default=list, blank=True)
    points = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.text[:80]


class Attempt(TimeStampedModel):
    quiz = models.ForeignKey(Quiz, related_name="attempts", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="quiz_attempts", on_delete=models.CASCADE)
    answers = models.JSONField(default=list)
    score = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} — {self.quiz} ({self.score}%)"


class Exercise(TimeStampedModel):
    TYPE_TEXT = "text"
    TYPE_STRATEGY = "strategy"
    TYPE_CREATIVE = "creative"
    TYPE_CODE = "code"
    TYPE_BUSINESS = "business_plan"

    TYPE_CHOICES = [
        (TYPE_TEXT, "Réponse textuelle"),
        (TYPE_STRATEGY, "Stratégie"),
        (TYPE_CREATIVE, "Travail visuel"),
        (TYPE_CODE, "Code"),
        (TYPE_BUSINESS, "Business plan"),
    ]

    lesson = models.ForeignKey(
        "courses.Lesson", related_name="exercises", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    exercise_type = models.CharField(max_length=24, choices=TYPE_CHOICES, default=TYPE_TEXT)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Submission(TimeStampedModel):
    STATUS_SUBMITTED = "submitted"
    STATUS_CHECKED_AI = "checked_ai"
    STATUS_VALIDATED = "validated"

    STATUS_CHOICES = [
        (STATUS_SUBMITTED, "Soumise"),
        (STATUS_CHECKED_AI, "Corrigée (IA)"),
        (STATUS_VALIDATED, "Validée (humain)"),
    ]

    exercise = models.ForeignKey(Exercise, related_name="submissions", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="submissions", on_delete=models.CASCADE)
    content = models.TextField()
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    ai_score = models.JSONField(default=dict, blank=True)
    human_validated = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} — {self.exercise}"