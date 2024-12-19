# Event Management System Overview

Refactoring with 
1. [x] Flask blueprints, 
    - [x] auth - related to user management, authentication and so on
    - [x] events - related to events, new events, listing of events and event details
    - [x] api - RESTful api for access by other clients
2. [x] Flask-login, 
3. [x] Flask-sqlalchemy - implemented.
4. [x] Flask-WTForms

## 1. Code Structure
events_app/
│
├── app/
│   ├── __init__.py           # Initialize the Flask app and database
│   ├── models.py             # Database models (SQLAlchemy ORM)
│   ├── forms.py              # Flaskforms definitions for login, register... (WTForms / flask_wtforms)
│   ├── routes/
│   │   ├── __init__.py       # Register blueprints
│   │   ├── auth.py           # Authentication routes
│   │   ├── events.py         # Event management routes
│   │   ├── [ ]api.py            # API routes (e.g., AJAX validation)
│   └── services/
│       ├── __init__.py       # Utility functions
│       ├── db_utils.py       # Database operations (e.g., queries)
│       ├── auth_utils.py     # Authentication helpers
│
├── instance/
│   └── events.db            # SQLite database file (auto-generated)
│
├── templates/                # HTML templates
│   ├── base.html             # Base layout template
│   ├── home.html             # Home page
│   ├── login_signup.html     # Login/Signup page
│   ├── event_details.html    # Event details page
│   ├── user_owned_events.html
│   ├── user_registered_events.html
│
├── static/                   # Static files (CSS, JS, images)
│
├── README.md                 # Project overview and details (this document)
├── requirements.txt          # Python dependencies
├── run.py                    # Entry point for the application


## 1. User Management
- **User Registration**
  - [x] Users can sign up by providing necessary information (username, email, password).  
  - [ ] User roles can be defined (e.g., regular users and event organizers).
  - [ ] Credentials of other SM like google/github/... for signing on and logging in.

- **User Signup**
  - [x] Unique Username and unique email choice - incorporation of javascript to dynamically check and update avaiability of input username and email for new account.

- **User Authentication**
  - [x] Users can log in using their credentials.
  - [ ]Password recovery options for forgotten passwords.

- **User Profiles**
  - [ ] Users can view and edit their profiles.
  - [x] Users can see a history of events they have hosted and attended.

## 2. Event Management
- **Creating Events**
  - [x] Logged-in users can create new events. 
  - [ ] Event details include 
    - [x] title
    - [x] date and time in DateTime format
    - [x] location
    - [x] description
    - [ ] maximum capacity
    - [ ] categories.
  - [ ] Option to upload images or promotional material for the event.

- **Managing Events**
  - [ ] Event organizers can edit or delete their events.
  - [ ] Ability to view RSVP or registration statistics.
  - [ ] Manage attendees (e.g., sending updates or notifications).

## 3. Event Listing
- **Browse Events**
  - [x] Users can view a list of upcoming events, 
        - [ ] filtered by date, category, or location.
  - [ ] Search functionality for users to find specific events.
  
- **Event Details**
  - [x] Users can click on events to see detailed information, including date, location, description,
         - [] timing and a list of attendees.
  - [ ] Option to add events to personal calendars.

## 4. Registration and Participation
- **RSVP for Events**
  - [x] Users can sign up or RSVP for events they wish to attend.
    - [ ] RSVP
  - [ ] Option to leave comments or questions for the event organizer.

- **Notifications**
  - [ ] Users receive notifications or reminders for events they are attending.
  - [ ] Event organizers can send announcements to attendees.

## 5. Administrative Functions
- **User Management**
  - [ ] Admin can manage user accounts (approve, suspend, or delete accounts).
- **Event Oversight**
  - [ ] Admin can review and manage all events on the platform.
- **Reporting and Analytics**
  - [ ] Admin can access reports on user activity, event participation, and other metrics to help improve the platform.

## 6. Technology Stack
- **Frontend:**
  - [x] HTML, CSS and JavaScript.
- **Backend:**
  - [x] Flask for handling server-side logic.
  - [x] RESTful API for communication between frontend and backend.
- **Database:**
  - [x] SQLite for storing user and event data.
- **Authentication:**
  - [x] secure password by werkzeug tools
  - [ ] JWT (JSON Web Tokens) or session-based authentication for managing user sessions.

## 7. User Interface
- **Responsive Design**
  - [ ] Ensure the application is accessible on both desktop and mobile devices.
- **User-Friendly Navigation**
  - [ ] Intuitive layout for easy navigation between different sections of the application. (??)

## 8. Additional Features (Optional)
- **Social Media Integration**
  - [ ] Users can share events on social media platforms.
- **Payment Integration**
  - [ ] For paid events, integration with payment gateways for processing transactions.
- **Feedback and Reviews**
  - [ ] Users can leave feedback or reviews for events they attended.


