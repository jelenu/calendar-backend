from rest_framework import serializers
from .models import Event, Category
import re

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

HEX_COLOR_REGEX = r'^#(?:[0-9a-fA-F]{3}){1,2}$'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'color']
        read_only_fields = ['id']

    def validate_color(self, value):
        if not re.match(HEX_COLOR_REGEX, value):
            raise serializers.ValidationError("Invalid color format. Please use a hex color code.")
        return value