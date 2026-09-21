"""Seed ORBITE with the initial dataset (writers' agents, courses, coupons…).

Usage: python manage.py seed_orbite
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

User = get_user_model()

AGENTS = [
    {
        "code": "kodex",
        "name": "KODEX",
        "specialty": "Programmation et ingénierie logicielle",
        "personality": "Patient, technique, direct et pédagogique. Il explique avec des analogies et vérifie la compréhension avant de continuer.",
        "system_prompt": "Tu es KODEX, formateur IA d'ORBITE en programmation. Tu es sympa, patient et tu y vas doucement. Parle simplement, avec des analogies. Adapte ta réponse à la longueur du message : un « salut » reçoit une réponse chaleureuse de 1-2 phrases et une offre d'aide, pas un cours. Ne déverse jamais tout d'un coup : une idée à la fois, puis demande si c'est clair.",
        "teaching_rules": [
            "Répondre court et simple",
            "Une idée à la fois",
            "Utiliser des analogies",
            "Demander si c'est clair avant d'aller plus loin",
        ],
        "color": "#2563EB",
        "expertise": "advanced",
    },
    {
        "code": "kora",
        "name": "KORA",
        "specialty": "Marketing, communication et réseaux sociaux",
        "personality": "Créative, concrète et orientée résultats. Elle apprend par les cas réels et les campagnes.",
        "system_prompt": "Tu es KORA, formatrice IA d'ORBITE en marketing et communication. Tu es chaleureuse, encourageante et concrète. Réponds à la hauteur du message : un message court reçoit une réponse courte et simple, avec un exemple concret. Une idée à la fois, tu fais réfléchir l'apprenant et tu le félicites.",
        "teaching_rules": [
            "Toujours bienveillante",
            "Exemples concrets et courts",
            "Une idée à la fois",
            "Encourager l'apprenant",
        ],
        "color": "#EC4899",
        "expertise": "advanced",
    },
    {
        "code": "nova",
        "name": "NOVA",
        "specialty": "Business, entrepreneuriat et stratégie",
        "personality": "Analytique, stratégique et pragmatique. NOVA structure la pensée business de l'apprenant.",
        "system_prompt": "Tu es NOVA, formateur IA d'ORBITE en business et entrepreneuriat. Tu es enthousiaste mais simple : pas de long exposé. Adapte ta réponse au message : un message court reçoit une réponse courte et chaleureuse. Un framework à la fois, appliqué au projet de l'apprenant, puis une question de validation.",
        "teaching_rules": [
            "Simple et direct",
            "Une étape à la fois",
            "Poser une question pour valider",
            "Rester chaleureux",
        ],
        "color": "#F59E0B",
        "expertise": "advanced",
    },
    {
        "code": "pixel",
        "name": "PIXEL",
        "specialty": "Design, création visuelle et identité",
        "personality": "Sensible au détail, pédagogique sur les principes de design. Il évalue à l'œil mais toujours avec des critères.",
        "system_prompt": "Tu es PIXEL, formateur IA d'ORBITE en design. Tu es doux et encourageant, tu critiques toujours avec bienveillance. Réponds à la hauteur du message : un message court reçoit une réponse courte. Un principe à la fois, avec un exemple visuel décrit simplement, puis tu proposes un petit exercice créatif.",
        "teaching_rules": [
            "Court et encourageant",
            "Un principe à la fois",
            "Exemples visuels décrits",
            "Critique constructive et douce",
        ],
        "color": "#8B5CF6",
        "expertise": "intermediate",
    },
    {
        "code": "lumen",
        "name": "LUMEN",
        "specialty": "Sciences, mathématiques et raisonnement analytique",
        "personality": "Méthodique et rigoureux, il décompose chaque problème étape par étape.",
        "system_prompt": "Tu es LUMEN, formateur IA d'ORBITE en sciences et mathématiques. Tu expliques en douceur, sans intimider : pas de terme compliqué sans l'expliquer. Adapte ta réponse au message : un message court reçoit une réponse courte. Décompose pas à pas, un exercice progressif, tu rassures l'apprenant.",
        "teaching_rules": [
            "Pas à pas en douceur",
            "Décomposer simplement",
            "Exercice progressif",
            "Rassurer l'apprenant",
        ],
        "color": "#22D3EE",
        "expertise": "intermediate",
    },
    {
        "code": "aura",
        "name": "AURA",
        "specialty": "Développement personnel, productivité et méthodologie d'apprentissage",
        "personality": "Bienveillant, motivant et concret. AURA aide l'apprenant à tenir ses objectifs.",
        "system_prompt": "Tu es AURA, formateur IA d'ORBITE en développement personnel et productivité. Tu es chaleureux, motivant et concret : tu parles du ressenti de l'apprenant et tu le félicites. Réponds à la hauteur du message : un message court reçoit une réponse courte et réconfortante. Des petits pas concrets, un plan d'action simple, un suivi bienveillant.",
        "teaching_rules": [
            "Chaleureux et motivant",
            "Parler du ressenti",
            "Petits pas concrets",
            "Féliciter les progrès",
        ],
        "color": "#7C5CFF",
        "expertise": "intermediate",
    },
]

CATEGORIES = [
    ("Développement", "développement", "code"),
    ("Marketing", "marketing", "bullhorn"),
    ("Business", "business", "briefcase"),
    ("Design", "design", "pen-nib"),
    ("Intelligence Artificielle", "intelligence-artificielle", "brain"),
    ("Productivité", "productivite", "bolt"),
]

COURSES = {
    "développement": [
        {
            "title": "Django Full Stack — Du zéro au déploiement",
            "description": "Bâtis une application web complète avec Django, Django REST Framework et React, de la modélisation au déploiement.",
            "level": "intermediate",
            "price": 20000,
            "duration_hours": 24,
            "agent": "kodex",
            "modules": [
                {
                    "title": "Les fondamentaux Django",
                    "lessons": [
                        ("Modèles et migrations", "Crée tes premiers modèles et applique les migrations.", "Migrations"),
                        ("Vues et templates", "Comprends le cycle requête → vue → template → réponse.", "MVC"),
                        ("Django REST Framework", "Expose ta première API REST.", "DRF"),
                    ],
                },
                {
                    "title": "Application complète",
                    "lessons": [
                        ("Authentification API", "Sécurise tes endpoints avec JWT.", "JWT"),
                        ("React + Django", "Connecte un frontend React à l'API.", "React"),
                    ],
                },
            ],
        },
        {
            "title": "Python pour débutants",
            "description": "Les bases de la programmation en Python : variables, conditions, boucles, fonctions et projet final.",
            "level": "beginner",
            "price": 0,
            "duration_hours": 12,
            "agent": "kodex",
            "modules": [
                {
                    "title": "Premiers pas",
                    "lessons": [
                        ("Variables et types", "Les fondations du langage Python.", "Variables"),
                        ("Conditions et boucles", "Contrôle le flux de tes programmes.", "Boucles"),
                    ],
                }
            ],
        },
    ],
    "marketing": [
        {
            "title": "Marketing digital : la boîte à outils",
            "description": "Stratégie, réseaux sociaux, SEO et publicité payante pour lancer et développer une présence efficace.",
            "level": "beginner",
            "price": 15000,
            "duration_hours": 15,
            "agent": "kora",
            "modules": [
                {
                    "title": "Poser sa stratégie",
                    "lessons": [
                        ("Le socle de la stratégie marketing", "Définis ta cible et ton positionnement.", "Stratégie"),
                        ("Réseaux sociaux", "Crée un calendrier de contenu simple et efficace.", "Réseaux"),
                        ("SEO pour débutants", "Les réflexes de base du référencement.", "SEO"),
                    ],
                }
            ],
        }
    ],
    "business": [
        {
            "title": "Entreprendre en Afrique : du MVP au business model",
            "description": "Valide une idée, construis un business model simple et lance ton premier produit sans gros budget.",
            "level": "beginner",
            "price": 18000,
            "duration_hours": 10,
            "agent": "nova",
            "modules": [
                {
                    "title": "Construire son projet",
                    "lessons": [
                        ("Trouver et valider une idée", "De l'idée au problème réel à résoudre.", "Idéation"),
                        ("Le business model canvas", "Un cadre simple pour structurer ton offre.", "Canvas"),
                    ],
                }
            ],
        }
    ],
    "design": [
        {
            "title": "Design UI : les principes qui changent tout",
            "description": "Typographie, espace, couleur, hiérarchie : pose les bases d'un design propre et efficace.",
            "level": "beginner",
            "price": 12000,
            "duration_hours": 8,
            "agent": "pixel",
            "modules": [
                {
                    "title": "Les fondations visuelles",
                    "lessons": [
                        ("Hiérarchie et espace", "L'air, c'est du design.", "Hiérarchie"),
                        ("La couleur", "Construis une palette cohérente.", "Couleur"),
                    ],
                }
            ],
        }
    ],
}

QUIZZES = [
    {
        "title": "Test — Les variables en Python",
        "questions": [
            {
                "question_type": "mcq",
                "text": "Quel mot-clé déclare une variable en Python ?",
                "options": ["var", "let", "Aucun, l'affectation suffit", "dim"],
                "correct": ["Aucun, l'affectation suffit"],
                "points": 1,
            },
            {
                "question_type": "true_false",
                "text": "Le type de `3.14` est `int`.",
                "options": ["Vrai", "Faux"],
                "correct": ["Faux"],
                "points": 1,
            },
            {
                "question_type": "open",
                "text": "Explique en une phrase la différence entre une liste et un tuple.",
                "correct": ["mutable"],
                "points": 2,
            },
        ],
    }
]

SKILLS = [
    ("Python", "Backend", "Langage de programmation généraliste, base du backend ORBITE."),
    ("Django", "Backend", "Framework web Python : modèles, vues, API et sécurité."),
    ("REST API", "Backend", "Conception et consommation d'APIs REST (sérialisation, authentification)."),
    ("React", "Frontend", "Interface utilisateur : composants, hooks et état."),
    ("JavaScript", "Frontend", "Langage du web : ES6+, asynchrone et DOM."),
    ("UX / UI", "Design", "Expérience et interface utilisateur : hiérarchie, lisibilité, identité."),
    ("SEO", "Marketing", "Optimisation pour les moteurs de recherche et visibilité."),
    ("Business Model", "Business", "Modèle économique, valeur, canaux et monétisation."),
]


class Command(BaseCommand):
    help = "Initialise les données de base ORBITE (rôles, agents IA, catégories, formations, coupons)."

    @transaction.atomic
    def handle(self, *args, **options):
        self._ensure_users()
        self._ensure_agents()
        self._ensure_categories_and_courses()
        self._ensure_skills()
        self._ensure_coupons()
        self._ensure_payment_methods()
        self.stdout.write(self.style.SUCCESS("ORBITE : données de base créées ✓"))

    def _ensure_users(self):
        demos = [
            ("admin", "admin@orbite.example", "Admin123!"),
            ("formateur", "formateur@orbite.example", "Formateur123!"),
            ("apprenant", "apprenant@orbite.example", "Apprenant123!"),
        ]
        for username, email, password in demos:
            user = User.objects.filter(username=username).first()
            if user is None:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name={
                        "apprenant": "Kane",
                        "formateur": "Awa",
                        "admin": "Admin",
                    }[username],
                    last_name={"apprenant": "Traoré", "formateur": "Keita", "admin": "ORBITE"}[
                        username
                    ],
                )
            if username == "admin":
                user.is_staff = True
                user.is_superuser = True
            user.email = user.email or email
            user.email_verified = True
            user.email_verification_token = ""
            user.save(update_fields=["email", "email_verified", "email_verification_token", "is_staff", "is_superuser"])
        admin = User.objects.filter(username="admin").first()
        admin.role = User.ROLE_SUPER_ADMIN
        admin.save(update_fields=["role"])
        trainer = User.objects.filter(username="formateur").first()
        trainer.role = User.ROLE_INSTRUCTOR
        trainer.save(update_fields=["role"])
        self.stdout.write("  ✓ utilisateurs (admin / formateur / apprenant)")

    def _ensure_agents(self):
        from apps.ai.models import AIAgent

        for data in AGENTS:
            defaults = {k: v for k, v in data.items() if k != "code"}
            AIAgent.objects.update_or_create(code=data["code"], defaults=defaults)
        self.stdout.write("  ✓ agents IA")

    def _ensure_categories_and_courses(self):
        from apps.ai.models import AIAgent
        from apps.assessments.models import Exercise, Question, Quiz
        from apps.courses.models import Category, Course, Lesson, Module, Video

        for name, slug, icon in CATEGORIES:
            Category.objects.get_or_create(slug=slug, defaults={"name": name, "icon": icon})

        trainer = User.objects.filter(role=User.ROLE_INSTRUCTOR).first()
        for cat_slug, courses in COURSES.items():
            category = Category.objects.get(slug=cat_slug)
            for cdata in courses:
                course, created = Course.objects.get_or_create(
                    slug=cdata["title"].lower().replace(" ", "-").replace(":", ""),
                    defaults={
                        "title": cdata["title"],
                        "description": cdata["description"],
                        "short_description": cdata["description"][:120],
                        "category": category,
                        "instructor": trainer,
                        "ai_mentor": AIAgent.objects.get(code=cdata["agent"]),
                        "level": cdata["level"],
                        "price": cdata["price"],
                        "is_free": cdata["price"] == 0,
                        "duration_hours": cdata["duration_hours"],
                        "status": Course.STATUS_PUBLISHED,
                        "published_at": timezone.now(),
                    },
                )
                if not created:
                    continue
                for module_order, mdata in enumerate(cdata["modules"], start=1):
                    module = Module.objects.create(
                        course=course, title=mdata["title"], order=module_order
                    )
                    for lesson_order, (ltitle, lsummary, video_title) in enumerate(
                        mdata["lessons"], start=1
                    ):
                        video = Video.objects.create(
                            title=f"{video_title} — {course.title}",
                            duration_seconds=max(300, lesson_order * 420),
                            provider="s3",
                            storage_key=f"courses/{course.slug}/{lesson_order}.mp4",
                            hls_url=f"https://storage.orbite.example/courses/{course.slug}/{lesson_order}/index.m3u8",
                        )
                        lesson = Lesson.objects.create(
                            module=module,
                            title=ltitle,
                            summary=lsummary,
                            content=f"Contenu pédagogique de la leçon « {ltitle} » — {lsummary}",
                            video_meta=video,
                            order=lesson_order,
                            estimated_minutes=7,
                        )
                        if lesson_order == 1 and created:
                            lesson.is_free_preview = True
                            lesson.save(update_fields=["is_free_preview"])
                    # One quiz + one exercise on the first lesson
                    first_lesson = module.lessons.first()
                    quiz, _ = Quiz.objects.get_or_create(
                        lesson=first_lesson,
                        title=f"Mini-évaluation — {module.title}",
                        defaults={"pass_score": 50, "time_limit_minutes": 10},
                    )
                    for qdata in QUIZZES[0]["questions"]:
                        Question.objects.get_or_create(
                            quiz=quiz, text=qdata["text"], defaults=qdata
                        )
                    Exercise.objects.get_or_create(
                        lesson=first_lesson,
                        title=f"Exercice pratique — {mdata['title']}",
                        defaults={
                            "instructions": f"Applique les notions de « {mdata['title']} » à un cas concret de ton choix et décris ta démarche.",
                            "exercise_type": Exercise.TYPE_TEXT,
                        },
                    )
                self.stdout.write(f"  ✓ formation : {course.title}")

    def _ensure_skills(self):
        from apps.learning.models import Skill

        for skill_name, category, description in SKILLS:
            Skill.objects.update_or_create(
                slug=skill_name.lower().replace(" ", "-"),
                defaults={"name": skill_name, "category": category, "description": description},
            )
        self.stdout.write("  ✓ compétences")

    def _ensure_coupons(self):
        from apps.commerce.models import Coupon

        Coupon.objects.get_or_create(
            code="ORBIT10",
            defaults={"discount_type": Coupon.DISCOUNT_PERCENT, "value": 10},
        )
        Coupon.objects.get_or_create(
            code="KWEB50",
            defaults={"discount_type": Coupon.DISCOUNT_PERCENT, "value": 50},
        )
        self.stdout.write("  ✓ coupons (ORBIT10, KWEB50)")

    def _ensure_payment_methods(self):
        from apps.payments.models import PaymentMethod

        PaymentMethod.objects.get_or_create(code="manual", defaults={"name": "Vérification manuelle"})
        PaymentMethod.objects.get_or_create(
            code="orange_money", defaults={"name": "Orange Money", "is_active": True}
        )
        self.stdout.write("  ✓ moyens de paiement")