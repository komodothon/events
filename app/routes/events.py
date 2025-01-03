"""app/routes/events.py"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from app import db, login_manager
from app.services.db_utils import *
from app.services.email import email_create_event

from app.forms import CreateEventForm

events_bp = Blueprint("events", __name__, template_folder="templates")

@events_bp.route("/")
def home():
    events = get_all_events()
    return render_template("home.html", events=events)

@events_bp.route("/user_owned_events")
@login_required
def user_owned_events():
    """ User owned events """
    if current_user.is_authenticated:
        headers, user_owned_events = get_owned_events(current_user)
        return render_template("user_owned_events.html", user_owned_events=user_owned_events, headers=headers)
    return "username not found!"

@events_bp.route("/user_registered_events")
@login_required
def user_registered_events():
    """ Events registered for by the user"""
    if current_user.is_authenticated:
        headers, user_registered_events = get_registered_events(current_user)
        return render_template("user_registered_events.html", user_registered_events=user_registered_events, headers=headers)
        # return f'Events for username {username}'

    return "username not found!"

@events_bp.route("/event_details/<int:event_id>")
def event_details(event_id):
    """ event details page """
    event = get_event_detail(event_id)

    if event:
        return render_template("event_details.html", event=event)
    else:
        return "Event Not Found"
    
@events_bp.route("/create_event", methods=["POST", "GET"])
@login_required
def create_event():
    """ Create a new event """

    create_event_form = CreateEventForm()
    print("create event: initiated")

    if create_event_form.validate_on_submit():
    # if request.method == "POST":
        print(request.form.items())
        # print("create event: validated")
        title = create_event_form.title.data
        date = create_event_form.date.data
        location = create_event_form.location.data
        description = create_event_form.description.data
        
        create_new_event(title, date, location, description, current_user)

        recipient = [current_user.email]
        subject = f"Event: {title} created"
        body = f"Congrats. This is a confirmation  email for the event creation: {title}"

        email_create_event(recipient, subject, body,)

        return redirect(url_for("events.home"))

    return render_template("create_event.html", form=create_event_form)


@events_bp.route("/register_for_event/<int:event_id>", methods=["GET"])
@login_required
def register_for_event(event_id):
    """ User registering for an event """
    if current_user.is_authenticated and event_id:
        user_event_registration(event_id, current_user)
    return redirect(url_for("events.user_registered_events"))