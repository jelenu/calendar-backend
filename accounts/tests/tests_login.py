from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()
class LoginViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="email@test.com",
            password="StrongPassword123!"
        )
        self.user.is_active = True
        self.user.save()

        self.login_url = reverse('token_obtain_pair')

    def test_login_success(self):
        data = {
            "email": "email@test.com",
            "password": "StrongPassword123!",
        }

        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        data = {
            "email": "email@test.com",
            "password": "StrongPassword123!",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_login_invalid_password(self):
        data = {
            "email": "email@test.com",
            "password": "aa!",
        }

        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_login_missing_fields(self):
        data = {
            "email": "",
            "password": "",
        }

        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)

    def test_login_non_existent_user(self):
        data = {
            "email": "invalid@email.com",
            "password": "StrongPassword123!",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

        