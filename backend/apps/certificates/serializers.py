from rest_framework import serializers

from .models import Certificate, CertificateVerification


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Certificate
        fields = [
            "id",
            "certificate_id",
            "course",
            "course_title",
            "user_name",
            "issued_at",
            "conditions_met",
            "qr_token",
            "pdf_key",
        ]
        read_only_fields = fields


class CertificateVerificationSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="certificate.course.title", read_only=True)
    user_name = serializers.CharField(source="certificate.user.full_name", read_only=True)
    issued_at = serializers.DateTimeField(source="certificate.issued_at", read_only=True)

    class Meta:
        model = CertificateVerification
        fields = ["id", "certificate_id", "course_title", "user_name", "issued_at", "verified_at"]
        read_only_fields = fields