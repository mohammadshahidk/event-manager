from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from .models import Event
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from attendees.models import Attendees
from django.utils import timezone
from .serializers import EventSerializer, EventRegisterSerializer
from attendees.serializers import AttendeeSerializer
from .utils import register_attendee


@extend_schema(
    tags=["Events"],
    parameters=[
        OpenApiParameter(
            name='Timezone',
            location=OpenApiParameter.HEADER,
            description='Client timezone (e.g., Asia/Kolkata, UTC, America/New_York). '
                        'If provided, event times will be converted before returning.',
            required=False,
            type=str
        )
    ],
    responses={
        200: OpenApiResponse(
            response=EventSerializer(many=True),
            description="List of upcoming events."
        ),
        201: OpenApiResponse(
            response=EventSerializer,
            description="Event created successfully."
        ),
    }
)
class EventListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating events.
    """
    serializer_class = EventSerializer
    
    def get_queryset(self):
        if self.request.method == 'GET':
             return Event.objects.filter(
               start_time__gte=timezone.now()).order_by('start_time')
        return Event.objects.all()
    

@extend_schema(
    tags=["Event Registration"],
    request=EventRegisterSerializer,
    responses={
        201: OpenApiResponse(
            description="Attendee successfully registered for the event.",
            response={
                "message": "Registration successful"
            }
        ),
        400: OpenApiResponse(
            description="Validation error"
        ),
        404: OpenApiResponse(
            description="Event not found."
        )
    }
)
class EventRegisteView(generics.GenericAPIView):
    """
    API endpoint to **register an attendee for an event**.
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
        

@extend_schema(
    tags=["Event Attendees"],
    responses={
        200: OpenApiResponse(
            response=AttendeeSerializer(many=True),
            description="List of attendees registered for the given event."
        ),
        404: OpenApiResponse(
            description="Event not found."
        )
    }
)
class EventAttendeesListView(generics.ListAPIView):
    """
    API endpoint to **list all attendees for a given event**.
    """
    serializer_class = AttendeeSerializer
    
    def get_queryset(self):
        event_id = self.kwargs["event_id"]
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise NotFound("Event not found")
        return Attendees.objects.filter(registrations__event_id=event_id).distinct()
    
    
    
    
    
    
    