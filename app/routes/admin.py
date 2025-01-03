"""app/routes/admin.py"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from flask_mailman import EmailMessage
from datetime import datetime

from app import db, bcrypt
from app.models import User, Event, Role
from app.services.decorators import role_required

from app.services.auth_utils import get_all_users, get_all_roles
from app.services.db_utils import get_all_events
from app.services.email import send_email

admin_bp = Blueprint('admin', __name__, template_folder="templates", static_folder="static")

@admin_bp.route("/")
@login_required
@role_required('admin')
def admin_home():
    users = get_all_users()
    events = get_all_events()
    roles = get_all_roles()

    return render_template("admin.html", users=users, events=events, roles=roles)

@admin_bp.route("/edit_user/<int:id>", methods=["POST"])
@login_required
@role_required('admin')
def edit_user(id):
    user = User.query.get(id)
    role_name = request.form.get("role")
    user.role = Role.query.filter_by(name=role_name).first()

    try:
        db.session.commit()
        flash(f"User {user.username} details updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occured during updates: {e}", "danger")

    return redirect(url_for("admin.admin_home"))


@admin_bp.route("/edit_event/<int:id>", methods=["POST"])
@login_required
@role_required('admin')
def edit_event(id):
    event = Event.query.get(id)

    event.title = request.form.get("title")
    event.date = datetime.fromisoformat(request.form.get("date"))
    event.location = request.form.get("location")
    event.description = request.form.get("description")

    try:
        db.session.commit()
        flash(f"Event {event.title} updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occured during updates: {e}.", "danger")

    return redirect(url_for("admin.admin_home"))


@admin_bp.route("/edit_role/<int:id>", methods=["POST"])
@login_required
@role_required('admin')
def edit_role(id):
    role = Role.query.get(id)

    role.name = request.form.get("name")
    role.description = request.form.get("description")

    try:
        db.session.commit()
        flash(f"Role {role.name} updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occured during updates {e}.", "danger")
    
    return redirect(url_for("admin.admin_home"))


@admin_bp.route("/send_email", methods=["GET", "POST"])
@login_required
@role_required('admin')
def send_test_email():
    
    if request.method == "POST":
        to_email = [request.form.get("to_email")]
        subject = request.form.get("subject")
        body = request.form.get("body")

        if all([to_email, subject, body]):
            print(f"to_email: {to_email}")
            print(f"subject: {subject}")
            print(f"body: {body}")

            try:
                send_email(to_email, subject, body)

                flash("Email sent successfully.", "success")

                return redirect(url_for("admin.admin_home"))
            except Exception as e:
                flash(f"Error during email send: {e}", "danger")
                return redirect(url_for("admin.admin_home"))

    
    return render_template("send_email.html")





