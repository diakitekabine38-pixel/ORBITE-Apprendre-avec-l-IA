from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.tests import make_user

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_login_me_flow(self):
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

        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "nouveau", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn("access", login.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        me = self.client.get("/api/v1/auth/me/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["email"], "nouveau@orbite.test")

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

    def test_register_issues_token_and_sends_email(self):
        response = self._register()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="verif")
        self.assertFalse(user.email_verified)
        self.assertTrue(user.email_verification_token)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["verif@orbite.test"])
        self.assertIn("/verification-email/", email.body)

    def test_verify_email_success(self):
        user = make_user("verifuser")
        user.email_verification_token = "token123"
        user.save(update_fields=["email_verification_token"])
        response = self.client.get("/api/v1/auth/verify-email/token123/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.email_verified)
        self.assertEqual(user.email_verification_token, "")

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

    def test_resend_verification_authenticated(self):
        user = make_user("resend")
        response = self.client.post(
            "/api/v1/auth/resend-verification/",
            HTTP_AUTHORIZATION=f"Bearer {self._token(user)}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        user.refresh_from_db()
        self.assertTrue(user.email_verification_token)

    def test_resend_verification_rate_limited(self):
        user = make_user("resend2")
        auth = {"HTTP_AUTHORIZATION": f"Bearer {self._token(user)}"}
        first = self.client.post("/api/v1/auth/resend-verification/", **auth)
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        second = self.client.post("/api/v1/auth/resend-verification/", **auth)
        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_resend_verification_requires_auth(self):
        response = self.client.post("/api/v1/auth/resend-verification/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_resend_verification_when_already_verified(self):
        user = make_user("resend3")
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        response = self.client.post(
            "/api/v1/auth/resend-verification/",
            HTTP_AUTHORIZATION=f"Bearer {self._token(user)}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _token(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken

        return str(RefreshToken.for_user(user).access_token)


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