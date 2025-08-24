Mini Event Management System

---

# Setup Instructions

1. Clone the Repository

git clone https://github.com/mohammadshahidk/event-manager.git
cd event-manager

2. Create and Activate Virtual Environment

use 'python -m venv venv' or 'mkvirtualenv event'

3. Install Dependencies

pip install -r requirements.txt

4. Database Setup

The project uses SQLite (default Django DB).

A pre-configured event_manager.sqlite3 file is included in the repo for convenience.

-> If you want to start fresh:

python manage.py migrate

5. Run the Server

python manage.py runserver

# Assumptions

All event times are stored in UTC internally.

Client must pass a Timezone header (e.g., Asia/Kolkata, America/New_York) for conversion when listing/creating events.

If no timezone is provided, defaults to Asia/Kolkata.

# API Documentation

Swagger/OpenAPI is enabled.
Access it at: http://127.0.0.1:8000/swagger/

# A Postman Collection is provided in the repo:

Event manager.postman_collection.json

# Running Tests

pytest
