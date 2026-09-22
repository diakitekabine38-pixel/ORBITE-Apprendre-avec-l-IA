"""ORBITE Learning Engine.

The adaptive engine is a separate component (not a chatbot). It consumes the
learner profile (progress, scores, skills, history) and produces a concrete,
immediate pedagogical action recommendation.
"""
from django.utils import timezone

from apps.ai.models import Recommendation

from .models import Enrollment, LessonProgress

from apps.courses.models import Course

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


# === Orbite personnelle — cartographie visuelle des compétences ===

ORBITE_RINGS = [
    {"tier": 1, "radius": 285, "name": "Émergence", "subtitle": "Premiers pas sur votre trajectoire"},
    {"tier": 2, "radius": 205, "name": "Orbite stable", "subtitle": "Compétences en pleine assimilation"},
    {"tier": 3, "radius": 125, "name": "Pleine gravité", "subtitle": "Maîtrisées et en rotation autour de vous"},
]


def _skill_from_enrollment(enrollment):
    course = enrollment.course
    mastery = round(enrollment.progress)
    return {
        "id": course.id,
        "slug": course.slug,
        "name": course.title,
        "mastery_score": mastery,
        "level": min(5, 1 + mastery // 20),
        "xp": mastery,
        "color": (course.ai_mentor.color if course.ai_mentor and course.ai_mentor.color else "#7C5CFF"),
        "description": course.short_description or course.description[:200] or "",
    }


def build_orbite(user):
    """Trajectoire orbitale de l'apprenant → contrat du OrbitalCanvas."""
    enrollments = list(
        Enrollment.objects.filter(user=user)
        .select_related("course", "course__ai_mentor", "course__category")
    )
    for e in enrollments:
        e.recompute_progress()

    skills = [_skill_from_enrollment(e) for e in enrollments]
    for skill in skills:
        for ring in ORBITE_RINGS:
            if skill["mastery_score"] < 35 and ring["tier"] == 1:
                skill["ringTier"] = 1
                break
            if 35 <= skill["mastery_score"] < 70 and ring["tier"] == 2:
                skill["ringTier"] = 2
                break
            if skill["mastery_score"] >= 70 and ring["tier"] == 3:
                skill["ringTier"] = 3
                break

    rings = []
    for ring in ORBITE_RINGS:
        rings.append(
            {
                "tier": ring["tier"],
                "radius": ring["radius"],
                "name": ring["name"],
                "subtitle": ring["subtitle"],
                "skills": [s for s in skills if s["ringTier"] == ring["tier"]],
            }
        )

    profile = user.profile
    learner = {
        "full_name": user.get_full_name() or user.username,
        "gravitational_index": round(sum(s["mastery_score"] for s in skills) / len(skills)) if skills else 0,
        "xp": user.xp,
        "level": user.level,
        "streak_days": profile.ai_preferences.get("streak_days", 0),
        "active_skills_count": len(skills),
    }

    recommendation = None
    if enrollments:
        weakest = min(skills, key=lambda s: s["mastery_score"])
        recommendation = {
            "title": f"Prochaine accélération : {weakest['name']}",
            "reason": (
                f"Vous êtes à {weakest['mastery_score']}% de maîtrise sur cette compétence. "
                "Reprendre ce parcours est le levier le plus rapide pour augmenter votre gravité orbitale."
            ),
            "action_label": "Reprendre le parcours",
        }
    else:
        starter = Course.published_objects.order_by("-is_free", "-created_at").first()
        if starter:
            recommendation = {
                "title": "Lancez votre première orbite",
                "reason": (
                    f"Commencez par « {starter.title} » : votre gravité orbitale se mettra à "
                    "tourner dès le premier module terminé."
                ),
                "action_label": "Découvrir les formations",
            }

    return {"learner": learner, "orbital_rings": rings, "recommendation": recommendation}