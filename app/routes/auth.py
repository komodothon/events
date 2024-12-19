"""app/roputes/auth.py"""

# Handles user authentication, such as login, signup, and logout.

from flask import Blueprint, redirect, url_for, render_template, request, jsonify
from flask_login import login_user, logout_user, login_required
from email_validator import validate_email, EmailNotValidError

from app import db, login_manager
from app.models import User
from app.services import *
from app.forms import RegisterForm, LoginForm

auth_bp = Blueprint("auth", __name__, template_folder="../../templates")

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
    error = None
    login_form = LoginForm()
    register_form = RegisterForm()

    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        
        authenticated_user = authenticate_user(username, password)
 
        if authenticated_user:
            print("user authenticated")
            login_user(authenticated_user)
            return redirect(url_for("events.home"))
        else:
            print("Invalid username or password")
            error = "Invalid username or password"
            return render_template("login_signup.html", error=error, login_form=login_form, register_form=register_form)
    
    return render_template("login_signup.html", error=error, login_form=login_form, register_form=register_form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("events.home"))

@auth_bp.route("/password_recovery", methods=["GET", "POST"])
def password_recovery():

    return render_template("password_recovery.html")

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