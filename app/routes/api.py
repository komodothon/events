"""app/routes/api.py"""

from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from app.services import create_new_user, authenticate_user, get_all_events, get_owned_events, get_registered_events, create_new_event, get_event_detail, user_event_registration
user_event_registration

api_bp = Blueprint("api", __name__)

# api register new user
@api_bp.route("/register", methods=["POST"])
def register():
    """api new user registration"""
    data = request.json
    username = data["username"]
    email = data["email"]
    password = data["password"]
    
    new_user = create_new_user(username, email, password)
    return jsonify({'message': 'New user registered successfully', 'user_id':new_user.id})

# api user login
@api_bp.route("/login", methods=["POST"])
def login():
    """api user login"""
    data = request.json
    username = data["username"]
    password = data["password"]

    user = authenticate_user(username, password)
    if user:
        login_user(user)
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

# api user logout
@api_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """api user logout"""
    logout_user()
    return jsonify({'message': 'User logged out'})

# api get all events
@api_bp.route("/events", methods=["GET"])
def list_all_events():
    events = get_all_events()
    return jsonify([{
        'id': event.id,
        'title': event.title,
        'date': event.date,
        'location': event.location,
        'description': event.description,
        'owner_id': event.owner_id
    } for event in events]), 200

# api user owned events
@api_bp.route("/user_owned_events/", methods=["GET"])
@login_required
def user_owned_events():    
    headers, events = get_owned_events(current_user)
    return jsonify([{
        'id': event.id,
        'title': event.title,
        'date': event.date,
        'location': event.location,
        'description': event.description,
        'owner_id': event.owner_id
    } for event in events]), 200

# api user registered events
@api_bp.route("/user_registered_events/", methods=["GET"])
@login_required
def user_registered_events():    
    headers, events = get_registered_events(current_user)
    return jsonify([{
        'id': event.id,
        'title': event.title,
        'date': event.date,
        'location': event.location,
        'description': event.description,
        'owner_id': event.owner_id
    } for event in events]), 200


# api create new event
@api_bp.route("/create_event/", methods=["POST"])
@login_required
def create_event(): 
    data = request.json

    title = data["title"]
    date_str = data["date"]
    date = datetime.fromisoformat(date_str)
    location = data["location"]
    description = data["description"]


    create_new_event(title, date, location, description, current_user)

    return jsonify({'message': 'Event created Successfully', 'event title': title}), 200

# api event details
@api_bp.route("/event_details/<int:event_id>", methods=["GET"])
def event_details(event_id):
    event = get_event_detail(event_id)
    return jsonify({
        'id': event.id,
        'title': event.title,
        'date': event.date,
        'location': event.location,
        'description': event.description,
        'owner_id': event.owner_id,
    }), 200
    

# api user register for an event
@api_bp.route("/register_for_event/<int:event_id>", methods=["POST"])
@login_required
def register_for_event(event_id):
    """ User registering for an event """
    if current_user.is_authenticated and event_id:
        user_event_registration(event_id, current_user)
    return jsonify({'message': 'Registration successful', 'user': current_user.username, 'event_id': event_id})