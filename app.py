from flask import Flask, render_template, request, g, session, redirect, url_for, jsonify
# from werkzeug.security import check_password_hash, generate_password_hash

from os.path import join
import sqlite3, re

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from db_models import db, User, Event


EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

app = Flask(__name__)

# configurations
app.config['SECRET_KEY'] = "app_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# extensions
db.init_app(app)
bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()

# ---------db actions ----------

# def get_db_connection():
    # if 'db' not in g:
    #     g.db = sqlite3.connect(DATABASE)
    #     # print("database connection established")
    #     return g.db
    


def create_new_user(username, email, password):
    hashed_password = bcrypt.generate_password_hash(password)
    
    new_user = User(username=username, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return new_user.username


def create_new_event(title, date, location, description, username):
    owner = db.session.query(User).filter_by(username=username).first()

    event = Event(title=title, date=date, location=location, description=description, owner_id=owner.id)  

    db.session.add(event)
    db.session.commit()


def get_event_detail(id):
    event = db.session.get(Event, id)
    return event

def get_owned_events(username):
    user = db.session.query(User).filter_by(username=username).first()
    user_owned_events = user.events_owned
    headers = Event.headers()
    
    return headers, user_owned_events

def get_registered_events(username):
    user = db.session.query(User).filter_by(username=username).first()
    user_registered_events = user.events_registered_for
    headers = Event.headers()
    
    return headers, user_registered_events
    

def user_event_registration(event_id, username):
    event = db.session.get(Event, event_id)
    user = db.session.query(User).filter_by(username=username).first()

    if user not in event.registrants:
        event.registrants.append(user)
        
    db.session.commit()

def authenticate_user(username, user_password):

    user = db.session.query(User).filter_by(username=username).first()
    print(user)
    if user and bcrypt.check_password_hash(user.password, user_password):
        return user.username   
    else:
        return None
    # return user.username if user and bcrypt.check_password_hash(user_password, user.password) else None


# def add_event_user_registration(event_id, username):
#     connection = get_db_connection()
#     cursor = connection.cursor()

#     cursor.execute("SELECT 1 FROM user WHERE username = ?", (username))
#     cursor.row_factory = sqlite3.Row
#     user_detail = cursor.fetchone()
#     user_id = user_detail['user_id']

#     prepped_data = (event_id, user_id)

#     cursor.execute("INSERT INTO events_registrations (event_id, user_id) VALUES (?, ?)", prepped_data)

#     connection.commit()

# @app.teardown_appcontext
# def close_db_connection(exception):
#     db = g.pop('db', None)
#     if db is not None:
#         db.close()

# -----------routes-----------

@app.route("/")
def home():
    username = session.get('username')
    events = db.session.query(Event).all()
    return render_template("home.html", events=events, username=username)

@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        user_password = request.form.get('user_password')

        authenticated_username = authenticate_user(username, user_password)
 
        if authenticated_username:
            session['username'] = authenticated_username
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password"
            return render_template("login_signup.html", error=error)
    
    return render_template("login_signup.html")

@app.route("/signup", methods=["POST","GET"])
def signup():
    if request.method == "POST":
        new_username = request.form.get('new_username')
        new_email = request.form.get('new_email')
        new_password = request.form.get('new_password')

        added_username = create_new_user(new_username, new_email, new_password)
        if added_username:
            session['username'] = added_username

            return redirect(url_for("home"))

    return render_template("login_signup.html")

@app.route("/create_event", methods=["POST", "GET"])
def create_event():
    username = session.get('username')
    if request.method == 'POST':
        title = request.form.get('title')
        date = request.form.get('date')
        location = request.form.get('location')
        description = request.form.get('description')

        if not title or not date or not location or not description:
            return "Incomplete fields", 400

        create_new_event(title, date, location, description, username)

        return redirect(url_for("home"))
    
    return render_template("create_event.html", username=username)

@app.route("/event_details/<int:event_id>")
def event_details(event_id):
    username = session.get('username')

    event = get_event_detail(event_id)

    if event:
        return render_template("event_details.html", event=event, username=username)
    else:
        return "Event Not Found"

@app.route("/register_for_event/<int:event_id>", methods=["GET"])
def register_for_event(event_id):
    username = session.get('username')
    if username and event_id:
        user_event_registration(event_id, username)
    return redirect(url_for("user_registered_events"))

@app.route("/user_owned_events")
def user_owned_events():
    username = session.get('username')
    if username is not None:
        headers, user_owned_events = get_owned_events(username)
        return render_template("user_owned_events.html", username=username, user_owned_events=user_owned_events, headers=headers)
    return "username not found!"

@app.route("/user_registered_events")
def user_registered_events():
    username = session.get('username')
    if username is not None:
        headers, user_registered_events = get_registered_events(username)
        return render_template("user_registered_events.html", username=username, user_registered_events=user_registered_events, headers=headers)
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
    session.clear()
    return redirect(url_for("home"))

@app.route("/password_recovery")
def password_recovery():
    return render_template("password_recovery.html")

if __name__ == "__main__":
    app.run(debug=True)