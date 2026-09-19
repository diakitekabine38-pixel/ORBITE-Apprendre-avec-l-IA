from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("agents", views.AgentViewSet, basename="ai-agent")
router.register("sessions", views.ChatViewSet, basename="ai-session")
router.register("recommendations", views.RecommendationViewSet, basename="recommendation")

urlpatterns = router.urls