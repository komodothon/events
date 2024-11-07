from flask import Flask, render_template, request, g, session, redirect, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from os.path import join
import sqlite3, re

DATABASE = join('instance', 'event_user_data.db')

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

app = Flask(__name__)

app.secret_key = "app_secret_key"




# ---------db actions ----------

def get_db_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        # print("database connection established")
        return g.db
    
# with app.app_context():
def get_db_as_dict():
    connection = get_db_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT event_id, event_name, event_date, event_location, event_description FROM events")
    headers = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    rows = [dict(row) for row in rows]
    
    # for row in rows:
    #     for key, value in row.items():
    #         print(f'{key}: {value}')
    return headers, rows

def create_new_user(username, email, password):
    hashed_password = generate_password_hash(password)
    prepped_data = (username, email, hashed_password)

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO users (username, user_email, user_password) VALUES (?, ?, ?)", prepped_data)

    connection.commit()
    return username

def create_new_event(prepped_data):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO events 
        (event_name, event_date, event_location, event_description, event_owner) 
        VALUES (?, ?, ?, ?, ?)""", prepped_data)
            
    connection.commit()

def get_owned_events(username):
    connection = get_db_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT event_name, event_date, event_location, event_description FROM events WHERE event_owner = (?)", (username,))
    user_owned_events = cursor.fetchall()
    user_owned_events = [dict(row) for row in user_owned_events]
    headers = [description[0] for description in cursor.description]
    
    return headers, user_owned_events

def get_registered_events(username):
    connection = get_db_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT event_name, event_date, event_location, event_description FROM events WHERE event_id IN
        (SELECT event_id FROM events_registrations WHERE username = (?))""", (username,))
    user_owned_events = cursor.fetchall()
    user_owned_events = [dict(row) for row in user_owned_events]
    headers = [description[0] for description in cursor.description]
    
    return headers, user_owned_events
    
def user_event_registration(event_id, username):
    prepped_data = (event_id, username)

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO events_registrations (event_id, username) VALUES (?, ?)", prepped_data)
    connection.commit()


def authenticate_user(username, user_password):
    connection = get_db_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? LIMIT 1", (username,))

    user_detail = cursor.fetchone()

    connection.close()

    if user_detail:
        if check_password_hash(user_detail['user_password'], user_password):
            return user_detail['username']
        else:
            return None
    else:
        return None


def add_event_user_registration(event_id, username):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT 1 FROM user WHERE username = ?", (username))
    cursor.row_factory = sqlite3.Row
    user_detail = cursor.fetchone()
    user_id = user_detail['user_id']

    prepped_data = (event_id, user_id)

    cursor.execute("INSERT INTO events_registrations (event_id, user_id) VALUES (?, ?)", prepped_data)

    connection.commit()


@app.teardown_appcontext
def close_db_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()



# -----------routes-----------

@app.route("/")
def home():
    headers, events_list = get_db_as_dict()
    # username = None [instead, setup session['username'] and control validation through that]
    username = session.get('username')

    return render_template("home.html", headers=headers, events_list=events_list, username=username)


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
        event_name = request.form.get('event_name')
        event_date = request.form.get('event_date')
        event_location = request.form.get('event_location')
        event_description = request.form.get('event_description')
        event_owner = session['username']

        prepped_data = (event_name, event_date, event_location, event_description, event_owner)
        print(prepped_data)

        if not event_name or not event_date or not event_location or not event_description:
            return "Incomplete fields", 400
        # connection = get_db_connection()
        # cursor = connection.cursor()
        # cursor.execute(
        #     """
        #     INSERT INTO events 
        #     (event_name, event_date, event_location, event_description) 
        #     VALUES (?, ?, ?, ?)""", prepped_data)
                
        # connection.commit()
        # connection.close()
        create_new_event(prepped_data)

        return redirect(url_for("home"))
    
    return render_template("create_event.html", username=username)

@app.route("/event_details/<int:event_id>")
def event_details(event_id):
    connection = get_db_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE event_id = ? LIMIT 1", (event_id,))
    event = cursor.fetchone()

    if event:
        event = dict(event)
        session['event_id'] = event['event_id']
            
    connection.close()
    username = session.get('username')

    return render_template("event_details.html", event=event, username=username)

@app.route("/register_for_event")
def register_for_event():
    event_id = session.get('event_id')
    username = session.get('username')

    print(event_id, username)

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



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route('/check_username')
def check_username():
    username = request.args.get("username")
    # print(f'username: {username}')
    available = False

    # Database query to check if the username exists
    if username:
        # print(f'username: {username}')

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        # print(f'result: {result}')
        
        # If no result is found, username is available
        available = result is None
        # print(f'available = {available}')

    # Return JSON response
    return jsonify({"available": available})


@app.route("/check_email", methods=["GET"])
def check_email():
    email = request.args.get('email')

    if re.match(EMAIL_REGEX, email):
        return jsonify({'valid': True, 'message': 'Valid email address'}), 200
    else:
        return jsonify({'valid': False, 'message': 'Invalid email address'}), 400

if __name__ == "__main__":
    app.run(debug=True)