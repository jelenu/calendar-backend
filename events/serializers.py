from rest_framework import serializers
from .models import Event, Category

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'user', 'createdAt']

    def validate(self, data):
        start = data.get('startDate')
        end = data.get('endDate')
        if start and end and start > end:
            raise serializers.ValidationError("The start date cannot be greater than the end date.")
        return data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']