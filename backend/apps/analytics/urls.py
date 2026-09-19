from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("events", views.EventViewSet, basename="analytics-event")
router.register("stats", views.DashboardStatsViewSet, basename="analytics-stats")

urlpatterns = router.urls