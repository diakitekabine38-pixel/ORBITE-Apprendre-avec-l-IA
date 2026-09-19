from django.contrib import admin

from .models import Certificate, CertificateVerification


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("certificate_id", "user", "course", "issued_at")


@admin.register(CertificateVerification)
class CertificateVerificationAdmin(admin.ModelAdmin):
    list_display = ("certificate", "verified_at", "ip_address")