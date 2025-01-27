# Event Management System Overview

Refactoring with 
1. [x] Flask blueprints, 
    - [x] amdin - admin 
    - [x] auth - related to user management, authentication and so on
    - [x] events - related to events, new events, listing of events and event details
    - [x] api - RESTful api for access by other clients
2. [x] Flask-login, 
3. [x] OAuth 2.0
    - [x] Refactoring of database usign Flask Migrate to enable additional type (google oauth) of users
    - [x] Google OAuth 2.0 integration
    - [x] Separation of sensitive info into .env files

4. [x] Flask-sqlalchemy - implemented.
5. [x] Flask-WTForms
6. [x] Custom decorators to implement access controls and enforce certain rules.


## 1. Code Structure
<!--
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
├── templates/                        # HTML templates
│   ├── base.html                     # Base layout template
│   ├── home.html                     # Home page
│   ├── login_signup.html             # Login/Signup page
│   ├── event_details.html            # Event details page
│   ├── user_owned_events.html        # Events created by user
│   ├── user_registered_events.html   # events registered for by user
│   ├── create_event.html             # create new event
│   ├── send_email.html               # send support email to users
│   ├── user_profile.html             # user view and edit their profile
│
├── static/                   # Static files (CSS, JS, images)
│
├── README.md                 # Project overview and details (this document)
├── requirements.txt          # Python dependencies
├── config.py                 # App configurations
├── .env                      # Separation of sensitive info
├── run.py                    # Entry point for the application
-->

## 1. User Management
- **User Registration**
  - [x] Users can sign up by providing necessary information (username, email, password).  
  - [x] User roles can be defined (e.g., regular users and event organizers).
  - [x] OAuth / Credentials of other SM like google/github/... for signing on and logging in.
      - [x] Google OAuth 2.0
      - [ ] Github

- **User Signup**
  - [x] Unique Username and unique email choice - incorporation of javascript to dynamically check and update avaiability of input username and email for new account.

- **User Authentication**
  - [x] Role-based access management ('admin', 'moderator', 'user', 'guest')
  - [x] Users can log in using their credentials.
  - [x] Password reset options for forgotten passwords.
      - [x] Flast-Mailman library implementation to manage reset password emails

- **User Profiles**
  - [x] Users can view and edit their profiles.
  - [x] Change password
  - [x] Users can see a history of events they have hosted and attended.

- **Notifications and Communication**
  - [x] Automated email notifications and communication for
    - [x] New event creation
    - [ ] Event modifications
    - [x] Setting up of 'mailtrap' online tool to test the email functionality

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
  - [x] Option to upload images or promotional material for the event.

- **Managing Events**
  - [x] Event organizers can edit or delete their events.
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
  - [x] Admin can manage user accounts (approve, suspend, or delete accounts).
- **Event Oversight**
  - [x] Admin can review and manage all events on the platform.
      - [x] edit
      - [x] delete
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
  - [x] secure password by flask_bcrypt tools
  - [x] OAuth 2.0 authentication.
  - [ ] JWT (JSON Web Tokens) or session-based authentication for managing user sessions.

## 7. User Interface
- **Responsive Design**
  - [ ] Ensure the application is accessible on both desktop and mobile devices.
- **User-Friendly Navigation**
  - [x] Intuitive layout for easy navigation between different sections of the application.

## 8. Additional Features (Optional)
- **Social Media Integration**
  - [ ] Users can share events on social media platforms.
- **Payment Integration**
  - [ ] For paid events, integration with payment gateways for processing transactions.
- **Feedback and Reviews**
  - [ ] Users can leave feedback or reviews for events they attended.

## Libraries and requirements

## Routes
