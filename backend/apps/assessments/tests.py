from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.assessments.models import Attempt
from apps.assessments.services import grade_attempt
from apps.common.tests import make_course, make_user
from apps.learning.models import Enrollment


class GradingTests(TestCase):
    def setUp(self):
        self.student = make_user("quizzer")
        self.instructor = make_user("prof", role="instructor")
        self.course = make_course(instructor=self.instructor, price=0)
        self.quiz = self.course.modules.first().lessons.first().quizzes.first()

    def _answers(self, pairs):
        return [{"question_id": q.id, "answer": a} for q, a in pairs]

    def test_perfect_quiz_passes_and_awards_xp(self):
        questions = list(self.quiz.questions.all())
        xp_before = self.student.xp
        attempt, detail = grade_attempt(
            self.student, self.quiz, self._answers([(q, q.correct[0]) for q in questions])
        )
        self.assertEqual(attempt.score, 100.0)
        self.assertTrue(attempt.passed)
        self.student.refresh_from_db()
        self.assertGreaterEqual(self.student.xp, xp_before + 50)

    def test_wrong_answers_fail_quiz(self):
        questions = list(self.quiz.questions.all())
        attempt, _ = grade_attempt(
            self.student, self.quiz, self._answers([(q, "mauvaise réponse") for q in questions])
        )
        self.assertLess(attempt.score, 50.0)
        self.assertFalse(attempt.passed)


class AttemptApiTests(APITestCase):
    def setUp(self):
        self.student = make_user("student2")
        self.instructor = make_user("prof", role="instructor")
        self.course = make_course(instructor=self.instructor, price=0)
        Enrollment.objects.create(user=self.student, course=self.course)
        self.quiz = self.course.modules.first().lessons.first().quizzes.first()

    def test_submit_quiz_via_api(self):
        self.client.force_authenticate(self.student)
        payload = {
            "quiz": self.quiz.id,
            "answers": [
                {"question_id": q.id, "answer": q.correct[0]}
                for q in self.quiz.questions.all()
            ],
        }
        response = self.client.post("/api/v1/assessments/attempts/submit/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["score"], 100.0)

    def test_non_enrolled_cannot_submit(self):
        outsider = make_user("ext")
        self.client.force_authenticate(outsider)
        response = self.client.post(
            "/api/v1/assessments/attempts/submit/",
            {"quiz": self.quiz.id, "answers": []},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_max_attempts_enforced(self):
        self.client.force_authenticate(self.student)
        payload = {
            "quiz": self.quiz.id,
            "answers": [
                {"question_id": q.id, "answer": q.correct[0]}
                for q in self.quiz.questions.all()
            ],
        }
        attempts = self.quiz.max_attempts + 2
        for i in range(attempts):
            response = self.client.post(
                "/api/v1/assessments/attempts/submit/", payload, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Attempt.objects.filter(quiz=self.quiz, user=self.student).count(), self.quiz.max_attempts)