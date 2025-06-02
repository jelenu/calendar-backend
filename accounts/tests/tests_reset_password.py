from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class ResetPasswordTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@email.com",
            password="StrongPassword123!"
        )
        self.user.is_active = True
        self.user.save()
        

        self.reset_password_url = reverse('reset-password')
        
    def test_reset_password_request(self):
        data = {
            "email": "test@email.com"
        }
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_request_non_existent_user(self):
        data = {
            "email": "fail@email.com"
        }
        response = self.client.post(self.reset_password_url, data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("msg", response.data)

    def test_reset_password_confirm(self):
        data = {
            "email": "test@email.com"
        }
        response = self.client.post(self.reset_password_url, data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        token = default_token_generator.make_token(self.user)
        confirm_url = reverse('reset-password-confirm', kwargs={'uidb64': uid, 'token': token})
        confirm_data = {
            "password": "NewStrongPassword123!"
        }
        response = self.client.post(confirm_url, confirm_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPassword123!"))

    def test_reset_password_confirm_invalid_token(self):
        data = {
            "email": "test@email.com"
        }
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        invalid_token= "invalid_token"
        confirm_url = reverse('reset-password-confirm', kwargs={'uidb64': uid, 'token': invalid_token})
        confirm_data = {
            "password": "NewStrongPassword123!"
        }
        response = self.client.post(confirm_url, confirm_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_reset_password_confirm_invalid_uid(self):
        invalid_uid = "invalid_uid"
        token = default_token_generator.make_token(self.user)
        confirm_url = reverse('reset-password-confirm', kwargs={'uidb64': invalid_uid, 'token': token})
        confirm_data = {
            "password": "NewStrongPassword123!"
        }
        response = self.client.post(confirm_url, confirm_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("Invalid token", response.data["error"])
    
    def test_reset_password_confirm_no_password(self):
        data = {
            "email": "test@email.com"
        }
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        confirm_url = reverse('reset-password-confirm', kwargs={'uidb64': uid, 'token': token})
        confirm_data = {
            "password": ""
        }
        response = self.client.post(confirm_url, confirm_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    
    def test_reset_password_confirm_week_password(self):
        data = {
            "email": "test@email.com"
        }
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        confirm_url = reverse('reset-password-confirm', kwargs={'uidb64': uid, 'token': token})
        confirm_data = {
            "password": "12345"
        }
        response = self.client.post(confirm_url, confirm_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    