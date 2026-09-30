"""ORBITE AI Orchestrator.

User → Django → AI Orchestrator → Context Builder → Agent → LLM → Validation → Django → User

The agents never touch the database directly; they consume the context the
backend builds for them, and their output is validated before reaching the user.
"""
import json
import logging
import re

from django.conf import settings
from django.utils import timezone

from .models import AIMessage, AISession, Recommendation

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Profil de l'apprenant : les dimensions que les coachs doivent connaître pour
# personnaliser réellement leurs réponses (au lieu d'un discours générique).
# ---------------------------------------------------------------------------

LEARNER_PROFILE_DIMENSIONS = [
    ("objectif", "son objectif principal (ex. changer de métier, obtenir un diplôme, se spécialiser)"),
    ("statut", "son statut (étudiant, professionnel, en reconversion, autodidacte…)"),
    ("niveau", "son niveau actuel dans le domaine (débutant, intermédiaire, avancé)"),
    ("disponibilite", "son temps disponible pour apprendre (heures par semaine, moments de la journée)"),
    ("methode", "sa méthode d'apprentissage préférée (vidéos, lecture, exercices, pratique, projets)"),
    ("motivation", "sa motivation, ainsi que les difficultés ou blocages éventuels"),
]

_PROFILE_LABELS = {key: label for key, label in LEARNER_PROFILE_DIMENSIONS}

_NIVEAU_RULES = [
    (re.compile(r"\b(zéro|rien|jamais|début|débute|débutant|débutante)\b", re.I), "débutant"),
    (re.compile(r"\b(intermédiaire|moyen|quelques bases|je connais)\b", re.I), "intermédiaire"),
    (re.compile(r"\b(avancé|confirmé|expert|bon niveau)\b", re.I), "avancé"),
]

_METHODE_RULES = [
    (re.compile(r"\b(vidéo|vidéos|regarder|regarde|écouter|podcasts?)\b", re.I), "vidéos / audio"),
    (re.compile(r"\b(livre|lecture|lire|articles?|documentation)\b", re.I), "lecture"),
    (re.compile(r"\b(exercice|exercices|quiz|entraîn|entraînement|fiches)\b", re.I), "exercices"),
    (re.compile(r"\b(pratique|mise en pratique|projets?|réaliser|construire|appliquer)\b", re.I), "projets pratiques"),
]

_STATUT_RULES = [
    (re.compile(r"\b(reconversion|changer de métier|nouveau métier)\b", re.I), "en reconversion"),
    (re.compile(r"\b(étudiant|étudiante|lycéen|lycéenne|faculté|université|école)\b", re.I), "étudiant"),
    (re.compile(r"\b(professionnel|professionnelle|je travaille|salarié|salariée|en poste)\b", re.I), "professionnel"),
    (re.compile(r"\b(autodidacte|auto-formation|par moi-même)\b", re.I), "autodidacte"),
]

_OBJECTIF_RULES = [
    (re.compile(r"\b(mon objectif|mon but|ma cible)\b", re.I), "objectif"),
    (re.compile(r"\b(je veux|j'aimerais|je souhaite|je compte|je vise|je rêve de)\b", re.I), "objectif"),
    (re.compile(r"\b(devenir|pour devenir)\b", re.I), "objectif"),
]

_DISPONIBILITE_RULES = [
    (re.compile(r"\b(\d{1,2})\s*h(?:eures?)?\b", re.I), "heures/semaine"),
    (re.compile(r"\b(le soir|le matin|la nuit|le week-end|le weekend|les week-ends)\b", re.I), "moments de la journée"),
]

_MOTIVATION_RULES = [
    (re.compile(r"\b(motivation|motivé|motivée|passion)\b", re.I), "motivation"),
    (re.compile(r"\b(bloque|bloqué|difficile|j'ai du mal|j'ai mal|décourag|perds|manque de temps)\b", re.I), "difficultés"),
]


def _sentence_around(text, match):
    """Extrait la phrase contenant le match (tronquée proprement)."""
    start = text.rfind(".", 0, match.start()) + 1
    end = text.find(".", match.end())
    if end == -1:
        end = len(text)
    snippet = re.sub(r"\s+", " ", text[start:end])
    return snippet.strip(" .")[:180]


class LearnerProfileService:
    """Mémoire « qui est cet apprenant » : ce que les coachs savent de lui.

    Les dimensions sont stockées dans `Profile.ai_preferences["learner_profile"]`
    (partagées entre tous les coachs) afin que chaque agent personnalise ses
    réponses avec la même connaissance de l'apprenant.
    """

    @staticmethod
    def read(user):
        profile = getattr(user, "profile", None)
        if profile is None:
            return {}
        return dict(profile.ai_preferences.get("learner_profile") or {})

    @staticmethod
    def load(user):
        stored = LearnerProfileService.read(user)
        known = {key: value for key, value in stored.items() if value}
        missing = [key for key, _ in LEARNER_PROFILE_DIMENSIONS if key not in known]

        lines = []
        if known:
            parts = []
            for key, _ in LEARNER_PROFILE_DIMENSIONS:
                if key in known:
                    parts.append(f"{_PROFILE_LABELS[key]} → {known[key]}")
            lines.append("Profil connu de l'apprenant : " + "; ".join(parts) + ".")
        else:
            lines.append("Profil de l'apprenant inconnu (aucune dimension renseignée pour l'instant).")
        if missing:
            labels = " ; ".join(_PROFILE_LABELS[key] for key in missing)
            lines.append(f"Dimensions du profil à découvrir : {labels}.")
        return {"known": known, "missing": missing, "lines": lines}

    @staticmethod
    def update(user, updates):
        profile = getattr(user, "profile", None)
        if profile is None:
            return
        prefs = dict(profile.ai_preferences)
        stored = dict(prefs.get("learner_profile") or {})
        stored.update({k: v for k, v in updates.items() if v})
        prefs["learner_profile"] = stored
        profile.ai_preferences = prefs
        profile.save(update_fields=["ai_preferences", "updated_at"])

    @staticmethod
    def extract_from(user, text):
        """Détecte des informations sur l'apprenant dans son message et les mémorise."""
        if not text:
            return []
        stored = LearnerProfileService.read(user)
        updates = {}

        lowered = text.lower()
        for regex, value in _NIVEAU_RULES:
            if "niveau" not in stored and regex.search(lowered):
                updates["niveau"] = value
                break
        for regex, value in _METHODE_RULES:
            if "methode" not in stored and regex.search(lowered):
                updates["methode"] = value
                break
        for regex, value in _STATUT_RULES:
            if "statut" not in stored and regex.search(lowered):
                updates["statut"] = value
                break

        if "objectif" not in stored:
            for regex, _ in _OBJECTIF_RULES:
                match = regex.search(text)
                if match:
                    updates["objectif"] = _sentence_around(text, match)
                    break
        if "disponibilite" not in stored:
            for regex, label in _DISPONIBILITE_RULES:
                match = regex.search(text)
                if match:
                    value = f"{label} — {_sentence_around(text, match)}"
                    updates["disponibilite"] = value[:180]
                    break
        if "motivation" not in stored:
            for regex, label in _MOTIVATION_RULES:
                if regex.search(lowered):
                    updates["motivation"] = label
                    break

        if updates:
            LearnerProfileService.update(user, updates)
        return list(updates)


class LLMProvider:
    """Provider interface. `mock` is the default dev provider."""

    def complete(self, *, system, messages):
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    """Deterministic dev provider — no external call, safe in tests/CI.

    Conscient de son persona : il lit le nom et le domaine du coach dans le
    system prompt, salue brièvement (politesse + mission) quand on le salue,
    et répond court sinon — jamais de cours générique déversé d'un coup.
    """

    _GREETING = re.compile(
        r"^\s*(bonjour|bonsoir|salut|slt|bjr|hello|hi|coucou|hey|yo|wesh|cc)\b[\s!.,…;:-]*$",
        re.IGNORECASE,
    )

    @staticmethod
    def _persona(system):
        match = re.search(
            r"Tu es (\w+),?\s+(?:formateur|formatrice)\s+IA\s+d'ORBITE\s+en\s+([^.\n]+?)\.",
            system or "",
            re.IGNORECASE,
        )
        if match:
            return match.group(1).upper(), match.group(2).strip()
        return "Coach IA", "ton domaine"

    def complete(self, *, system, messages):
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        ).strip()
        name, domain = self._persona(system)
        if not last_user:
            last_user = "Aucune question détectée."
        if self._GREETING.match(last_user):
            return (
                f"Bonjour à toi ! 😊 Je suis {name}, ton coach d'ORBITE spécialisé "
                f"en {domain}.\n\n"
                f"Mon rôle : t'accompagner pas à pas pour progresser à ton rythme, "
                f"avec des exemples concrets.\n\n"
                f"Ça te dit de me parler de toi en une phrase (ton objectif, ton "
                f"niveau actuel) ? On part de là."
            )
        return (
            f"[{name}] J'ai bien noté : « {last_user[:120]} ». Avant de te répondre "
            f"précisément sur {domain} : où en es-tu exactement sur ce sujet, et "
            f"qu'est-ce qui te bloque ? Je t'expliquerai avec un exemple concret à "
            f"ton niveau, une étape à la fois."
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
        profile = LearnerProfileService.load(u)
        lines = profile["lines"]
        lines += [
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
            "Accueil : quand l'apprenant te salue (bonjour, salut…), réponds par une "
            "salutation chaleureuse avec une formule de politesse, puis présente en "
            "UNE phrase qui tu es et ce que tu fais (ta mission) ; garde l'ensemble "
            "très court et termine par une question d'accroche pour faire connaissance.",
        ]

        if profile["missing"]:
            lines += [
                "Personnalisation stricte : ne fournis JAMAIS une réponse « générique "
                "pour tout le monde ». Base chaque réponse sur ce que tu sais de "
                "l'apprenant (voir profil ci-dessus) : utilise son objectif, son statut, "
                "son niveau, sa disponibilité et sa méthode préférée pour choisir les "
                "exemples, le rythme et les outils que tu proposes.",
                "Fais connaissance : le profil est incomplet (dimensions à découvrir). "
                "Pose UNE question par échange (jamais deux à la suite) sur une dimension "
                "manquante du profil — pour ouvrir la conversation ou en complément de ta "
                "réponse — afin d'apprendre à réellement connaître l'apprenant. Quand une "
                "dimension est renseignée, ne la redemande plus. Reste naturel : tu fais "
                "connaissance, pas un interrogatoire.",
            ]
        else:
            lines += [
                "Profil complet : personnalise chaque réponse avec ces informations "
                "(objectif, statut, niveau, disponibilité, méthode, motivation). "
                "Si un doute subsiste, pose une question de précision adaptée.",
            ]

        if self.agent is not None:
            rules = self.agent.teaching_rules or []
            if isinstance(rules, list) and rules:
                lines.append(
                    f"Règles pédagogiques de {self.agent.name} : "
                    + "; ".join(str(rule) for rule in rules)
                    + "."
                )

        if self.agent is not None:
            resources = self.agent.resources or []
            if isinstance(resources, list):
                items = [
                    f"{r.get('titre') or r.get('name') or '…'} ({r.get('url', '')})"
                    for r in resources
                    if isinstance(r, dict) and r.get("url")
                ]
                if items:
                    lines.append(
                        f"Ressources externes recommandées par ORBITE (sélection de qualité) : "
                        + "; ".join(items)
                        + "."
                    )
                    lines.append(
                        "Usage de ces ressources : ce sont des suggestions de qualité, jamais "
                        "une publicité. Ne les cite PAS en bloc et n'en parle pas à chaque message : "
                        "mentionne seulement 1 à 3 liens (jamais toute la liste), avec l'URL exacte, "
                        "quand c'est réellement utile à la question de l'apprenant (s'entraîner, "
                        "approfondir, s'outiller, débloquer un sujet). Intègre-les naturellement en une "
                        "phrase courte. Si la question n'en a pas besoin, n'en parle pas ; ne les "
                        "favorise jamais de façon biaisée : choisis selon le besoin réel de l'apprenant."
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
        # Apprendre à connaître l'apprenant : on mémorise les informations qu'il
        # partage de lui-même (partagées entre tous les coachs).
        LearnerProfileService.extract_from(self.user, content)
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