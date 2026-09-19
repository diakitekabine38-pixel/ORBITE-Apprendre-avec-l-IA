import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse

from apps.common.models import TimeStampedModel


def generate_certificate_id():
    """ORB-2026-X92K style identifiers."""
    prefix = getattr(settings, "CERTIFICATE_PREFIX", "ORB")
    year = "2026"
    token = uuid.uuid4().hex[:4].upper()
    return f"{prefix}-{year}-{token}"


class Certificate(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="certificates", on_delete=models.CASCADE)
    course = models.ForeignKey(
        "courses.Course", related_name="certificates", on_delete=models.CASCADE
    )
    certificate_id = models.CharField(max_length=32, unique=True, default=generate_certificate_id)
    issued_at = models.DateTimeField(auto_now_add=True)
    conditions_met = models.JSONField(default=dict, blank=True)
    qr_token = models.CharField(max_length=64, blank=True)
    pdf_key = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ["user", "course"]

    def __str__(self):
        return f"{self.certificate_id} — {self.user}"


class CertificateVerification(TimeStampedModel):
    certificate = models.ForeignKey(
        Certificate, related_name="verifications", on_delete=models.CASCADE
    )
    verified_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.certificate.certificate_id} @ {self.verified_at}"