from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.ai.models import AIAgent
from apps.common.permissions import IsAdminOrInstructorOwner, IsAdminUser, IsInstructor, IsOwnerOrReadOnly

from .models import Category, Course, Lesson, Module, Review, Video
from .serializers import (
    CategorySerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseWriteSerializer,
    LessonBriefSerializer,
    LessonDetailSerializer,
    ModuleSerializer,
    ReviewSerializer,
    VideoSerializer,
)


CAN_PUBLISH = [Course.STATUS_APPROVED, Course.STATUS_PUBLISHED]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return Category.objects.filter(is_active=True).annotate(
            published_courses=Count(
                "courses", filter=Q(courses__status=Course.STATUS_PUBLISHED)
            )
        ).order_by("name")


class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CourseWriteSerializer
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseListSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_admin():
            qs = Course.objects.all()
        elif user.is_authenticated and user.is_instructor():
            qs = Course.objects.filter(Q(instructor=user) | Q(status=Course.STATUS_PUBLISHED))
        else:
            qs = Course.objects.filter(status=Course.STATUS_PUBLISHED)
        return (
            qs.select_related("category", "instructor", "ai_mentor")
            .prefetch_related("modules__lessons")
            .order_by("-created_at")
        )

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsInstructor()]
        if self.action in ("submit", "submit_to_review", "start_review", "approve", "publish", "unpublish"):
            return [IsAdminOrInstructorOwner()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    # ---- Workflow de publication : brouillon → soumis → en révision → approuvé → publié

    @action(detail=True, methods=["post"])
    def submit(self, request, slug=None):
        """Instructor requests validation (draft → submitted)."""
        course = self.get_object()
        if course.instructor != request.user and not request.user.is_admin():
            return Response({"detail": "Vous n'êtes pas le formateur de cette formation."}, status=403)
        if course.status != Course.STATUS_DRAFT:
            return Response({"detail": "Seul un brouillon peut être soumis."}, status=400)
        course.status = Course.STATUS_SUBMITTED
        course.save(update_fields=["status"])
        return Response({"detail": "Formation soumise à validation.", "status": course.status})

    @action(detail=True, methods=["post"])
    def start_review(self, request, slug=None):
        """Admin takes the course into review (submitted → in_review)."""
        course = self.get_object()
        if not request.user.is_admin():
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        if course.status != Course.STATUS_SUBMITTED:
            return Response({"detail": "La formation doit être soumise."}, status=400)
        course.status = Course.STATUS_IN_REVIEW
        course.save(update_fields=["status"])
        return Response({"detail": "Formation en révision.", "status": course.status})

    @action(detail=True, methods=["post"])
    def approve(self, request, slug=None):
        """Admin validates the content (in_review → approved)."""
        course = self.get_object()
        if not request.user.is_admin():
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        if course.status != Course.STATUS_IN_REVIEW:
            return Response({"detail": "La formation doit être en révision."}, status=400)
        course.status = Course.STATUS_APPROVED
        course.save(update_fields=["status"])
        return Response({"detail": "Formation approuvée.", "status": course.status})

    @action(detail=True, methods=["post"])
    def publish(self, request, slug=None):
        """Only an admin / super admin can publish a course (business rule)."""
        course = self.get_object()
        if not request.user.is_admin():
            return Response(
                {"detail": "Seul un administrateur peut publier une formation."}, status=403
            )
        if course.status != Course.STATUS_APPROVED:
            return Response({"detail": "La formation doit être approuvée avant publication."}, status=400)
        course.status = Course.STATUS_PUBLISHED
        course.save(update_fields=["status"])
        return Response({"detail": "Formation publiée.", "status": course.status})

    @action(detail=True, methods=["post"])
    def unpublish(self, request, slug=None):
        course = self.get_object()
        if not request.user.is_admin():
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        if course.status == Course.STATUS_PUBLISHED:
            course.status = Course.STATUS_APPROVED
            course.save(update_fields=["status"])
        return Response({"detail": "Formation dépubliée.", "status": course.status})


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Module.objects.filter(course__status=Course.STATUS_PUBLISHED)


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_serializer_class(self):
        return LessonDetailSerializer if self.action == "retrieve" else LessonBriefSerializer

    def get_queryset(self):
        """Computed values are safe to expose; sensitive data stays server-side."""
        course_slug = self.request.query_params.get("course")
        qs = Lesson.objects.select_related("video_meta").prefetch_related("resources")
        if course_slug:
            qs = qs.filter(module__course__slug=course_slug)
        return qs

    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        qs = self.get_queryset()
        user = request.user

        enrolled = (
            user.is_authenticated
            and lesson.module.course.enrollments.filter(user=user).exists()
        )
        if lesson.is_free_preview or enrolled or user.is_instructor():
            serializer = LessonDetailSerializer(lesson, context={"request": request})
            return Response(serializer.data)
        # Non-enrolled visitors get a pedagogical summary, never the protected video.
        return Response(
            {
                "id": lesson.id,
                "title": lesson.title,
                "summary": lesson.summary,
                "order": lesson.order,
                "locked": True,
            }
        )


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VideoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Video.objects.all()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Review.objects.select_related("user")
        if self.action == "list":
            qs = qs.filter(status=Review.STATUS_APPROVED)
        elif self.request.user.is_admin():
            return qs
        else:
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        # Only enrolled learners may review a course.
        user = self.request.user
        course = serializer.validated_data["course"]
        if course.enrollments.filter(user=user).exists():
            serializer.save(user=user)
        else:
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                {"detail": "Seuls les apprenants inscrits peuvent laisser un avis."}
            )