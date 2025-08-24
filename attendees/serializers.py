from rest_framework import serializers
from .models import Attendees


class AttendeeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Attendee model.
    """
    
    class Meta:
        model = Attendees
        fields = "__all__"