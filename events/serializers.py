from rest_framework import serializers
from .models import Event
from datetime import datetime, timezone as dt_timezone
from django.utils import timezone
from zoneinfo import ZoneInfo
from .utils import register_attendee
import re


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for the Event model.
    """
    
    class Meta:
        model = Event
        fields = "__all__"
        
    def validate(self, data):
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("End time must be after start time.")
        return data
    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        for field in ["start_time", "end_time"]:
            value = getattr(instance, field, None)
            if value:
                local_value = timezone.localtime(value)
                data[field] = local_value.strftime("%d/%m/%Y %I:%M %p")

        return data
        
    
class EventRegisterSerializer(serializers.Serializer):
    """
    Serializer for register an attendee to specific event.
    """
    name = serializers.CharField(
        max_length=100, min_length=2, allow_blank=True)
    email = serializers.EmailField(allow_blank=True)
    
    def validate_name(self, value):
        """
        Validate name field.
        """
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty or contain only whitespace.")
        
        if not re.match(r'^[a-zA-Z\s\-\']+$', value.strip()):
            raise serializers.ValidationError("Name can only contain letters, spaces, hyphens, and apostrophes.")
        
        return value
    
    def validate_email(self, value):
        """
        Validate email field
        """
        if not value.strip():
            raise serializers.ValidationError("Email cannot be empty")
        return value
    
    def create(self, validated_data):
        """
        Override create method
        """
        return register_attendee(
            event_id=self.context["event_id"],
            name=validated_data["name"],
            email=validated_data["email"],
        )