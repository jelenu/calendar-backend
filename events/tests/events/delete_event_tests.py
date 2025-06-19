from accounts.models import CustomUser
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from events.models import Event, Category
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import datetime

class DeleteEventTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='testuser@example.com', password='testpass123', is_active=True)
        self.user2 = CustomUser.objects.create_user(email='testuser2@example.com', password='testpass123', is_active=True)
        self.category = Category.objects.create(name="Initial Category", user=self.user)
        start = timezone.make_aware(datetime.datetime(2025, 6, 17, 10, 0, 0))
        end = timezone.make_aware(datetime.datetime(2025, 6, 17, 12, 0, 0))
        self.event = Event.objects.create(
            title="Initial Event",
            description="Initial Description",
            startDate=start,
            endDate=end,
            category=self.category,
            user=self.user
        )
        self.url = reverse('event-detail', kwargs={'pk': self.event.pk})

    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def test_delete_event_authenticated(self):
        access_token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.delete(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), 0)

    def test_delete_event_unauthenticated(self):
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_event_not_owner(self):
        access_token = self.get_token_for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.delete(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Event.objects.count(), 1)

    def test_delete_event_non_existent(self):
        non_existent_url = reverse('event-detail', kwargs={'pk': 9999})
        access_token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.delete(non_existent_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Event.objects.count(), 1)

