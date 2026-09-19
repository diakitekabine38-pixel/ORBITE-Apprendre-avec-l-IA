from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

from apps.common.models import TimeStampedModel


class Enrollment(TimeStampedModel):
    """Access to a course and global progress (progress = mean of module progress)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="enrollments", on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        "courses.Course", related_name="enrollments", on_delete=models.CASCADE
    )
    progress = models.FloatField(default=0.0)
    last_lesson = models.ForeignKey(
        "courses.Lesson", on_delete=models.SET_NULL, null=True, blank=True
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["user", "course"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} → {self.course}"

    def recompute_progress(self):
        """Module progress = ratio completed lessons; course progress = mean."""
        modules = self.course.modules.prefetch_related("lessons")
        module_progress = []
        for module in modules:
            lessons = list(module.lessons.all())
            if not lessons:
                module_progress.append(1.0)
                continue
            done = sum(
                1
                for lp in self.progress_items.filter(
                    lesson__module=module, status=LessonProgress.STATUS_COMPLETED
                )
            )
            module_progress.append(done / len(lessons))
        if not module_progress:
            return 0.0
        total = round(sum(module_progress) / len(module_progress) * 100, 1)
        self.progress = total
        self.completed = total >= 100.0
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        self.save(update_fields=["progress", "completed", "completed_at", "updated_at"])
        return total


class LessonProgress(TimeStampedModel):
    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, "À faire"),
        (STATUS_IN_PROGRESS, "En cours"),
        (STATUS_COMPLETED, "Terminée"),
    ]

    enrollment = models.ForeignKey(
        Enrollment, related_name="progress_items", on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(
        "courses.Lesson", related_name="progress", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED)
    progress_percent = models.PositiveSmallIntegerField(default=0)
    seconds_watched = models.PositiveIntegerField(default=0)
    last_position = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["enrollment", "lesson"]
        ordering = ["lesson__order"]

    def __str__(self):
        return f"{self.enrollment.user} — {self.lesson.title} [{self.status}]"


class Skill(TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class UserSkill(TimeStampedModel):
    """Mastery of a skill by a user — the adaptive engine input."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="skills", on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, related_name="users", on_delete=models.CASCADE)
    mastery_score = models.PositiveSmallIntegerField(default=0)
    confidence = models.FloatField(default=0.5)
    last_assessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "skill"]

    def __str__(self):
        return f"{self.user} : {self.skill} = {self.mastery_score}%"


class Goal(TimeStampedModel):
    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_ARCHIVED = "archived"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_COMPLETED, "Atteinte"),
        (STATUS_ARCHIVED, "Archivée"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="goals", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    courses = models.ManyToManyField("courses.Course", related_name="goals", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user}: {self.title}"


class LearningPath(TimeStampedModel):
    """Multi-course path built around an objective (ex. Python → Django → API → React)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="learning_paths", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    courses = models.ManyToManyField(
        "courses.Course", related_name="learning_paths", blank=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user}: {self.title}"