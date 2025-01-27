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

    return render_template("event_details.html", event=event)


@events_bp.route("/edit_event/<int:event_id>", methods=["GET", "POST"])
def edit_event(event_id):
    event = get_event_detail(event_id)

    if request.method == "POST":
        
        try:
            event.title = request.form.get("title", event.title)

            event_type = request.form.get("event_type")
            if event_type not in ["VIRTUAL", "IN-PERSON"]:
                return f"Invalid event type: {event_type}", 400
            
            event.event_type = event_type

            event.description = request.form.get("description", event.description)
            event.date = datetime.strptime(request.form["date"], "%Y-%m-%dT%H:%M")

            print("edit_event form submitted")

            # location details
            google_place_id = request.form.get("place_id")
            name = request.form.get("name")
            address = request.form.get("address")
            latitude = request.form.get("latitude")
            longitude = request.form.get("longitude")

            location_id = None
            if google_place_id:
                location = get_location(google_place_id)
                if not location:
                    location = create_new_location(google_place_id, name, address, latitude, longitude)
                location_id = location.id
            else:
                # error handling
                location_id = 6

            event.location_id = location_id
            print(f"location_id: {event.location_id}")
            
            # image handling
            if "image" in request.files and request.files["image"].filename:
                file = request.files["image"]
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.root_path, "../static/uploads/event_images")

                # Ensurin that the folder exists
                os.makedirs(upload_folder, exist_ok=True)

                # Delete old image from folder, if any
                if event.image_path and os.path.exists(os.path.join(current_app.root_path, event.image_path)):
                    os.remove(os.path.join(current_app.root_path, "..", event.image_path))

                # Save the new image
                image_path = os.path.join("static/uploads/event_images", filename).replace("\\", "/")
                with Image.open(file) as img:
                    img.thumbnail((800,800))
                    img.save(os.path.join(upload_folder, filename))
                event.image_path = image_path

            db.session.commit()

            print("edit_event form submitted")
            flash("Event updated successfully.", "info")
            return redirect(url_for("events.event_details", event_id=event.id))


        except Exception as e:
            db.session.rollback()
            flash(f"Error during update of event: {str(e)}", "danger")
    return render_template("edit_event.html", event=event)


@events_bp.route("/create_event", methods=["POST", "GET"])
@login_required
def create_event():
    """ Create a new event """

    event_form = EventForm()


    if event_form.validate_on_submit():
    # if request.method == "POST":

        title = event_form.title.data
        event_type = event_form.event_type.data
        date = event_form.date.data

        # location details
        google_place_id = request.form.get("place_id")
        name = request.form.get("name")
        address = request.form.get("address")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")

        print(f"""
                google_place_id = {google_place_id}
                location_name = {name}
                location_address = {address}
                location_latitude = {latitude}
                location_longitude = {longitude}
              """)

        if google_place_id:
            location = get_location(google_place_id)
            if not location:
                location = create_new_location(google_place_id, name, address, latitude, longitude)
            
            location_id = location.id
            print(location)
        else:
            # error handling
            location_id = 6


        description = event_form.description.data

        file = event_form.image.data
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
                # print(f"File saved to: {image_path}")
            except Exception as e:
                # print(f"Error saving file: {e}")
                flash("Error while saving file.", "danger")
                return redirect(url_for("events.create_event"))
            
        create_new_event(title, event_type, date, location_id, description, current_user, image_path)

        recipient = [current_user.email]
        subject = f"Event: {title} created"
        body = f"Congrats. This is a confirmation  email for the event creation: {title}"

        send_email(recipient, subject, body)

        flash("Event created successfully!", "info")

        return redirect(url_for("events.home"))

    return render_template("create_event.html", event_form=event_form)


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
    return redirect(url_for("events.user_owned_events"))