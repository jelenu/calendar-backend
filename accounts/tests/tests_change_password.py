from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@email.com",
            password="StrongPassword123!"
        )
        self.user.is_active = True
        self.user.save()

        self.change_password_url = reverse('change-password')

    def get_tokens_for_user(self):
        login_url = reverse('token_obtain_pair')
        data = {
            "email": "test@email.com",
            "password": "StrongPassword123!"
        }

        response = self.client.post(login_url, data)
        return response.data
    
    def test_change_password(self):
        tokens = self.get_tokens_for_user()
        access_token = tokens['access']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        data = {
            "old_password": "StrongPassword123!",
            "new_password": "NewStrongPassword123!"
        }
        
        response = self.client.post(self.change_password_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPassword123!"))

    def test_change_password_invalid_old_password(self):
        tokens = self.get_tokens_for_user()
        access_token = tokens['access']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        data = {
            "old_password": "WrongOldPassword!",
            "new_password": "NewStrongPassword123!"
        }
        
        response = self.client.post(self.change_password_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data['error'], "Incorrect current password")

    def test_change_password_unauthenticated(self):
        data = {
            "old_password": "StrongPassword123!",
            "new_password": "NewStrongPassword123!"
        }
        
        response = self.client.post(self.change_password_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_change_password_missing_old_password(self):
        tokens = self.get_tokens_for_user()
        access_token = tokens['access']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        data = {
            "new_password": "NewStrongPassword123!"
        }
        
        response = self.client.post(self.change_password_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_change_password_missing_new_password(self):
        tokens = self.get_tokens_for_user()
        access_token = tokens['access']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        data = {
            "old_password": "StrongPassword123!"
        }
        
        response = self.client.post(self.change_password_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

        
    