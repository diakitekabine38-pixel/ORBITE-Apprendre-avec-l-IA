from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminUser, IsAdminOrOwner

from . import services
from .models import Attempt, Exercise, Quiz, Submission
from .serializers import (
    AttemptCreateSerializer,
    AttemptSerializer,
    ExerciseSerializer,
    QuizSerializer,
    SubmissionSerializer,
)


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Quiz.objects.filter(is_published=True).select_related("lesson__module__course")
        course = self.request.query_params.get("course")
        if course:
            qs = qs.filter(lesson__module__course__slug=course)
        return qs


class AttemptViewSet(viewsets.ModelViewSet):
    serializer_class = AttemptSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = Attempt.objects.select_related("user", "quiz")
        return qs if self.request.user.is_admin() else qs.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def submit(self, request):
        """Server-side grading of a quiz attempt."""
        serializer = AttemptCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz = serializer.validated_data["quiz"]

        # Attempt guard: only enrolled learners sitting a published quiz.
        from apps.learning.models import Enrollment

        if not Enrollment.objects.filter(user=request.user, course=quiz.lesson.module.course).exists():
            return Response(
                {"detail": "Vous devez être inscrit(e) à la formation pour passer ce quiz."},
                status=status.HTTP_403_FORBIDDEN,
            )

        previous = Attempt.objects.filter(quiz=quiz, user=request.user).count()
        if previous >= quiz.max_attempts:
            return Response(
                {"detail": "Nombre maximal de tentatives atteint pour ce quiz."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        attempt, detail = services.grade_attempt(
            request.user,
            quiz,
            serializer.validated_data["answers"],
            serializer.validated_data.get("time_spent_seconds", 0),
        )
        return Response(
            {
                **AttemptSerializer(attempt).data,
                "detail": detail,
            },
            status=status.HTTP_201_CREATED,
        )


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ExerciseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Exercise.objects.select_related("lesson__module__course").all()


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = Submission.objects.select_related("user", "exercise")
        return qs if self.request.user.is_admin() else qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def evaluate(self, request, pk=None):
        """AI evaluation (module 10) — the AI proposes, the human validates."""
        submission = self.get_object()
        return Response(
            {"detail": "L'évaluation IA sera produite par l'orchestrateur IA."}
        )