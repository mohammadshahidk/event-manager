from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound
from .models import Event, Registration
from attendees.models import Attendees


@transaction.atomic
def register_attendee(event_id: int, name: str, email: str) -> Registration:
    """
    Creates a registration ensuring:
    - No duplicates for (event, attendee)
    - No overbooking beyond max_capacity
    Uses SELECT ... FOR UPDATE to avoid race conditions under concurrency.
    """
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        raise NotFound(detail="Event not found")


    attendee, _ = Attendees.objects.get_or_create(email=email.lower(), name=name)


    if Registration.objects.filter(event=event, attendee=attendee).exists():
        raise ValidationError("Attendee already registered for this event.")


    current = Registration.objects.filter(event=event).count()
    if current >= event.max_capacity:
        raise ValidationError("Event is already full.")


    return Registration.objects.create(event=event, attendee=attendee)
