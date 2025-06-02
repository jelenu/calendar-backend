from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class TokenRefreshViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@email.com",
            password="StrongPassword123!"
        )
        self.user.is_active = True
        self.user.save()

        self.refresh_url = reverse('token_refresh')

    def get_tokens_for_user(self):
        login_url = reverse('token_obtain_pair')
        data = {
            "email": "test@email.com",
            "password": "StrongPassword123!"
        }
        response = self.client.post(login_url, data)
        return response.data

    def test_token_refresh_success(self):
        tokens = self.get_tokens_for_user()
        refresh_token = tokens['refresh']
        response = self.client.post(self.refresh_url, {"refresh": refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_refresh_invalid_token(self):
        response = self.client.post(self.refresh_url, {"refresh": "invalid_token"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_token_refresh_missing_field(self):
        response = self.client.post(self.refresh_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh", response.data)

        