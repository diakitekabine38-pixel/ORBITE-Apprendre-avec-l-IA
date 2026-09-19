from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model providing created_at / updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActiveQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class StatusModel(models.Model):
    status = models.CharField(
        max_length=32,
        default="active",
        choices=[],
        db_index=True,
    )

    class Meta:
        abstract = True