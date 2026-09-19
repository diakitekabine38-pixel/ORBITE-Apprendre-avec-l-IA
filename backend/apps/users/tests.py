from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.tests import make_user


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