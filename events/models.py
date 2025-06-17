from django.db import models
import uuid
from django.conf import settings

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    category = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clients"
    )
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
