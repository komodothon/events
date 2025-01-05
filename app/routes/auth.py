"""app/routes/auth.py"""
# Handles user authentication, such as login, signup, and logout.

from flask import Blueprint, redirect, url_for, render_template, request, jsonify, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from email_validator import validate_email, EmailNotValidError
from uuid import uuid4

from werkzeug.exceptions import Unauthorized

from app import db, login_manager, oauth

from app.models import User
from app.services import *
from app.services.auth_utils import change_password, verify_reset_token, send_password_reset_email
from app.forms import RegisterForm, LoginForm, RequestResetForm, ResetPasswordForm
from app.services.decorators import logout_required

auth_bp = Blueprint("auth", __name__, template_folder="../../templates")

google = None

# Configure Google OAuth using current_app to fetch configuration values
@auth_bp.before_app_request
def configure_google_oauth():

    global google
    if google is None:
        google = oauth.register(
            name="google",
            client_id =current_app.config['GOOGLE_CLIENT_ID'],
            client_secret=current_app.config['GOOGLE_CLIENT_SECRET'],
            server_metadata_url=current_app.config['GOOGLE_DISCOVERY_URL'],
            client_kwargs={"scope": "openid email profile"},
        )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """ Register a new user """

    login_form = LoginForm()
    register_form = RegisterForm()

    if register_form.validate_on_submit():

        username = register_form.username.data
        email = register_form.email.data
        password = register_form.password.data

        new_user = create_new_user(username, email, password)
        if new_user:
            login_user(new_user)
            return redirect(url_for("events.home"))

    return render_template("login_signup.html", login_form=login_form, register_form=register_form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """ User Login"""

    login_form = LoginForm()
    register_form = RegisterForm()

    if login_form.validate_on_submit():
        
        username = login_form.username.data
        password = login_form.password.data
        
        authenticated_user = authenticate_user(username, password)
 
        if authenticated_user:
            login_user(authenticated_user)
            role_name = current_user.role
            return redirect(url_for("events.home"))
        else:
            flash("Invalid username or password", "danger")
            return render_template("login_signup.html", login_form=login_form, register_form=register_form)
    
    return render_template("login_signup.html", login_form=login_form, register_form=register_form)

"""Google OAuth 2.0 routes"""
@auth_bp.route("/google_login")
def google_login():
    """Initiate Google OAuth login."""
    nonce = uuid4().hex
    session['nonce'] = nonce

    redirect_url = url_for("auth.google_callback", _external=True)
    return google.authorize_redirect(redirect_url, nonce=nonce)


@auth_bp.route("/google_callback")
def google_callback():
    """Handle callback from Google"""
    token = google.authorize_access_token()

    if not token:
        flash("Authorization failed.", "danger")
        return redirect(url_for("auth.login"))

    nonce = session.pop("nonce", None)
    
    if not nonce:
        flash("Invalid nonce. Please try logging in again.", "danger")
        return redirect(url_for("auth.login"))

    try:
        user_info = google.parse_id_token(token, nonce=nonce)
        print(f"user_info: {user_info}")
    except Exception as e:
        flash(f"Failed to parse ID token: {e}", "danger")
        return redirect(url_for("auth.login"))

    if user_info:        

        email = user_info.get('email')
        username = email.split("@")[0]

        # check if user already exists in database
        user = User.query.filter_by(email=email).first()
        if not user:
            # creates new user in database for this google OAuth user
            user = User(
                username = username,
                email = email,
                auth_method = 'oauth',
            )
            db.session.add(user)
            db.session.commit()
        
        # log the user in
        login_user(user)            
        return redirect(url_for("events.home"))
    flash("Google authentication failed.", "error")
    return redirect(url_for("auth.login"))


"""Logout route"""
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("events.home"))


"""Reset Password"""
@auth_bp.route("/reset_request", methods=["GET", "POST"])
@logout_required
def reset_request():
    form = RequestResetForm()

    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if user.auth_method == "oauth":
            flash("Please login with oauth 2.0 link provided!", "danger")
            return redirect(url_for("auth.login"))

        if user and user.auth_method == "password":
            send_password_reset_email(user)
            flash("A password reset link will be sent to this email after verification", "info")
            return redirect(url_for("auth.login"))

    return render_template("reset_request.html", form=form)

@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
@logout_required
def reset_password(token):
    email = verify_reset_token(token)
    print(f"email verified: {email}")

    if not email:
        flash("Invalid or expired token", "danger")
        return redirect(url_for("auth.reset_request"))
    
    user = User.query.filter_by(email=email).first_or_404()
    print(f"User found: {user}")

    form = ResetPasswordForm()

    if form.validate_on_submit():
        new_password = form.new_password.data
        change_password(user, new_password)
        flash("Your password has been changed successfully!", "success")

        return redirect(url_for("auth.login"))
    return render_template("reset_password.html", token=token, form=form)
            

"""Profile"""
@auth_bp.route("/user_profile", methods=["GET", "POST"])
@login_required
def user_profile():

    if request.method == "POST":
        password = request.form.get("password")
        change_password(current_user, password)

    return render_template("user_profile.html")



"""AJAX routes"""
@auth_bp.route('/check_username')
def check_username():
    username = request.args.get("username")
    # print(f'username: {username}')
    available = False

    # Database query to check if the username exists
    if username:
        # print(f'username: {username}')
        result = db.session.query(User).filter_by(username=username).first()

               
        # If no result is found, username is available
        available = result is None # if result is None, available = True
        # print(f'available = {available}')

    # Return JSON response
    return jsonify({"available": available})

@auth_bp.route("/check_email", methods=["GET"])
def check_email():
    email = request.args.get('email')

    # validate email
    try:
        valid = validate_email(email)
        email = valid.email

    except EmailNotValidError as e:
        return jsonify({'valid': False, 'available': False, 'message': str(e)}), 400
    
    result = db.session.query(User).filter_by(email=email).first()
    available = result is None

    if available:
        return jsonify({'valid': True, 'available': available, 'message': 'Valid and available email address'}), 200
    
    else:
        return jsonify({'valid': True, 'available': available, 'message': 'Valid but not available email address '}), 409
    

