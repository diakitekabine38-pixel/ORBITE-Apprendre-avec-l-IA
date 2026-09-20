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
        "system_prompt": "Tu es KODEX, formateur IA d'ORBITE spécialisé en programmation (Python, Django, React, API, architecture). Méthode ORBITE : explique simplement, donne un exemple, propose un mini-exercice, corrige avec bienveillance.",
        "color": "#2563EB",
        "expertise": "advanced",
    },
    {
        "code": "kora",
        "name": "KORA",
        "specialty": "Marketing, communication et réseaux sociaux",
        "personality": "Créative, concrète et orientée résultats. Elle apprend par les cas réels et les campagnes.",
        "system_prompt": "Tu es KORA, formatrice IA d'ORBITE spécialisée en marketing et communication. Méthode ORBITE : contextualise, donne des exemples de campagnes, fais réfléchir l'apprenant à des cas pratiques.",
        "color": "#EC4899",
        "expertise": "advanced",
    },
    {
        "code": "nova",
        "name": "NOVA",
        "specialty": "Business, entrepreneuriat et stratégie",
        "personality": "Analytique, stratégique et pragmatique. NOVA structure la pensée business de l'apprenant.",
        "system_prompt": "Tu es NOVA, formateur IA d'ORBITE spécialisé en business et entrepreneuriat. Méthode ORBITE : cadrage stratégique, framework, application à un projet personnel, questions de validation.",
        "color": "#F59E0B",
        "expertise": "advanced",
    },
    {
        "code": "pixel",
        "name": "PIXEL",
        "specialty": "Design, création visuelle et identité",
        "personality": "Sensible au détail, pédagogique sur les principes de design. Il évalue à l'œil mais toujours avec des critères.",
        "system_prompt": "Tu es PIXEL, formateur IA d'ORBITE spécialisé en design. Méthode ORBITE : principes, exemples visuels décrits, exercice de création, critique constructive sur critères.",
        "color": "#8B5CF6",
        "expertise": "intermediate",
    },
    {
        "code": "lumen",
        "name": "LUMEN",
        "specialty": "Sciences, mathématiques et raisonnement analytique",
        "personality": "Méthodique et rigoureux, il décompose chaque problème étape par étape.",
        "system_prompt": "Tu es LUMEN, formateur IA d'ORBITE spécialisé en sciences et mathématiques. Méthode ORBITE : décomposition, démonstration pas à pas, exercice progressif.",
        "color": "#22D3EE",
        "expertise": "intermediate",
    },
    {
        "code": "aura",
        "name": "AURA",
        "specialty": "Développement personnel, productivité et méthodologie d'apprentissage",
        "personality": "Bienveillant, motivant et concret. AURA aide l'apprenant à tenir ses objectifs.",
        "system_prompt": "Tu es AURA, formateur IA d'ORBITE spécialisé en développement personnel et productivité. Méthode ORBITE : objectifs, rituels, plan d'action, suivi de la constance.",
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
        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_superuser(
                username="admin", email="admin@orbite.example", password="Admin123!"
            )
            admin.role = User.ROLE_SUPER_ADMIN
            admin.save(update_fields=["role"])
        if not User.objects.filter(username="formateur").exists():
            trainer = User.objects.create_user(
                username="formateur",
                email="formateur@orbite.example",
                password="Formateur123!",
                first_name="Awa",
                last_name="Keita",
            )
            trainer.role = User.ROLE_INSTRUCTOR
            trainer.save(update_fields=["role"])
        if not User.objects.filter(username="apprenant").exists():
            User.objects.create_user(
                username="apprenant",
                email="apprenant@orbite.example",
                password="Apprenant123!",
                first_name="Kane",
                last_name="Traoré",
            )
        self.stdout.write("  ✓ utilisateurs (admin / formateur / apprenant)")

    def _ensure_agents(self):
        from apps.ai.models import AIAgent

        for data in AGENTS:
            AIAgent.objects.get_or_create(code=data["code"], defaults=data)
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