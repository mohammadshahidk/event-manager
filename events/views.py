from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from .models import Event
from drf_spectacular.utils import extend_schema, OpenApiParameter
from attendees.models import Attendees
from django.utils import timezone
from .serializers import EventSerializer, EventRegisterSerializer
from attendees.serializers import AttendeeSerializer
from .utils import register_attendee


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='Timezone',
            location=OpenApiParameter.HEADER,
            description='Client timezone (e.g. Asia/Kolkata, UTC, America/New_York)',
            required=False,
            type=str
        )
    ]
)
class EventListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating events.

    - **GET**: Returns upcoming events where `start_time` is greater than or equal to the current time.
      - Accepts an optional `TimeZone` header. If provided, `start_time` and `end_time`
        fields will be converted to the specified timezone before being returned.
        
    - **POST**: Creates a new event.
      - Event times provided in the request body are assumed to be in the given `TimeZone`
        (defaults to `Asia/Kolkata` if not provided).
      - The times are stored in UTC internally.
    """
    serializer_class = EventSerializer
    
    def get_queryset(self):
        if self.request.method == 'GET':
             return Event.objects.filter(start_time__gte=timezone.now()).order_by('start_time')
        return Event.objects.all()
    

class EventRegisteView(generics.GenericAPIView):
    """
    API endpoint to **register an attendee for an event**.

    - **POST**: Registers a new attendee for the given `event_id`.
      Requires `name` and `email` in the request body.
      Returns success message if registration is successful, 
      otherwise returns an error message.
    """
    serializer_class = EventRegisterSerializer
    
    def post(self, request, event_id):
        serializer = self.get_serializer(
            data=request.data,
            context={"event_id": event_id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Registration successful"},
            status=status.HTTP_201_CREATED)
        

class EventAttendeesListView(generics.ListAPIView):
    """
    API endpoint to **list all attendees for a given event**.

    - **GET**: Returns a list of attendees who have registered for the event
      specified by `event_id` in the URL.
      Ensures unique attendees using `.distinct()`.
    """
    serializer_class = AttendeeSerializer
    
    def get_queryset(self):
        event_id = self.kwargs["event_id"]
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise NotFound("Event not found")
        return Attendees.objects.filter(registrations__event_id=event_id).distinct()
    
    
    
    
    
    
    