from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.certificates.service import CertificateService
from apps.common.tests import make_course, make_user
from apps.learning.models import Enrollment
from apps.learning.services import LearningEngine


class CertificateEligibilityTests(TestCase):
    def setUp(self):
        self.student = make_user("certif")
        self.instructor = make_user("prof", role="instructor")
        self.course = make_course(instructor=self.instructor, price=0)
        self.enrollment = Enrollment.objects.create(user=self.student, course=self.course)

    def test_certificate_issued_after_completion(self):
        module = self.course.modules.first()
        for lesson in module.lessons.all():
            LearningEngine(self.student).complete_lesson(self.enrollment, lesson)
        self.enrollment.refresh_from_db()
        certificate = self.student.certificates.first()
        self.assertIsNotNone(certificate)
        self.assertTrue(certificate.certificate_id.startswith("ORB-"))

    def test_low_completion_blocks_certificate(self):
        from apps.courses.models import Lesson

        course = make_course(instructor=self.instructor, price=0, title="Exigeante", with_modules=True)
        course.min_completion_rate = 90
        course.save(update_fields=["min_completion_rate"])
        module = course.modules.first()
        # Add two more lessons so one completed → ~33% < 90%
        for i in range(2):
            Lesson.objects.create(module=module, title=f"Leçon bonus {i}", order=99 + i, estimated_minutes=5)
        enrollment = Enrollment.objects.create(user=self.student, course=course)
        first = module.lessons.first()
        LearningEngine(self.student).complete_lesson(enrollment, first)
        enrollment.refresh_from_db()
        self.assertLess(enrollment.progress, 90)
        self.assertFalse(self.student.certificates.filter(course=course).exists())

    def test_is_eligible_message(self):
        course = make_course(instructor=self.instructor, price=0, title="Sans cert")
        course.certification_enabled = False
        course.save(update_fields=["certification_enabled"])
        enrollment = Enrollment.objects.create(user=self.student, course=course)
        eligible, message = CertificateService.is_eligible(enrollment)
        self.assertFalse(eligible)
        self.assertIn("certification", message)


class VerificationApiTests(APITestCase):
    def setUp(self):
        self.student = make_user("verifyuser")
        self.instructor = make_user("prof", role="instructor")
        self.course = make_course(instructor=self.instructor, price=0)
        self.enrollment = Enrollment.objects.create(user=self.student, course=self.course)
        module = self.course.modules.first()
        for lesson in module.lessons.all():
            LearningEngine(self.student).complete_lesson(self.enrollment, lesson)
        self.certificate = self.student.certificates.first()

    def test_public_verification_no_auth(self):
        response = self.client.get(
            f"/api/v1/certificates/verify/{self.certificate.certificate_id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["valid"])

    def test_unknown_id_404(self):
        response = self.client.get("/api/v1/certificates/verify/ORB-0000-XXXX/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_learner_lists_own_certificates(self):
        self.client.force_authenticate(self.student)
        response = self.client.get("/api/v1/certificates/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)