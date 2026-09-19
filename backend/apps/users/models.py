from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import TimeStampedModel


class Role(models.Model):
    """Access level on the platform (student, instructor, admin, super_admin)."""

    code = models.SlugField(unique=True)
    label = models.CharField(max_length=64)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.label


class User(AbstractUser):
    """Custom user. Django remains the single source of truth for auth."""

    ROLE_STUDENT = "student"
    ROLE_INSTRUCTOR = "instructor"
    ROLE_ADMIN = "admin"
    ROLE_SUPER_ADMIN = "super_admin"

    ROLE_CHOICES = [
        (ROLE_STUDENT, "Apprenant"),
        (ROLE_INSTRUCTOR, "Formateur"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_SUPER_ADMIN, "Super Admin"),
    ]

    role = models.CharField(
        max_length=24, choices=ROLE_CHOICES, default=ROLE_STUDENT, db_index=True
    )
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True, default="")
    phone = models.CharField(max_length=32, blank=True)
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveSmallIntegerField(default=1)

    def has_role(self, *codes):
        self_role = self.role if self.is_superuser else self.role
        return self_role in codes

    def is_admin(self):
        return self.has_role(self.ROLE_ADMIN, self.ROLE_SUPER_ADMIN) or self.is_superuser

    def is_super_admin(self):
        return self.has_role(self.ROLE_SUPER_ADMIN) or self.is_superuser

    def is_instructor(self):
        return self.has_role(self.ROLE_INSTRUCTOR) or self.is_admin()

    def add_xp(self, amount):
        self.xp = self.xp + amount
        while self.xp >= self.level * 1000:
            self.xp -= self.level * 1000
            self.level += 1
        self.save(update_fields=["xp", "level"])

    @property
    def full_name(self):
        return (self.first_name + " " + self.last_name).strip() or self.username

    def __str__(self):
        return self.username


class Profile(TimeStampedModel):
    """Pedagogical and personal profile of a user."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    language = models.CharField(max_length=8, default="fr")
    timezone = models.CharField(max_length=64, default="Africa/Bamako")
    theme = models.CharField(max_length=16, default="dark")
    learning_preferences = models.JSONField(default=dict, blank=True)
    notification_preferences = models.JSONField(default=dict, blank=True)
    ai_preferences = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Profil de {self.user.username}"


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def ensure_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)