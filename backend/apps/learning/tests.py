from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.tests import make_course, make_user
from apps.learning.models import Enrollment, LessonProgress
from apps.learning import services
from apps.learning.services import LearningEngine, XP_COURSE, XP_LESSON


class ProgressEngineTests(TestCase):
    def setUp(self):
        self.student = make_user("progresseur")
        self.instructor = make_user("prof", role="instructor")
        self.course = make_course(instructor=self.instructor, price=0)
        self.enrollment = Enrollment.objects.create(user=self.student, course=self.course)

    def test_completing_lessons_advances_progress_and_xp(self):
        module = self.course.modules.first()
        lesson = module.lessons.first()
        start_xp = self.student.xp

        LearningEngine(self.student).complete_lesson(self.enrollment, lesson)

        self.student.refresh_from_db()
        # Completing the only lesson also completes the course → XP leçon + XP formation.
        self.assertEqual(self.student.xp, start_xp + XP_LESSON + XP_COURSE)
        self.enrollment.refresh_from_db()
        self.assertTrue(self.enrollment.progress >= 100)  # single-lesson module

    def test_course_completion_generates_certificate(self):
        module = self.course.modules.first()
        for lesson in module.lessons.all():
            LearningEngine(self.student).complete_lesson(self.enrollment, lesson)
        self.enrollment.refresh_from_db()
        self.assertTrue(self.enrollment.completed)
        self.assertTrue(self.student.certificates.filter(course=self.course).exists())


class EnrollmentApiTests(APITestCase):
    def setUp(self):
        self.student = make_user("apprenant")
        self.instructor = make_user("prof", role="instructor")

    def test_enroll_free_course(self):
        course = make_course(instructor=self.instructor, price=0, title="Gratuite")
        self.client.force_authenticate(self.student)
        response = self.client.post(
            "/api/v1/learning/enrollments/enroll/", {"slug": course.slug}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Enrollment.objects.filter(user=self.student, course=course).exists())

    def test_enroll_paid_course_requires_payment(self):
        course = make_course(instructor=self.instructor, price=8000, title="Payante")
        self.client.force_authenticate(self.student)
        response = self.client.post(
            "/api/v1/learning/enrollments/enroll/", {"slug": course.slug}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

    def test_dashboard_vue(self):
        course = make_course(instructor=self.instructor, price=0, title="Ma formation")
        Enrollment.objects.create(user=self.student, course=course)
        self.client.force_authenticate(self.student)
        response = self.client.get("/api/v1/learning/enrollments/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["enrollments"]), 1)

    def test_isolation_between_students(self):
        other = make_user("autre")
        course = make_course(instructor=self.instructor, price=0, title="Privée")
        Enrollment.objects.create(user=self.student, course=course)
        self.client.force_authenticate(other)
        response = self.client.get("/api/v1/learning/enrollments/")
        self.assertEqual(response.data["count"], 0)


class SkillTests(TestCase):
    def test_userskill_unique_per_user(self):
        from apps.learning.models import Skill, UserSkill

        student = make_user("skil")
        skill = Skill.objects.create(name="Python", slug="python")
        for _ in range(2):
            UserSkill.objects.get_or_create(user=student, skill=skill, defaults={"mastery_score": 50})
        self.assertEqual(UserSkill.objects.filter(user=student, skill=skill).count(), 1)