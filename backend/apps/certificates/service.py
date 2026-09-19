"""Certificate service. Issue is eligibility-checked and never client-side."""

import uuid

from .models import Certificate


class CertificateService:
    @staticmethod
    def is_eligible(enrollment):
        course = enrollment.course
        if not course.certification_enabled:
            return False, "La certification n'est pas activée pour cette formation."
        if enrollment.progress < course.min_completion_rate:
            return False, "Le taux de complétion minimum n'est pas atteint."
        # Quiz / assessment minimum is checked by the assessments layer; here we
        # keep the rule explicit and verifiable.
        return True, ""

    @staticmethod
    def issue_if_eligible(enrollment):
        eligible, message = CertificateService.is_eligible(enrollment)
        if not eligible:
            return None
        certificate, created = Certificate.objects.get_or_create(
            user=enrollment.user,
            course=enrollment.course,
            defaults={
                "conditions_met": {
                    "completion_rate": enrollment.progress,
                    "min_completion_rate": enrollment.course.min_completion_rate,
                },
                "qr_token": uuid.uuid4().hex,
            },
        )
        return certificate