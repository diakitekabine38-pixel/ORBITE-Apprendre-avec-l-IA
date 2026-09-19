from django.urls import path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("verify", views.VerifyViewSet, basename="certificate-verify")
router.register("", views.CertificateViewSet, basename="certificate")

urlpatterns = router.urls