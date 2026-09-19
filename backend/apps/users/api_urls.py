from django.urls import path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("profile", views.ProfileViewSet, basename="user-profile")
router.register("roles", views.RoleViewSet, basename="role")

urlpatterns = router.urls