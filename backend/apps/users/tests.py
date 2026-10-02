from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.tests import make_user

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_is_immediately_active_and_logged_in(self):
        register = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "nouveau",
                "email": "nouveau@orbite.test",
                "first_name": "Aminata",
                "last_name": "Diallo",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(register.status_code, status.HTTP_201_CREATED)
        self.assertEqual(register.data["role"], "student")
        self.assertIn("access", register.data, "connexion immédiate attendue")
        self.assertIn("refresh", register.data)

        user = User.objects.get(username="nouveau")
        self.assertTrue(user.is_active, "l'inscription active directement le compte")
        self.assertTrue(user.email_verified, "pas de phase de vérification par email")
        self.assertEqual(user.email_verification_token, "")

        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "nouveau", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn("access", login.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {register.data['access']}")
        me = self.client.get("/api/v1/auth/me/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["email"], "nouveau@orbite.test")
        self.assertTrue(me.data["email_verified"])

    def test_registration_password_mismatch(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "x",
                "email": "x@orbite.test",
                "first_name": "A",
                "last_name": "B",
                "password": "StrongPass123!",
                "password2": "different1!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_rejected(self):
        first = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "doublon1",
                "email": "meme@orbite.test",
                "first_name": "Awa",
                "last_name": "Première",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "doublon2",
                "email": "meme@orbite.test",
                "first_name": "Binta",
                "last_name": "Seconde",
                "password": "AutrePass123!",
                "password2": "AutrePass123!",
            },
            format="json",
        )
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", second.data)
        users = User.objects.filter(email__iexact="meme@orbite.test")
        self.assertEqual(users.count(), 1)
        self.assertEqual(users.first().username, "doublon1")

    def test_verified_email_blocks_new_registration(self):
        user = make_user("confirme")
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "intrus",
                "email": user.email,
                "first_name": "A",
                "last_name": "B",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_change_password(self):
        user = make_user("kane")
        self.client.force_authenticate(user)
        response = self.client.post(
            "/api/v1/auth/change-password/",
            {"old_password": "TestPass123!", "new_password": "NouveauPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NouveauPass123!"))

    def test_anonymous_me_forbidden(self):
        self.client.credentials()
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EmailVerificationTests(APITestCase):
    REGISTER = {
        "username": "verif",
        "email": "verif@orbite.test",
        "first_name": "Awa",
        "last_name": "Diallo",
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
    }

    def setUp(self):
        # TestCase flush la DB entre les tests mais pas le cache LocMem :
        # les ids utilisateurs repartent de 1 et fausseraient le rate-limit.
        from django.core.cache import cache

        cache.clear()

    def _register(self):
        return self.client.post("/api/v1/auth/register/", self.REGISTER, format="json")

    def test_register_issue_immediat_active_verified_no_email(self):
        response = self._register()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="verif")
        self.assertTrue(user.email_verified, "pas de phase de vérification par email")
        self.assertTrue(user.is_active, "le compte est actif dès l'inscription")
        self.assertEqual(user.email_verification_token, "")
        self.assertEqual(len(mail.outbox), 0, "aucun email de vérification envoyé")
        self.assertIn("access", response.data, "connexion immédiate attendue")

    def test_verify_email_success(self):
        user = make_user("verifuser")
        user.is_active = False
        user.save(update_fields=["is_active"])
        user.email_verification_token = "token123"
        user.save(update_fields=["email_verification_token"])
        response = self.client.get("/api/v1/auth/verify-email/token123/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.email_verified)
        self.assertTrue(user.is_active, "la vérification rend le compte actif")
        self.assertEqual(user.email_verification_token, "")
        self.assertIn("access", response.data, "connexion immédiate attendue")
        self.assertIn("refresh", response.data)
        me = self.client.get(
            "/api/v1/auth/me/",
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}",
        )
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["email"], user.email)

    def test_verify_email_invalid_token(self):
        response = self.client.get("/api/v1/auth/verify-email/nope/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_idempotent_token_cleared(self):
        user = make_user("verif2")
        user.email_verification_token = "token456"
        user.save(update_fields=["email_verification_token"])
        self.client.get("/api/v1/auth/verify-email/token456/")
        response = self.client.get("/api/v1/auth/verify-email/token456/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resend_sends_to_existing_unverified_email(self):
        user = make_user("resend")
        user.email_verified = False
        user.save(update_fields=["email_verified"])
        response = self.client.post(
            "/api/v1/auth/resend-verification/",
            {"email": user.email},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        user.refresh_from_db()
        self.assertTrue(user.email_verification_token)

    def test_resend_unknown_email_does_not_leak(self):
        response = self.client.post(
            "/api/v1/auth/resend-verification/",
            {"email": "inconnu@orbite.test"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0, "aucun email, aucune révélation")

    def test_resend_verified_email_does_not_send(self):
        user = make_user("resend3")
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        response = self.client.post(
            "/api/v1/auth/resend-verification/",
            {"email": user.email},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)

    def test_resend_rate_limited(self):
        user = make_user("resend2")
        user.email_verified = False
        user.save(update_fields=["email_verified"])
        self.client.post(
            "/api/v1/auth/resend-verification/", {"email": user.email}, format="json"
        )
        self.client.post(
            "/api/v1/auth/resend-verification/", {"email": user.email}, format="json"
        )
        # Réponse toujours 200, mais un seul email émis (rate-limit 60s).
        self.assertEqual(len(mail.outbox), 1)


class ProfileAndRolesTests(APITestCase):
    def test_profile_roundtrip(self):
        user = make_user("profil")
        self.client.force_authenticate(user)
        response = self.client.patch(
            "/api/v1/users/profile/me/",
            {"bio": "J'apprends Django", "language": "fr"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.bio, "J'apprends Django")

    def test_roles_are_registered(self):
        super_admin = make_user("root", role="super_admin")
        self.client.force_authenticate(super_admin)
        response = self.client.get("/api/v1/users/roles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = {entry["code"] for entry in response.data["results"]}
        self.assertTrue({"student", "instructor", "admin", "super_admin"} <= names)