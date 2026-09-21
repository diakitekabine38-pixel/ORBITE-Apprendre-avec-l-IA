"""ORBITE AI Orchestrator.

User → Django → AI Orchestrator → Context Builder → Agent → LLM → Validation → Django → User

The agents never touch the database directly; they consume the context the
backend builds for them, and their output is validated before reaching the user.
"""
import json
import logging

from django.conf import settings
from django.utils import timezone

from .models import AIMessage, AISession, Recommendation

logger = logging.getLogger(__name__)


class LLMProvider:
    """Provider interface. `mock` is the default dev provider."""

    def complete(self, *, system, messages):
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    """Deterministic dev provider — no external call, safe in tests/CI."""

    def complete(self, *, system, messages):
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        if not last_user:
            last_user = "Aucune question détectée."
        return (
            f"[KODEX · aperçu hors-ligne] Tu me demandes : « {last_user[:120]} ». "
            "Voici comment aborder la notion, pas à pas : "
            "1) Définis l'idée en une phrase, 2) Prends un exemple concret, "
            "3) Applique-la à un mini-exercice, 4) Vérifie ta compréhension par une question. "
            "Dis-moi avec tes mots ce que tu comprends et je poursuis."
        )


def _get_provider():
    provider_name = getattr(settings, "ORBITE_LLM_PROVIDER", "mock").lower()
    providers = {
        "mock": MockLLMProvider,
        "openai": OpenAILikeProvider,
        "anthropic": OpenAILikeProvider,
    }
    cls = providers.get(provider_name, MockLLMProvider)
    return cls()


class OpenAILikeProvider(LLMProvider):
    """Generic OpenAI-compatible chat completions provider (works with many LLMs)."""

    def __init__(self):
        self.api_key = getattr(settings, "ORBITE_LLM_API_KEY", "")
        self.model = getattr(settings, "ORBITE_LLM_MODEL", "orbite-default")

    def complete(self, *, system, messages):
        if not self.api_key:
            return MockLLMProvider().complete(system=system, messages=messages)
        import urllib.request

        base_url = getattr(settings, "ORBITE_LLM_BASE_URL", "https://api.openai.com/v1")
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "system", "content": system}] + messages,
                "temperature": 0.4,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{base_url}/chat/completions", data=payload, method="POST"
        )
        request.add_header("Content-Type", "application/json")
        request.add_header("Authorization", f"Bearer {self.api_key}")
        # Groq (et plusieurs passerelles Cloudflare) bloquent le User-Agent
        # par défaut de Python/urllib (erreur 1010). Un agent explicite passe.
        request.add_header("User-Agent", "OrbitePlatform/1.0 (Django backend)" )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"]
        except Exception:  # noqa: BLE001 - never crash the chat endpoint
            logger.exception("LLM call failed")
            return MockLLMProvider().complete(system=system, messages=messages)


def _lesson_text(lesson):
    """Normalise le contenu d'une leçon (chaîne ou bloc JSON) pour l'agent."""
    content = lesson.content or ""
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                text = block.get("text") or block.get("content") or ""
                if text:
                    parts.append(str(text))
            else:
                parts.append(str(block))
        content = " ".join(parts)
    return str(content).strip()


class ContextBuilder:
    """Builds a focused, pedagogically-situated context for the tutor agent.

    It turns the learner profile (personal data, progression, mastery signals,
    goals, last assessments) into a prompt block so every agent tutors based on
    what the learner really knows — not on generic advice.
    """

    def __init__(self, user, session, agent=None):
        self.user = user
        self.session = session
        self.agent = agent

    def build(self):
        from apps.learning.models import Enrollment, Goal, UserSkill

        u = self.user
        lines = [
            f"Tu t'adresses à {u.full_name} (pseudo : {u.username}).",
            "Méthode ORBITE : tu es un tuteur, pas un simple chatbot. "
            "Explique, reformule, donne un exemple concret, pose une question, "
            "propose un mini-exercice puis évalue — une seule étape à la fois, "
            "en t'adaptant aux réponses de l'apprenant.",
            "Sois sympathique, patient et encourageant : tu y vas doucement, "
            "tu félicites les progrès et tu rassures en cas d'erreur.",
            "Langue et style : réponds en français, en vocabulaire simple et "
            "chaleureux, sans jargon inutile. N'invente jamais de faits.",
            "Longueur : adapte ta réponse à celle du message de l'élève. "
            "Un simple « salut » mérite une réponse chaleureuse de 1-2 phrases "
            "(salue-le, demande comment il va, propose ton aide), pas un cours. "
            "Une question courte reçoit une réponse courte et claire. "
            "Développe en profondeur seulement si l'élève le demande ou si la "
            "question est technique — toujours une idée à la fois.",
        ]

        if self.agent is not None:
            rules = self.agent.teaching_rules or []
            if isinstance(rules, list) and rules:
                lines.append(
                    f"Règles pédagogiques de {self.agent.name} : "
                    + "; ".join(str(rule) for rule in rules)
                    + "."
                )

        if self.session.course_id:
            lines.append(f"Formation suivie : {self.session.course.title}.")
        if self.session.lesson_id:
            lesson = self.session.lesson
            module = lesson.module
            lines.append(
                f"Leçon en cours : « {lesson.title} » — module « {module.title} »."
            )
            snippet = _lesson_text(lesson)[:400]
            if snippet:
                lines.append(f"Contenu de la leçon en cours : {snippet}")

        goals = Goal.objects.filter(user=u, status=Goal.STATUS_ACTIVE)[:3]
        if goals.exists():
            lines.append(
                "Objectifs actifs de l'apprenant : "
                + ", ".join(goal.title for goal in goals)
                + "."
            )

        enrollments = Enrollment.objects.filter(user=u).select_related("course")
        if enrollments.exists():
            rows = ", ".join(
                f"{e.course.title} ({int(e.progress)}%)" for e in enrollments[:5]
            )
            lines.append(f"Progression de l'apprenant : {rows}.")
        else:
            lines.append("L'apprenant n'est pas encore inscrit à une formation.")

        skills = list(
            UserSkill.objects.filter(user=u)
            .select_related("skill")
            .order_by("-mastery_score")
        )
        if skills:
            strong = ", ".join(
                f"{s.skill.name} ({s.mastery_score}%)" for s in skills[:5]
            )
            weak_list = [f"{s.skill.name} ({s.mastery_score}%)" for s in skills if s.mastery_score < 40]
            lines.append(f"Points forts identifiés : {strong}.")
            if weak_list:
                lines.append(
                    "Compétences à renforcer : " + ", ".join(weak_list) + "."
                )
        else:
            lines.append(
                "Aucune compétence évaluée pour l'instant : propose des questions "
                "d'évaluation pour mesurer les acquis."
            )

        from apps.assessments.models import Attempt

        attempts = list(Attempt.objects.filter(user=u).order_by("-created_at")[:3])
        if attempts:
            results = ", ".join(
                f"{a.quiz.title} : {a.score}% "
                f"({'réussi' if a.passed else 'à retravailler'})"
                for a in attempts
            )
            lines.append(f"Derniers résultats d'évaluation : {results}.")

        return "\n".join(lines)


class AIOrchestrator:
    def __init__(self, user, session=None):
        self.user = user
        self.session = session

    def select_agent(self, agent_id=None):
        from .models import AIAgent

        if agent_id:
            return AIAgent.objects.filter(id=agent_id, is_active=True).first()
        # Default: the course's AI mentor, else KODEX.
        if self.session and self.session.course and self.session.course.ai_mentor_id:
            return self.session.course.ai_mentor
        return AIAgent.objects.filter(code="kodex", is_active=True).first() or AIAgent.objects.first()

    def reply(self, content, agent=None, save_session=True, course=None, lesson=None):
        agent = agent or self.select_agent()
        if self.session is None:
            self.session = AISession.objects.create(
                user=self.user,
                agent=agent,
                title=content[:60],
                course=course,
                lesson=lesson,
            )
        else:
            fields = ["updated_at"]
            if self.session.agent_id != agent.id:
                self.session.agent = agent
                fields.append("agent")
            if course is not None and self.session.course_id is None:
                self.session.course = course
                fields.append("course")
            if lesson is not None and self.session.lesson_id != lesson.id:
                self.session.lesson = lesson
                fields.append("lesson")
            self.session.save(update_fields=fields)

        history = list(
            self.session.messages.order_by("id").values_list("role", "content")[:20]
        )
        system = f"{agent.system_prompt or agent.personality}\n{ContextBuilder(self.user, self.session, agent).build()}"
        messages = [{"role": role, "content": content} for role, content in history]
        messages.append({"role": "user", "content": content})

        AIMessage.objects.create(session=self.session, role=AIMessage.ROLE_USER, content=content)
        answer = _get_provider().complete(system=system, messages=messages)
        AIMessage.objects.create(session=self.session, role=AIMessage.ROLE_ASSISTANT, content=answer)

        from apps.analytics.models import Event

        Event.objects.create(
            user=self.user,
            event_type="ai_session_started",
            context={"agent": agent.code, "session": self.session.id},
        )
        return self.session, answer


def run_recommendations(user, limit=3):
    """Ask the adaptive engine for recommendations and persist them."""
    from apps.learning.services import recommend_next_action

    recs = recommend_next_action(user, limit=limit)
    for rec in recs:
        existing = Recommendation.objects.filter(
            user=rec.user, course=rec.course, reason=rec.reason, is_dismissed=False
        ).first()
        if existing:
            existing.score = rec.score
            existing.rationale = rec.rationale
            existing.save(update_fields=["score", "rationale", "updated_at"])
        else:
            rec.save()
    return list(
        Recommendation.objects.filter(user=user, is_dismissed=False).order_by("-score")[:10]
    )