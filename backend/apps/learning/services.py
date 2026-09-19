"""ORBITE Learning Engine.

The adaptive engine is a separate component (not a chatbot). It consumes the
learner profile (progress, scores, skills, history) and produces a concrete,
immediate pedagogical action recommendation.
"""
from django.utils import timezone

from apps.ai.models import Recommendation

from .models import LessonProgress

XP_LESSON = 20
XP_QUIZ = 50
XP_EXERCISE = 80
XP_COURSE = 500


class LearningEngine:
    """Encapsulates the learning side-effects around the learner's actions."""

    def __init__(self, user):
        self.user = user

    def complete_lesson(self, enrollment, lesson, seconds_watched=0):
        lp, created = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
        lp.status = LessonProgress.STATUS_COMPLETED
        lp.progress_percent = 100
        lp.seconds_watched = seconds_watched or lp.seconds_watched
        lp.completed_at = timezone.now()
        lp.save()
        self.user.add_xp(XP_LESSON)
        enrollment.last_lesson = lesson
        enrollment.save(update_fields=["last_lesson", "updated_at"])
        enrollment.recompute_progress()
        if enrollment.completed:
            from apps.certificates.service import CertificateService

            CertificateService.issue_if_eligible(enrollment)
            self.user.add_xp(XP_COURSE)
        return lp


def update_watch(enrollment, lesson, seconds, position):
    lp, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    lp.seconds_watched = seconds
    lp.last_position = position
    if lp.status == LessonProgress.STATUS_NOT_STARTED:
        lp.status = LessonProgress.STATUS_IN_PROGRESS
    if seconds >= max(1, lesson.estimated_minutes * 60) * 0.8:
        lp.status = LessonProgress.STATUS_COMPLETED
        lp.completed_at = timezone.now()
        lp.progress_percent = 100
    lp.save()
    return lp


def recommend_next_action(user, limit=3):
    """Recommend the next pedagogical action from structured signals (not LLM).

    Falls back to the in-progress course with the highest progress so the
    learner always has a clear "what next" answer on the dashboard.
    """
    from .models import Enrollment

    enrollments = Enrollment.objects.filter(user=user, completed=False).order_by("-progress")
    recommendations = []
    for enrollment in enrollments:
        course = enrollment.course
        done_ids = enrollment.progress_items.filter(
            status=LessonProgress.STATUS_COMPLETED
        ).values_list("lesson_id", flat=True)
        next_lesson = (
            course.modules.prefetch_related("lessons")
            .values_list("lessons", flat=True)
        )
        remaining = [lid for lid in next_lesson if lid not in done_ids]
        if remaining:
            # First organized lesson not yet completed.
            from apps.courses.models import Lesson

            lesson = Lesson.objects.filter(module__course=course).exclude(pk__in=done_ids).order_by("module__order", "order").first()
            if lesson:
                recommendations.append(
                    Recommendation(
                        user=user,
                        course=course,
                        reason=Recommendation.REASON_ADAPTIVE,
                        score=1.0,
                        rationale=(
                            f"Reprends la leçon « {lesson.title} » de la formation "
                            f"« {course.title} » — tu es à {int(enrollment.progress)}%."
                        ),
                    )
                )
                if len(recommendations) >= limit:
                    break
    return recommendations