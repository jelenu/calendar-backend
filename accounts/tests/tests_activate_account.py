from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class ActivateAccountViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="email@test.com",
            password="StrongPassword123!",
            is_active=False 
        )
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        self.url = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})

    def test_activate_account_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("msg", response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activate_account_invalid_uuid_and_token(self):
        invalid_url = reverse('activate', kwargs={'uidb64': 'invalid_uid', 'token': 'invalid_token'})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_activate_account_already_active(self):
        self.user.is_active = True
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data) 

    