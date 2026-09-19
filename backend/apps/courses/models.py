from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from apps.common.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=64, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CourseManager(models.Manager):
    def published(self):
        return self.get_queryset().filter(status=Course.STATUS_PUBLISHED)


class Course(TimeStampedModel):
    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_IN_REVIEW = "in_review"
    STATUS_APPROVED = "approved"
    STATUS_PUBLISHED = "published"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Brouillon"),
        (STATUS_SUBMITTED, "Soumis"),
        (STATUS_IN_REVIEW, "En révision"),
        (STATUS_APPROVED, "Approuvé"),
        (STATUS_PUBLISHED, "Publié"),
    ]

    LEVEL_BEGINNER = "beginner"
    LEVEL_INTERMEDIATE = "intermediate"
    LEVEL_ADVANCED = "advanced"

    LEVEL_CHOICES = [
        (LEVEL_BEGINNER, "Débutant"),
        (LEVEL_INTERMEDIATE, "Intermédiaire"),
        (LEVEL_ADVANCED, "Avancé"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    objectives = models.JSONField(default=list, blank=True)
    prerequisites = models.JSONField(default=list, blank=True)
    thumbnail = models.ImageField(upload_to="courses/thumbnails/", blank=True, null=True)
    promo_video_key = models.CharField(max_length=255, blank=True)

    category = models.ForeignKey(
        Category, related_name="courses", on_delete=models.SET_NULL, null=True
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="courses_taught",
        on_delete=models.CASCADE,
        limit_choices_to={"role__in": ["instructor", "admin", "super_admin"]},
    )
    ai_mentor = models.ForeignKey(
        "ai.AIAgent",
        related_name="courses",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    level = models.CharField(max_length=16, choices=LEVEL_CHOICES, default=LEVEL_BEGINNER)
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    duration_hours = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=24, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True
    )
    is_free = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    certification_enabled = models.BooleanField(default=True)
    min_completion_rate = models.PositiveSmallIntegerField(default=80)
    min_quiz_score = models.PositiveSmallIntegerField(default=60)

    objects = models.Manager()
    published_objects = CourseManager()

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def rating(self):
        ratings = self.reviews.filter(status=Review.STATUS_APPROVED).values_list("rating", flat=True)
        if not ratings:
            return 0.0
        return round(sum(ratings) / len(ratings), 1)

    @property
    def review_count(self):
        return self.reviews.filter(status=Review.STATUS_APPROVED).count()

    @property
    def student_count(self):
        return self.enrollments.count()

    def submission_workflow_progress(self):
        """Next status in the BROUILLON → SOUMIS → EN RÉVISION → APPROUVÉ → PUBLIÉ chain."""
        order = [
            self.STATUS_DRAFT,
            self.STATUS_SUBMITTED,
            self.STATUS_IN_REVIEW,
            self.STATUS_APPROVED,
            self.STATUS_PUBLISHED,
        ]
        return order


class Module(TimeStampedModel):
    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    ai_generated = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Video(TimeStampedModel):
    """Metadata only. Actual files live in the dedicated storage service."""

    title = models.CharField(max_length=200)
    duration_seconds = models.PositiveIntegerField(default=0)
    provider = models.CharField(max_length=32, default="s3")
    storage_key = models.CharField(max_length=255, blank=True)
    thumbnail_key = models.CharField(max_length=255, blank=True)
    hls_url = models.URLField(blank=True)
    is_free_preview = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Lesson(TimeStampedModel):
    module = models.ForeignKey(Module, related_name="lessons", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    video_meta = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_free_preview = models.BooleanField(default=False)
    estimated_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.module.title} → {self.title}"


class Resource(TimeStampedModel):
    TYPE_FILE = "file"
    TYPE_LINK = "link"
    TYPE_PDF = "pdf"

    TYPE_CHOICES = [
        (TYPE_FILE, "Fichier"),
        (TYPE_LINK, "Lien"),
        (TYPE_PDF, "PDF"),
    ]

    lesson = models.ForeignKey(Lesson, related_name="resources", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=16, choices=TYPE_CHOICES, default=TYPE_FILE)
    file_key = models.CharField(max_length=255, blank=True)
    url = models.URLField(blank=True)

    def __str__(self):
        return self.title


class Review(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_APPROVED, "Approuvé"),
        (STATUS_REJECTED, "Rejeté"),
    ]

    course = models.ForeignKey(Course, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reviews", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)

    class Meta:
        unique_together = ["course", "user"]

    def __str__(self):
        return f"{self.course.title} — {self.rating}★ par {self.user}"