import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from events.models import Event, Registration
from attendees.models import Attendees
from django.utils import timezone
from datetime import timedelta


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_event(db):
    return Event.objects.create(
        name="Pycon India 2025",
        location="Bangalore",
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=2),
        max_capacity=2,
    )


@pytest.fixture
def past_event(db):
    return Event.objects.create(
        name="Tech Conference",
        location="Delhi",
        start_time=timezone.now() - timedelta(days=2),
        end_time=timezone.now() - timedelta(days=1),
        max_capacity=50,
    )


@pytest.mark.django_db
def test_create_event(api_client):
    url = reverse("event-list-create")
    data = {
        "name": "Music Fest",
        "location": "Mumbai",
        "start_time": (timezone.now() + timedelta(days=5)).isoformat(),
        "end_time": (timezone.now() + timedelta(days=6)).isoformat(),
        "max_capacity": 100,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Event.objects.count() == 1




@pytest.mark.django_db
def test_list_upcoming_events(api_client, sample_event, past_event):
    url = reverse("event-list-create")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == sample_event.name


@pytest.mark.django_db
def test_event_timezone_conversion(api_client):
    url = reverse("event-list-create")
    data = {
        "name": "Timezone Management Event",
        "location": "New York",
        "start_time": "2025-09-25T10:20:00",
        "end_time": "2025-09-25T12:20:00",
        "max_capacity": 100,
    }
    headers = {"HTTP_Timezone": "America/New_York"}

    response = api_client.post(url, data, format="json", **headers)
    assert response.status_code == status.HTTP_201_CREATED

    fetch_url = reverse("event-list-create")
    headers_ist = {"HTTP_Timezone": "Asia/Kolkata"}
    response = api_client.get(fetch_url, **headers_ist, format="json")

    assert response.status_code == status.HTTP_200_OK
    returned_start_time = response.data['results'][0]["start_time"]

    # 10:20 AM New York (EDT) → 07:50 PM IST
    expected_ist = "25/09/2025 07:50 PM"
    assert returned_start_time == expected_ist


@pytest.mark.django_db
def test_register_attendee(api_client, sample_event):
    url = reverse("register-attendees", kwargs={"event_id": sample_event.id})
    data = {"name": "Albin", "email": "albin@email.com"}
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Registration.objects.count() == 1
    assert Attendees.objects.count() == 1


@pytest.mark.django_db
def test_register_attendee_event_not_found(api_client):
    url = reverse("register-attendees", kwargs={"event_id": 1500})
    data = {"name": "Albin", "email": "albin@email.com"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Event not found" in str(response.data)


@pytest.mark.django_db
def test_prevent_duplicate_registration(api_client, sample_event):
    url = reverse("register-attendees", kwargs={"event_id": sample_event.id})
    data = {"name": "Albin", "email": "albin@email.com"}
    api_client.post(url, data, format="json")
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in str(response.data).lower()


@pytest.mark.django_db
def test_prevent_overbooking(api_client, sample_event):
    url = reverse("register-attendees", kwargs={"event_id": sample_event.id})

    api_client.post(
        url,
        {"name": "Attendeeone", "email": "attendeeone@email.com"},
        format="json")
    api_client.post(
        url,
        {"name": "Attendeetwo", "email": "attendeetwo@email.com"},
        format="json")
    response = api_client.post(
        url,
        {"name": "Attendeethree", "email": "attendeethree@email.com"},
        format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "full" in str(response.data).lower()


@pytest.mark.django_db
def test_get_attendees(api_client, sample_event):
    url_register = reverse("register-attendees", kwargs={"event_id": sample_event.id})
    api_client.post(url_register, {"name": "Babu", "email": "babu@email.com"}, format="json")

    url_attendees = reverse("event-attendees", kwargs={"event_id": sample_event.id})
    response = api_client.get(url_attendees)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["email"] == "babu@email.com"


@pytest.mark.django_db
def test_get_attendees_event_not_found(api_client):
    url = reverse("event-attendees", kwargs={"event_id": 99999})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Event not found" in str(response.data)


@pytest.mark.django_db
def test_register_attendee_missing_required_fields(api_client, sample_event):
    url = reverse("register-attendees", kwargs={"event_id": sample_event.id})
    
    # Test missing name
    response = api_client.post(url, {"email": "test@example.com"}, format="json")
    print(str(response.data))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Test missing email
    response = api_client.post(url, {"name": "Test User"}, format="json")
    print(str(response.data))
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_attendee_invalid_email_format(api_client, sample_event):
    url = reverse("register-attendees", kwargs={"event_id": sample_event.id})
    data = {"name": "Test User", "email": "invalid-email"}
    response = api_client.post(url, data, format="json")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Enter a valid email address" in str(response.data)




@pytest.mark.django_db
def test_register_attendee_empty_email(api_client, sample_event):
    url = reverse("register-attendees", kwargs={"event_id": sample_event.id})
    
    # Test empty email
    data = {"name": "Test User", "email": ""}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email cannot be empty" in str(response.data)
    
    # Test whitespace-only email
    data = {"name": "Test User", "email": "   "}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email cannot be empty" in str(response.data)


@pytest.mark.django_db
def test_register_attendee_invalid_name(api_client, sample_event):
    url = reverse("register-attendees", kwargs={"event_id": sample_event.id})
    
   
    data = {"name": "Jose123", "email": "jose@email.com"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Name can only contain letters" in str(response.data)
    
    data = {"name": "   ", "email": "jose@email.com"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Name cannot be empty or contain only whitespace' in str(response.data)


@pytest.mark.django_db
def test_create_event_missing_required_fields(api_client):
    url = reverse("event-list-create")
    
    # Test missing name
    data = {
        "location": "Mumbai",
        "start_time": (timezone.now() + timedelta(days=5)).isoformat(),
        "end_time": (timezone.now() + timedelta(days=6)).isoformat(),
        "max_capacity": 100,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_event_invalid_dates(api_client):
    url = reverse("event-list-create")
    
    # Test end_time before start_time
    data = {
        "name": "Invalid Event",
        "location": "Mumbai",
        "start_time": (timezone.now() + timedelta(days=6)).isoformat(),
        "end_time": (timezone.now() + timedelta(days=5)).isoformat(),
        "max_capacity": 100,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "End time must be after start time" in str(response.data)


@pytest.mark.django_db
def test_register_same_attendee_different_events(api_client, sample_event):
    event2 = Event.objects.create(
        name="Another Conference",
        location="Chennai",
        start_time=timezone.now() + timedelta(days=3),
        end_time=timezone.now() + timedelta(days=4),
        max_capacity=5,
    )
    
    attendee_data = {"name": "Same Person", "email": "same@example.com"}
    
    
    url1 = reverse("register-attendees", kwargs={"event_id": sample_event.id})
    response1 = api_client.post(url1, attendee_data, format="json")
    assert response1.status_code == status.HTTP_201_CREATED
    
    url2 = reverse("register-attendees", kwargs={"event_id": event2.id})
    response2 = api_client.post(url2, attendee_data, format="json")
    assert response2.status_code == status.HTTP_201_CREATED
    
    assert Registration.objects.count() == 2
    assert Attendees.objects.count() == 1

