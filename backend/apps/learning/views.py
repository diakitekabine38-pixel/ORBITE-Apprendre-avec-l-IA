from django.shortcuts import get_object_or_404
from django.db.models import Count, F

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminOrOwner
from apps.courses.models import Course

from . import services
from .models import Enrollment, Goal, LearningPath, LessonProgress, Skill, UserSkill
from .serializers import (
    EnrollmentSerializer,
    GoalSerializer,
    LearningPathSerializer,
    LessonProgressSerializer,
    SkillSerializer,
    UserSkillSerializer,
)


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        user = self.request.user
        qs = Enrollment.objects.select_related("course").order_by("-created_at")
        return qs if user.is_admin() else qs.filter(user=user)

    @action(detail=False, methods=["get"])
    def library(self, request):
        """Module 17 — Bibliothèque de l'apprenant (en cours / terminées)."""
        qs = self.get_queryset().filter(user=request.user).annotate(
            lesson_count=Count("course__modules__lessons")
        )
        return Response(EnrollmentSerializer(qs, many=True, context={"request": request}).data)

    @action(detail=False, methods=["post"])
    def enroll(self, request):
        """Enroll into a free course, or a paid course after payment."""
        course = get_object_or_404(
            Course, slug=request.data.get("slug"), status=Course.STATUS_PUBLISHED
        )
        if not course.is_free and course.price > 0:
            return Response(
                {"detail": "Cette formation est payante. Terminez le paiement d'abord."},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )
        enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
        return Response(
            EnrollmentSerializer(enrollment, context={"request": request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        """Module 18 — Vue centralisée de l'apprenant."""
        qs = Enrollment.objects.filter(user=request.user).select_related("course__category")
        data = {
            "enrollments": EnrollmentSerializer(qs, many=True, context={"request": request}).data,
            "streak_days": request.user.profile.ai_preferences.get("streak_days", 0),
            "xp": request.user.xp,
            "level": request.user.level,
            "goals": [g.title for g in Goal.objects.filter(user=request.user, status=Goal.STATUS_ACTIVE)],
        }
        return Response(data)


class LessonProgressViewSet(viewsets.ModelViewSet):
    serializer_class = LessonProgressSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = LessonProgress.objects.select_related("enrollment__user", "lesson")
        if self.request.user.is_admin():
            return qs
        return qs.filter(enrollment__user=self.request.user)

    @action(detail=False, methods=["post"])
    def start(self, request):
        enrollment = get_object_or_404(
            Enrollment, user=request.user, course__slug=request.data.get("course_slug")
        )
        from apps.courses.models import Lesson

        lesson = get_object_or_404(Lesson, pk=request.data.get("lesson_id"))
        lp, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
        if lp.status == LessonProgress.STATUS_NOT_STARTED:
            lp.status = LessonProgress.STATUS_IN_PROGRESS
            lp.save(update_fields=["status", "updated_at"])
        return Response(LessonProgressSerializer(lp).data)

    @action(detail=False, methods=["post"])
    def complete(self, request):
        enrollment = get_object_or_404(
            Enrollment, user=request.user, course__slug=request.data.get("course_slug")
        )
        from apps.courses.models import Lesson

        lesson = get_object_or_404(
            Lesson, pk=request.data.get("lesson_id"), module__course=enrollment.course
        )
        seconds = int(request.data.get("seconds", 0) or 0)
        services.LearningEngine(request.user).complete_lesson(enrollment, lesson, seconds)
        return Response(
            {"detail": "Leçon terminée ✓", "progress": enrollment.progress}
        )

    @action(detail=False, methods=["post"])
    def watch(self, request):
        enrollment = get_object_or_404(
            Enrollment, user=request.user, course__slug=request.data.get("course_slug")
        )
        from apps.courses.models import Lesson

        lesson = get_object_or_404(
            Lesson, pk=request.data.get("lesson_id"), module__course=enrollment.course
        )
        lp = services.update_watch(
            enrollment,
            lesson,
            int(request.data.get("seconds", 0) or 0),
            int(request.data.get("position", 0) or 0),
        )
        return Response(LessonProgressSerializer(lp).data)


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Skill.objects.all()


class UserSkillViewSet(viewsets.ModelViewSet):
    serializer_class = UserSkillSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = UserSkill.objects.select_related("skill", "user")
        return qs if self.request.user.is_admin() else qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = Goal.objects.filter()
        return qs.all() if self.request.user.is_admin() else qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LearningPathViewSet(viewsets.ModelViewSet):
    serializer_class = LearningPathSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = LearningPath.objects.prefetch_related("courses")
        return qs if self.request.user.is_admin() else qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)