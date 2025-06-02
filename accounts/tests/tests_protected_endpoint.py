from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class ProtectedEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@email.com",
            password="StrongPassword123!"
        )
        self.user.is_active = True
        self.user.save()

        self.protected_url = reverse('protected')
    
    def get_tokens_for_user(self):
        login_url = reverse('token_obtain_pair')
        data = {
            "email": "test@email.com",
            "password": "StrongPassword123!"
        }
        response = self.client.post(login_url, data)
        return response.data
    
    def test_protected_endpoint_access(self):
        tokens = self.get_tokens_for_user()
        access_token = tokens['access']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.get(self.protected_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("msg", response.data)

    def test_protected_endpoint_no_auth(self):
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_protected_endpoint_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'invalid_token')
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


