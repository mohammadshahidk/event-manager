from django.urls import path
from .views import *


urlpatterns = [
    path('', EventListCreateView.as_view(), name='event-list-create'),
    path('<int:event_id>/register', EventRegisteView.as_view(), name='register-attendees'),
    path('<int:event_id>/attendees', EventAttendeesListView.as_view(), name='event-attendees')
]