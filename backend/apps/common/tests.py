"""Factories and helpers shared by every ORBITE test module."""
from django.contrib.auth import get_user_model

from apps.ai.models import AIAgent
from apps.assessments.models import Exercise, Question, Quiz
from apps.courses.models import Category, Course, Lesson, Module, Video

User = get_user_model()


def make_user(username, role="student", email=None, password="TestPass123!"):
    user = User.objects.create_user(
        username=username,
        email=email or f"{username}@orbite.test",
        password=password,
        first_name=username.capitalize(),
        last_name="Test",
    )
    user.role = role
    user.save(update_fields=["role"])
    return user


def make_course(
    instructor=None,
    status=Course.STATUS_PUBLISHED,
    title="Django pour tous",
    price=15000,
    with_modules=True,
    ai_mentor=None,
):
    category = Category.objects.get_or_create(
        name="Développement", slug="developpement"
    )[0]
    course = Course.objects.create(
        title=title,
        slug=title.lower().replace(" ", "-"),
        category=category,
        instructor=instructor,
        ai_mentor=ai_mentor,
        level=Course.LEVEL_BEGINNER,
        price=price,
        is_free=price == 0,
        status=status,
    )
    if with_modules:
        module = Module.objects.create(course=course, title=f"Module {title}", order=1)
        video = Video.objects.create(
            title="Vidéo test", duration_seconds=300, storage_key="test.mp4"
        )
        lesson = Lesson.objects.create(
            module=module,
            title="Leçon 1",
            summary="Résumé",
            content="Contenu",
            video_meta=video,
            order=1,
            estimated_minutes=5,
        )
        quiz = Quiz.objects.create(lesson=lesson, title=f"Quiz {title}", pass_score=50)
        for i, qdata in enumerate(
            [
                {
                    "question_type": "mcq",
                    "text": "2+2 ?",
                    "options": ["3", "4", "5"],
                    "correct": ["4"],
                    "points": 1,
                },
                {
                    "question_type": "mcq",
                    "text": "Capital du Mali ?",
                    "options": ["Bamako", "Dakar", "Ouaga"],
                    "correct": ["Bamako"],
                    "points": 1,
                },
            ]
        ):
            Question.objects.create(quiz=quiz, **qdata)
        Exercise.objects.create(
            lesson=lesson,
            title=f"Exercice {title}",
            instructions="Fais un mini cas pratique.",
        )
    return course


def make_agent(code="kodex", name="KODEX"):
    return AIAgent.objects.create(
        code=code, name=name, specialty="Développement", system_prompt="Système test."
    )