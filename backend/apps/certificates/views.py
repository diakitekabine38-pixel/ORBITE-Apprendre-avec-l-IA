from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminOrOwner

from .models import Certificate, CertificateVerification
from .serializers import CertificateSerializer, CertificateVerificationSerializer


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = Certificate.objects.select_related("course", "user")
        return qs if self.request.user.is_admin() else qs.filter(user=self.request.user)


class VerifyViewSet(viewsets.ViewSet):
    """Public certificate verification — no authentication required."""

    permission_classes = [AllowAny]

    def retrieve(self, request, pk=None):
        certificate = get_object_or_404(Certificate, certificate_id=pk)
        CertificateVerification.objects.create(
            certificate=certificate,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return Response(
            {
                "certificate_id": certificate.certificate_id,
                "course_title": certificate.course.title,
                "user_name": certificate.user.full_name,
                "issued_at": certificate.issued_at,
                "valid": True,
            }
        )