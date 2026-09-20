from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminOrOwner, IsAdminUser
from apps.courses.models import Course, Lesson

from . import services
from .models import AIAgent, AISession, Recommendation
from .serializers import (
    AIAgentAdminSerializer,
    AIAgentSerializer,
    AISessionSerializer,
    ChatPromptSerializer,
    RecommendationSerializer,
)


class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    """Public catalogue of active agents (read-only for learners)."""

    queryset = AIAgent.objects.filter(is_active=True)
    serializer_class = AIAgentSerializer
    permission_classes = [AllowAny]


class AgentAdminViewSet(viewsets.ModelViewSet):
    """Full CRUD to customise agent personas and their roles (admin only)."""

    queryset = AIAgent.objects.all()
    serializer_class = AIAgentAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        if not self.request.user.is_admin():
            return AIAgent.objects.none()
        return AIAgent.objects.prefetch_related("courses")


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = AISessionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = AISession.objects.select_related("agent", "course", "lesson", "user").prefetch_related("messages")
        return qs if self.request.user.is_admin() else qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"])
    def ask(self, request):
        """Send a message to the AI — the orchestrator selects agent + context."""
        serializer = ChatPromptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = None
        if serializer.validated_data.get("course_id"):
            course = Course.objects.filter(
                id=serializer.validated_data["course_id"],
                status=Course.STATUS_PUBLISHED,
            ).first()

        lesson = None
        if serializer.validated_data.get("lesson_id"):
            lesson = Lesson.objects.filter(
                id=serializer.validated_data["lesson_id"]
            ).first()

        initial_agent = None
        if serializer.validated_data.get("agent_id"):
            initial_agent = AIAgent.objects.filter(
                id=serializer.validated_data["agent_id"], is_active=True
            ).first()

        session = None
        if course:
            session = AISession.objects.filter(
                user=request.user, course=course, status=AISession.STATUS_OPEN
            ).order_by("-updated_at").first()

        orchestrator = services.AIOrchestrator(request.user, session)
        orchestrator.session, answer = orchestrator.reply(
            serializer.validated_data["content"],
            agent=initial_agent,
            course=course,
            lesson=lesson,
        )

        session_serializer = AISessionSerializer(orchestrator.session)
        return Response(
            {"session": session_serializer.data, "answer": answer},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        session = self.get_object()
        session.status = AISession.STATUS_CLOSED
        session.save(update_fields=["status", "updated_at"])
        return Response(AISessionSerializer(session).data)


class RecommendationViewSet(viewsets.ModelViewSet):
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = Recommendation.objects.select_related("user", "course")
        return qs if self.request.user.is_admin() else qs.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def refresh(self, request):
        """(Re)run the adaptive engine for the current learner."""
        recommendations = services.run_recommendations(request.user)
        return Response(RecommendationSerializer(recommendations, many=True).data)

    @action(detail=True, methods=["post"])
    def dismiss(self, request, pk=None):
        rec = self.get_object()
        rec.is_dismissed = True
        rec.save(update_fields=["is_dismissed", "updated_at"])
        return Response(RecommendationSerializer(rec).data)