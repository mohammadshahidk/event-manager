from django.db import models
from attendees.models import Attendees
from django.utils import timezone

class Event(models.Model):
    """
    Represents an event with details such as name, location,
    start/end times, and maximum attendee capacity.
    """
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_capacity = models.PositiveIntegerField()
    
    
    def __str__(self):
        return f'{self.name} {self.location}'
    
    
class Registration(models.Model):
    """Join table for Event ↔ Attendee."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    attendee = models.ForeignKey(Attendees, on_delete=models.CASCADE, related_name="registrations")
    created_at = models.DateTimeField(default=timezone.now, editable=False)


    class Meta:
        unique_together = ("event", "attendee")
        ordering = ["-created_at"]


    def __str__(self):
        return f"{self.attendee.email} → {self.event.name}"
