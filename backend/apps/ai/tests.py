from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from apps.ai.models import AIMessage, AISession, Recommendation
from apps.ai.services import (
    AIOrchestrator,
    ContextBuilder,
    LearnerProfileService,
)
from apps.common.tests import make_agent, make_course, make_user
from apps.learning.models import Enrollment, Skill, UserSkill


@override_settings(ORBITE_LLM_PROVIDER="mock")
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

    def test_mock_greets_and_states_mission(self):
        session, answer = AIOrchestrator(self.student).reply(
            "bonjour", agent=self.agent
        )
        self.assertIn("Bonjour", answer)
        self.assertIn("coach", answer.lower())
        self.assertIn("mon rôle", answer.lower())
        self.assertLess(len(answer), 500, "la salutation reste brève")

    def test_mock_stays_short_and_asks_one_question(self):
        _, answer = AIOrchestrator(self.student).reply(
            "Explique-moi Django.", agent=self.agent
        )
        self.assertIn("Django", answer)
        self.assertIn("?", answer)
        self.assertLess(len(answer), 500)

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

    def test_context_builder_pushes_personalization_when_profile_unknown(self):
        session = AISession.objects.create(user=self.student, agent=self.agent)
        builder = ContextBuilder(self.student, session, self.agent)
        self.assertIn("profil de l'apprenant inconnu", builder.build().lower())
        self.assertIn("pose une question", builder.build().lower())
        self.assertIn("générique", builder.build().lower())

    def test_context_builder_uses_profile_once_known(self):
        LearnerProfileService.update(
            self.student,
            {
                "niveau": "débutant",
                "objectif": "Devenir développeur web",
                "statut": "étudiant",
                "disponibilite": "10h par semaine",
                "methode": "exercices",
                "motivation": "motivation",
            },
        )
        session = AISession.objects.create(user=self.student, agent=self.agent)
        context = ContextBuilder(self.student, session, self.agent).build().lower()
        self.assertIn("devenir développeur web", context)
        self.assertIn("débutant", context)
        self.assertNotIn("dimensions du profil à découvrir", context)
        self.assertIn("profil complet", context)

    def test_context_builder_injects_resources_with_usage_directive(self):
        self.agent.resources = [
            {"titre": "France IO", "url": "https://www.france-ioi.org", "description": "plateforme", "gratuit": True},
            {"titre": "CodinGame", "url": "https://www.codingame.com", "description": "défis", "gratuit": True},
        ]
        self.agent.save(update_fields=["resources"])
        session = AISession.objects.create(user=self.student, agent=self.agent)
        context = ContextBuilder(self.student, session, self.agent).build().lower()
        self.assertIn("ressources externes recommandées", context)
        self.assertIn("france-ioi.org", context)
        self.assertIn("jamais toute la liste", context)
        self.assertIn("si la question n'en a pas besoin, n'en parle pas", context)

    def test_context_builder_skips_resources_when_empty(self):
        session = AISession.objects.create(user=self.student, agent=self.agent)
        context = ContextBuilder(self.student, session, self.agent).build().lower()
        self.assertNotIn("ressources externes recommandées", context)


class LearnerProfileTests(TestCase):
    def setUp(self):
        self.student = make_user("profil")

    def test_extract_from_detects_several_dimensions(self):
        updates = LearnerProfileService.extract_from(
            self.student,
            "Je suis étudiant et je débute en Python. Je veux devenir développeur, "
            "je peux y consacrer 10h par semaine le soir. J'aime apprendre par les exercices.",
        )
        updates = set(updates)
        stored = LearnerProfileService.read(self.student)
        self.assertIn("statut", updates)
        self.assertEqual(stored.get("statut"), "étudiant")
        self.assertIn("niveau", updates)
        self.assertEqual(stored.get("niveau"), "débutant")
        self.assertIn("objectif", updates)
        self.assertIn("devenir développeur", stored["objectif"])
        self.assertIn("disponibilite", updates)
        self.assertIn("10h", stored["disponibilite"])
        self.assertIn("methode", updates)
        self.assertEqual(stored.get("methode"), "exercices")

    def test_load_lists_missing_dimensions(self):
        data = LearnerProfileService.load(self.student)
        self.assertEqual(data["known"], {})
        self.assertGreaterEqual(len(data["missing"]), 5)
        LearnerProfileService.update(self.student, {"niveau": "débutant"})
        data = LearnerProfileService.load(self.student)
        self.assertEqual(data["known"], {"niveau": "débutant"})
        self.assertNotIn("niveau", data["missing"])

    def test_extract_does_not_override_known_values(self):
        LearnerProfileService.update(self.student, {"niveau": "avancé"})
        LearnerProfileService.extract_from(self.student, "Je débute complètement.")
        stored = LearnerProfileService.read(self.student)
        self.assertEqual(stored["niveau"], "avancé")


@override_settings(ORBITE_LLM_PROVIDER="mock")
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

    def test_ask_continues_same_session_with_session_id(self):
        self.client.force_authenticate(self.student)
        first = self.client.post(
            "/api/v1/ai/sessions/ask/",
            {"content": "Je débute en Python, par où commencer ?", "agent_id": self.agent.id},
            format="json",
        )
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        session_id = first.data["session"]["id"]
        self.assertEqual(AIMessage.objects.filter(session_id=session_id).count(), 2)

        second = self.client.post(
            "/api/v1/ai/sessions/ask/",
            {
                "content": "Et maintenant, qu'est-ce qu'une boucle for ?",
                "agent_id": self.agent.id,
                "session_id": session_id,
            },
            format="json",
        )
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            second.data["session"]["id"], session_id,
            "la seconde question doit poursuivre la même conversation",
        )
        self.assertEqual(
            AIMessage.objects.filter(session_id=session_id).count(), 4,
            "les deux tours (user + assistant) s'accumulent dans la session",
        )
        history = list(
            AIMessage.objects.filter(session_id=session_id).order_by("id").values_list("role", "content")
        )
        self.assertEqual(history[0][0], "user")
        self.assertEqual(history[1][0], "assistant")
        self.assertEqual(history[2][1], "Et maintenant, qu'est-ce qu'une boucle for ?")

    def test_ask_ignores_foreign_session(self):
        other = make_user("autre_chat")
        foreign = AISession.objects.create(user=other, agent=self.agent, title="À toi")
        self.client.force_authenticate(self.student)
        response = self.client.post(
            "/api/v1/ai/sessions/ask/",
            {
                "content": "Puis-je continuer ta conversation ?",
                "agent_id": self.agent.id,
                "session_id": foreign.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(
            response.data["session"]["id"], foreign.id,
            "une session d'un autre utilisateur ne doit pas être réutilisée",
        )

    def test_profile_endpoint(self):
        self.client.force_authenticate(self.student)
        response = self.client.get("/api/v1/ai/sessions/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("known", response.data)
        self.assertIn("missing", response.data)
        self.assertIn("dimensions", response.data)
        self.assertGreaterEqual(len(response.data["missing"]), 5)

    def test_ask_extracts_learner_profile(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            "/api/v1/ai/sessions/ask/",
            {"content": "Je suis étudiant et je débute en Python.", "agent_id": self.agent.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stored = LearnerProfileService.read(self.student)
        self.assertEqual(stored.get("statut"), "étudiant")
        self.assertEqual(stored.get("niveau"), "débutant")


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


class AgentAdminApiTests(APITestCase):
    def setUp(self):
        self.admin = make_user("admin_agent", role="admin")
        self.student = make_user("student_agent")
        self.agent = make_agent()

    def test_admin_can_create_and_edit_persona(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/v1/ai/admin/agents/",
            {
                "code": "tutorai",
                "name": "Tutor IA",
                "specialty": "Mentorat général",
                "personality": "Patiente et pédagogue.",
                "system_prompt": "Tu es un tuteur bienveillant. Explique par étapes.",
                "teaching_rules": ["Expliquer simplement", "Donner un exemple"],
                "expertise": "advanced",
                "model": "openai/gpt-oss-20b",
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = response.data
        self.assertEqual(created["system_prompt"], "Tu es un tuteur bienveillant. Explique par étapes.")
        self.assertEqual(len(created["teaching_rules"]), 2)

        patch = self.client.patch(
            f"/api/v1/ai/admin/agents/{created['id']}/",
            {"system_prompt": "Rôle mis à jour : expert senior."},
            format="json",
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        self.assertEqual(patch.data["system_prompt"], "Rôle mis à jour : expert senior.")

    def test_public_list_never_exposes_system_prompt(self):
        response = self.client.get("/api/v1/ai/agents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("system_prompt", response.data["results"][0])

    def test_non_admin_cannot_manage_agents(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            "/api/v1/ai/admin/agents/", {"name": "Nope"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)