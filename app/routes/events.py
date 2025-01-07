"""app/routes/events.py"""

from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from PIL import Image
from datetime import datetime

from app import db, login_manager
from app.services.db_utils import *
from app.services.email import send_email

from app.forms import EventForm

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

@events_bp.route("/event_details/<int:event_id>", methods=["GET", "POST"])
def event_details(event_id):
    """ event details page """
    event = get_event_detail(event_id)

    if not event:
        flash("Event not found.", "danger")
        return redirect(url_for("events.home"))
    
    if request.method == "POST":
        try:
            event.title = request.form.get("title", event.title)
            event.description = request.form.get("description", event.description)
            event.date = datetime.strptime(request.form["date"], "%Y-%m-%dT%H:%M")
            event.location = request.form.get("location", event.location)

            # Check for new image upload
            if "image" in request.files and request.files["image"].filename:
                print(f"request.files: {request.files}")
                file = request.files["image"]
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.root_path, "../static/uploads/event_images")

                # Ensure the directory exists
                os.makedirs(upload_folder, exist_ok=True)

                # Delete the old image if it exists
                if event.image_path and os.path.exists(os.path.join(current_app.root_path, event.image_path)):
                    os.remove(os.path.join(current_app.root_path,"..", event.image_path))

                # Save the new image
                image_path = os.path.join("static/uploads/event_images", filename).replace("\\", "/")
                with Image.open(file) as img:
                    img.thumbnail((800, 800))
                    img.save(os.path.join(upload_folder, filename))
                event.image_path = image_path

            db.session.commit()
            print(f"event updated: {event}")
            flash("Event successfully updated.", "info")

        except Exception as e:
            db.session.rollback()
            flash(f"Error during update of event: {str(e)}", "danger")


    return render_template("event_details.html", event=event)


@events_bp.route("/create_event", methods=["POST", "GET"])
@login_required
def create_event():
    """ Create a new event """

    form = EventForm()
    print("create event: initiated")

    if form.validate_on_submit():
    # if request.method == "POST":
        print(request.form.items())
        # print("create event: validated")
        title = form.title.data
        date = form.date.data
        location = form.location.data
        description = form.description.data

        file = form.image.data
        image_path = None

        if file:
            filename = secure_filename(file.filename)
            image_path = os.path.join("static/uploads/event_images", filename).replace("\\", "/")

            upload_folder = os.path.join(current_app.root_path, "../static/uploads/event_images")
            try:
                os.makedirs(upload_folder, exist_ok=True)
                with Image.open(file) as img:
                    img.thumbnail((800,800))
                    img.save(os.path.join(upload_folder, filename))
                print(f"File saved to: {image_path}")
            except Exception as e:
                print(f"Error saving file: {e}")
                flash("Error while saving file.", "danger")
                return redirect(url_for("events.create_event"))
            
        create_new_event(title, date, location, description, current_user, image_path)

        recipient = [current_user.email]
        subject = f"Event: {title} created"
        body = f"Congrats. This is a confirmation  email for the event creation: {title}"

        send_email(recipient, subject, body)

        flash("Event created successfully!", "info")

        return redirect(url_for("events.home"))

    return render_template("create_event.html", form=form)


@events_bp.route("/register_for_event/<int:event_id>", methods=["GET"])
@login_required
def register_for_event(event_id):
    """ User registering for an event """
    if current_user.is_authenticated and event_id:
        user_event_registration(event_id, current_user)
    return redirect(url_for("events.user_registered_events"))


@events_bp.route("/delete_event/<int:event_id>", methods=["GET"])
def delete_event(event_id):
    event =  Event.query.get(event_id)

    if not event:
        flash("Event not found!", "danger")
        return redirect(url_for("events.home"))
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted.", "info")
    return redirect(url_for("events.home"))