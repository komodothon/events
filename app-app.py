from flask import Flask, render_template, request, session, redirect, url_for, jsonify
# from werkzeug.security import check_password_hash, generate_password_hash

from os.path import join
import re

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from db_models import db, User, Event
from forms import *


EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

app = Flask(__name__)

# configurations
app.config['SECRET_KEY'] = "app_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# login  configurations
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# extensions
db.init_app(app)
bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()

# user loader helper function
@login_manager.user_loader
def load_user(user_id):
    user = db.session.get(User, int(user_id))
    return user


""" Functions """
def create_new_user(username, email, password):
    
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    
    new_user = User(username=username, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return new_user


def create_new_event(title, date, location, description, owner):
    event = Event(
        title=title, 
        date=date, 
        location=location, 
        description=description, 
        owner_id=owner.id
    )  

    db.session.add(event)
    db.session.commit()


def get_event_detail(id):
    event = db.session.get(Event, id)
    return event

def get_owned_events(user):
    user = db.session.query(User).filter_by(username=user.username).first()
    user_owned_events = user.events_owned
    headers = Event.headers()
    
    return headers, user_owned_events

def get_registered_events(user):
    user = db.session.query(User).filter_by(username=user.username).first()
    user_registered_events = user.events_registered_for
    headers = Event.headers()
    
    return headers, user_registered_events
    

def user_event_registration(event_id, user):
    event = db.session.get(Event, event_id)

    if user not in event.registrants:
        event.registrants.append(user)
        
    db.session.commit()

def authenticate_user(username, password):

    user = db.session.query(User).filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return user  
    else:
        return None
 
""" Routes """

@app.route("/")
def home():

    events = db.session.query(Event).all()
    return render_template("home.html", events=events)

@app.route("/login", methods = ["POST", "GET"])
def login():
    """ User Login"""
    error = None
    login_form = LoginForm()
    register_form = RegisterForm()

    if login_form.validate_on_submit():
        print("login form validated")
        username = login_form.username.data
        password = login_form.password.data
        
        authenticated_user = authenticate_user(username, password)
 
        if authenticated_user:
            print("user authenticated")
            login_user(authenticated_user)
            return redirect(url_for("home"))
        else:
            print("wrong username or password")
            error = "Invalid username or password"
            return render_template("login_signup.html", error=error, login_form=login_form, register_form=register_form)
    
    return render_template("login_signup.html", error=error, login_form=login_form, register_form=register_form)

@app.route("/signup", methods=["POST","GET"])
def signup():
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

            return redirect(url_for("home"))

    return render_template("login_signup.html", login_form=login_form, register_form=register_form)

@app.route("/create_event", methods=["POST", "GET"])
@login_required
def create_event():
    """ Create a new event """

    create_event_form = CreateEventForm()
    print("create event: initiated")

    # if create_event_form.validate_on_submit():
    if request.method == "POST":
        print(request.form.items())
        # print("create event: validated")
        title = create_event_form.title.data
        date = create_event_form.date.data
        location = create_event_form.location.data
        description = create_event_form.description.data
        
        create_new_event(title, date, location, description, current_user)

        return redirect(url_for("home"))

    return render_template("create_event.html", form=create_event_form)

@app.route("/event_details/<int:event_id>")
def event_details(event_id):
    """ event details page """
    event = get_event_detail(event_id)

    if event:
        return render_template("event_details.html", event=event)
    else:
        return "Event Not Found"

@app.route("/register_for_event/<int:event_id>", methods=["GET"])
@login_required
def register_for_event(event_id):
    """ User registering for an event """
    if current_user.is_authenticated and event_id:
        user_event_registration(event_id, current_user)
    return redirect(url_for("user_registered_events"))

@app.route("/user_owned_events")
@login_required
def user_owned_events():
    """ User owned events """
    if current_user.is_authenticated:
        headers, user_owned_events = get_owned_events(current_user)
        return render_template("user_owned_events.html", user_owned_events=user_owned_events, headers=headers)
    return "username not found!"

@app.route("/user_registered_events")
@login_required
def user_registered_events():
    """ Events registered for by the user"""
    if current_user.is_authenticated:
        headers, user_registered_events = get_registered_events(current_user)
        return render_template("user_registered_events.html", user_registered_events=user_registered_events, headers=headers)
        # return f'Events for username {username}'

    return "username not found!"

@app.route('/check_username')
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

@app.route("/check_email", methods=["GET"])
def check_email():
    email = request.args.get('email')

    if not email or not re.match(EMAIL_REGEX, email):
        return jsonify({'valid': False, 'available': False, 'message': 'Invalid email address'}), 400
    
    result = db.session.query(User).filter_by(email=email).first()
    available = result is None

    if available:
        return jsonify({'valid': True, 'available': available, 'message': 'Valid and available email address'}), 200
    
    else:
        return jsonify({'valid': True, 'available': available, 'message': 'Valid but not available email address '}), 409

    # if email and re.match(EMAIL_REGEX, email):
    #     result = db.session.query(User).filter_by(email=email).first()
    #     available = result is None

    #     if available:
    #         return jsonify({'valid': True, 'available': available, 'message': 'Valid and available email address'}), 200
        
    #     else:
    #         return jsonify({'valid': True, 'available': available, 'message': 'Valid but not available email address'}), 200



    # else:
    #     return jsonify({'valid': False, 'message': 'Invalid email address'}), 400

@app.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("home"))

@app.route("/password_recovery")
def password_recovery():
    return render_template("password_recovery.html")

if __name__ == "__main__":
    app.run(debug=True)