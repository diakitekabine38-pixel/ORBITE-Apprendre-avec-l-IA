from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.tests import make_agent, make_course, make_user
from apps.courses.models import Course


class CourseWorkflowTests(APITestCase):
    """BROUILLON → SOUMIS → EN RÉVISION → APPROUVÉ → PUBLIÉ, admin-only publish."""

    def setUp(self):
        self.instructor = make_user("prof", role="instructor")
        self.admin = make_user("admin1", role="admin")
        self.student = make_user("etudiant")

    def test_instructor_cannot_self_publish(self):
        self.client.force_authenticate(self.instructor)
        create = self.client.post(
            "/api/v1/courses/courses/",
            {"title": "Nouvelle formation", "description": "Desc", "price": 5000},
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        slug = create.data["slug"]

        publish = self.client.post(f"/api/v1/courses/courses/{slug}/publish/")
        self.assertEqual(publish.status_code, status.HTTP_403_FORBIDDEN)

    def test_full_publication_chain(self):
        self.client.force_authenticate(self.instructor)
        create = self.client.post(
            "/api/v1/courses/courses/",
            {"title": "Chaîne complète", "description": "Desc", "price": 10000},
            format="json",
        )
        slug = create.data["slug"]

        def endpoint(action):
            return self.client.post(f"/api/v1/courses/courses/{slug}/{action}/")

        self.assertEqual(endpoint("submit").data["status"], Course.STATUS_SUBMITTED)
        # Instructor cannot move to review — needs admin
        self.assertEqual(endpoint("start_review").status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.admin)
        self.assertEqual(endpoint("start_review").data["status"], Course.STATUS_IN_REVIEW)
        self.assertEqual(endpoint("approve").data["status"], Course.STATUS_APPROVED)
        self.assertEqual(endpoint("publish").data["status"], Course.STATUS_PUBLISHED)

    def test_students_see_only_published(self):
        make_course(instructor=self.instructor, status=Course.STATUS_DRAFT, title="Brouillon X")
        make_course(instructor=self.instructor, status=Course.STATUS_PUBLISHED, title="Visible")
        self.client.force_authenticate(self.student)
        response = self.client.get("/api/v1/courses/courses/")
        titles = [c["title"] for c in response.data["results"]]
        self.assertIn("Visible", titles)
        self.assertNotIn("Brouillon X", titles)

    def test_public_catalog(self):
        make_course(instructor=self.instructor)
        response = self.client.get("/api/v1/courses/courses/")
        self.client.credentials()
        response = self.client.get("/api/v1/courses/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)


class CourseAccessTests(APITestCase):
    def setUp(self):
        self.instructor = make_user("prof", role="instructor")
        self.student = make_user("etudiant")
        self.course = make_course(instructor=self.instructor, price=10000)
        self.lesson = self.course.modules.first().lessons.first()

    def test_locked_lesson_hides_video_for_non_enrolled(self):
        self.client.force_authenticate(self.student)
        response = self.client.get(f"/api/v1/courses/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("locked"))
        self.assertNotIn("content", response.data)

    def test_enrolled_student_sees_video(self):
        from apps.learning.models import Enrollment

        Enrollment.objects.create(user=self.student, course=self.course)
        self.client.force_authenticate(self.student)
        response = self.client.get(f"/api/v1/courses/lessons/{self.lesson.id}/")
        self.assertIn("video", response.data)

    def test_review_requires_enrollment(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            "/api/v1/courses/reviews/",
            {"course": self.course.id, "rating": 5, "comment": "Super !"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)