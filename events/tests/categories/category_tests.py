from accounts.models import CustomUser
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from events.models import Category
from rest_framework_simplejwt.tokens import RefreshToken

class CategoryTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='testuser@example.com', password='testpass123', is_active=True)
        self.user2 = CustomUser.objects.create_user(email='otheruser@example.com', password='testpass123', is_active=True)
        self.url = reverse('category-list')
        self.category = Category.objects.create(name="Personal", color="#123456", user=self.user)

    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_create_category_authenticated(self):
        access_token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(self.url, {"name": "Trabajo", "color": "#abcdef"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.filter(user=self.user).count(), 2)

    def test_create_category_unauthenticated(self):
        response = self.client.post(self.url, {"name": "Trabajo", "color": "#abcdef"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_category_invalid_color(self):
        access_token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(self.url, {"name": "Trabajo", "color": "red"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('color', response.data)

    def test_list_categories_authenticated(self):
        access_token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        categories = response.data if isinstance(response.data, list) else response.data['results']
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0]['name'], self.category.name)
        self.assertEqual(categories[0]['color'], self.category.color)

    def test_list_categories_unauthenticated(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_category(self):
        access_token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.patch(url, {"name": "Updated", "color": "#654321"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated")
        self.assertEqual(self.category.color, "#654321")

    def test_update_category_invalid_color(self):
        access_token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.patch(url, {"color": "nothex"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('color', response.data)

    def test_delete_category(self):
        access_token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())

    def test_cannot_access_others_category(self):
        access_token = self.get_token_for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)