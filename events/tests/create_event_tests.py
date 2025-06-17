from accounts.models import CustomUser
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from events.models import Event
from rest_framework_simplejwt.tokens import RefreshToken


class EventCreateTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='testuser@example.com', password='testpass123', is_active=True)
        self.url = reverse('event-list')
        self.event_data = {
            "title": "Test Event",
            "description": "Test Description",
            "startDate": "2025-06-17T10:00:00Z",
            "endDate": "2025-06-17T12:00:00Z",
            "category": "Test Category"
        }

    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_create_event_authenticated(self):
        access_token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(self.url, self.event_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)

        event = Event.objects.first()
        self.assertEqual(event.title, self.event_data['title'])
        self.assertEqual(event.user, self.user)

    def test_create_event_unauthenticated(self):
        response = self.client.post(self.url, self.event_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
