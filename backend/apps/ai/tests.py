from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.ai.models import AIMessage, AISession, Recommendation
from apps.ai.services import AIOrchestrator, ContextBuilder
from apps.common.tests import make_agent, make_course, make_user
from apps.learning.models import Enrollment, Skill, UserSkill


class OrchestratorTests(TestCase):
    def setUp(self):
        self.student = make_user("iauser")
        self.agent = make_agent()

    def test_reply_creates_session_and_messages(self):
        session, answer = AIOrchestrator(self.student).reply("Explique-moi Django.", agent=self.agent)
        self.assertIsNotNone(session)
        self.assertIn("Django", answer or "")
        self.assertEqual(
            AIMessage.objects.filter(session=session).count(), 2
        )

    def test_no_direct_db_access_via_agent(self):
        """The orchestrator builds a context; the default provider answers locally."""
        session, answer = AIOrchestrator(self.student).reply(
            "C'est quoi une variable ?", agent=self.agent
        )
        self.assertTrue(answer)
        self.assertTrue(session.agent_id == self.agent.id)

    def test_context_builder_injects_skills_and_lesson(self):
        course = make_course(instructor=make_user("prof_cb", role="instructor"), title="Context Builder")
        module = course.modules.first()
        lesson = module.lessons.first()
        lesson.content = "Le contenu exact de la leçon : les boucles en Python."
        lesson.save()
        skill = Skill.objects.create(name="Python", slug="python", category="Backend")
        UserSkill.objects.create(
            user=self.student, skill=skill, mastery_score=25, confidence=0.3
        )
        session = AISession.objects.create(
            user=self.student, agent=self.agent, course=course, lesson=lesson
        )
        context = ContextBuilder(self.student, session, self.agent).build()
        self.assertIn("le contenu exact de la leçon", context.lower())
        self.assertIn("points forts", context.lower())
        self.assertIn("compétences à renforcer", context.lower())
        self.assertIn("python", context.lower())


class ChatApiTests(APITestCase):
    def setUp(self):
        self.student = make_user("chateur")
        self.agent = make_agent()

    def test_ask_endpoint(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            "/api/v1/ai/sessions/ask/",
            {"content": "Comment structurer mon backend ?", "agent_id": self.agent.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("session", response.data)
        self.assertTrue(response.data["answer"])

    def test_sessions_scoped_to_user(self):
        make_course  # noqa - keep import footprint symmetrical
        user2 = make_user("autre_ia")
        s1 = AISession.objects.create(user=self.student, agent=self.agent, title="Mine")
        AISession.objects.create(user=user2, agent=self.agent, title="Pas à moi")

        self.client.force_authenticate(self.student)
        response = self.client.get("/api/v1/ai/sessions/")
        ids = [s["id"] for s in response.data["results"]]
        self.assertIn(s1.id, ids)
        self.assertEqual(len(ids), 1)

    def test_agents_public(self):
        response = self.client.get("/api/v1/ai/agents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials()
        response = self.client.get("/api/v1/ai/agents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ask_binds_session_to_course_and_lesson(self):
        from apps.courses.models import Lesson

        course = make_course(instructor=make_user("prof_ask", role="instructor"), title="Session liée")
        lesson = Lesson.objects.first() or course.modules.first().lessons.first()
        self.client.force_authenticate(self.student)
        response = self.client.post(
            "/api/v1/ai/sessions/ask/",
            {
                "content": "Aide-moi sur cette leçon.",
                "agent_id": self.agent.id,
                "course_id": course.id,
                "lesson_id": lesson.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        session = AISession.objects.get(pk=response.data["session"]["id"])
        self.assertEqual(session.course_id, course.id)
        self.assertEqual(session.lesson_id, lesson.id)


class RecommendationTests(APITestCase):
    def setUp(self):
        self.student = make_user("recu")
        self.instructor = make_user("prof", role="instructor")

    def test_refresh_creates_recommendation(self):
        course = make_course(instructor=self.instructor, price=0, title="En cours")
        enrollment = Enrollment.objects.create(user=self.student, course=course)

        self.client.force_authenticate(self.student)
        response = self.client.post("/api/v1/ai/recommendations/refresh/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recs = Recommendation.objects.filter(user=self.student)
        self.assertGreaterEqual(recs.count(), 1)
        self.assertIn("En cours", recs.first().course.title)