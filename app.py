from flask import Flask, render_template, request, g, session, redirect, url_for, jsonify
from werkzeug.security import check_password_hash
from os.path import join
import sqlite3

DATABASE = join('instance', 'event_user_data.db')

app = Flask(__name__)

app.secret_key = "app_secret_key"


# ---------db actions ----------

def get_db_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        print("database connection established")
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

@app.route("/create_event", methods=["POST", "GET"])
def create_event():
    if request.method == 'POST':
        event_name = request.form.get('event_name')
        event_date = request.form.get('event_date')
        event_location = request.form.get('event_location')
        event_description = request.form.get('event_description')

        prepped_data = (event_name, event_date, event_location, event_description)
        print(prepped_data)

        if not event_name or not event_date or not event_location or not event_description:
            return "Incomplete fields", 400
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO events 
            (event_name, event_date, event_location, event_description) 
            VALUES (?, ?, ?, ?)""", prepped_data)
                
        connection.commit()
        connection.close()

        return "event added"
    
    return render_template("create_event.html")

@app.route("/event_details/<int:event_id>")
def event_details(event_id):
    connection = get_db_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE event_id = ? LIMIT 1", (event_id,))
    event = cursor.fetchone()

    if event:
        event = dict(event)
            
    connection.close()
    username = session.get('username')

    return render_template("event_details.html", event=event, username=username)


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
        re_eneter_password = request.form.get('re_enter_password')

    return render_template("login_signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route('/check_username')
def check_username():
    username = request.args.get("username")
    available = False

    # Database query to check if the username exists
    if username:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        # If no result is found, username is available
        available = result is None

    # Return JSON response
    return jsonify({"available": available})

if __name__ == "__main__":
    app.run(debug=True)
