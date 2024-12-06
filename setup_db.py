from db_models import db, User, Event, event_registrations
from flask_bcrypt import Bcrypt
from random import randint, choice, sample
from datetime import datetime, date, timedelta

from app import app

bcrypt = Bcrypt(app)

def main():

    
    with app.app_context():
        add_sample_users()
        add_sample_events()
        add_sample_event_registrations()

        db.session.commit()
        db.session.close()


def add_sample_users():
    for i in range(1,26):
        username = f"user{i}"
        email = f"user{i}@sample.com"
        password = f"Hello{i}"
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(
            username=username, 
            email=email, 
            password=hashed_password
        )  
       
        db.session.add(user)

def add_sample_events():
    for i in range(1,26):
        title = f"title {i}"

        location = f"location {i}"
        description = f"description {i}"

        random_days = randint(3, 25)
        random_hour = randint(8,18)
        random_min = choice([0, 30])
        date = datetime.now() + timedelta(
            days=random_days, 
            hours=random_hour, 
            minutes=random_min
        )

        date = date.replace(second=0, microsecond=0)

        
        users = db.session.query(User).all()
        owner = choice(users)
        owner_id = owner.id

        event = Event(
            title=title, 
            date=date, 
            location=location, 
            description=description, 
            owner_id=owner_id
        )

        db.session.add(event)

def add_sample_event_registrations():
    events = db.session.query(Event).all()
    users = db.session.query(User).all()

    for event in events:
        available_users = [user for user in users if user.id != event.owner_id]
        
        registrant_count = randint(5, min(15, len(available_users)))

        registrants = sample(available_users, k=registrant_count)

        event.registrants.extend(registrants)




# import sqlite3
# from flask_bcrypt import Bcrypt
# from random import randint

# DATABASE = 'instance/events.db'

# def get_db_connection():
#     db_connection = sqlite3.connect(DATABASE)
#     return db_connection

# def add_sample_users(cursor):
#     for j in range(1,11):
#         username = f'username{j}'
#         user_email = f'user{j}@sample.com'
#         user_password = f'Hello{j}'
#         hashed_password = generate_password_hash(user_password)

#         prepped_data = (username, user_email, hashed_password)

#         cursor.execute(
#             """
#             INSERT INTO users
#             (username, user_email, user_password)
#             VALUES (?, ?, ?)""", prepped_data)

# def add_sample_events(cursor):
#     for i in range(1,21):
#         event_name = f'event_name{i}'
#         event_date =f'event_date{i}'
#         event_location =f'event_location{i}'
#         event_description =f'event_description{i}'
#         k = randint(1,10)
#         event_owner = f'username{k}'

#         prepped_data = (event_name, event_date, event_location, event_description, event_owner)

#         cursor.execute(
#             """
#             INSERT INTO events 
#             (event_name, event_date, event_location, event_description, event_owner) 
#             VALUES (?, ?, ?, ?, ?)""", prepped_data)

# def add_sample_events_registrations(cursor):
#     for i in range(1,6):
#         event_id = randint(1,20)

#         username= f'username{randint(1,10)}'

#         prepped_data = (event_id, username)

#         cursor.execute(
#             """
#             INSERT INTO events_registrations (
#             event_id, username) 
#             VALUES (?, ?)""", prepped_data)
            

# def main():
#     connection = get_db_connection()
#     cursor = connection.cursor()

#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS events (
#         event_id INTEGER PRIMARY KEY AUTOINCREMENT, 
#         event_name TEXT NOT NULL, 
#         event_date TEXT NOT NULL, 
#         event_location TEXT NOT NULL, 
#         event_description TEXT NOT NULL,
#         event_owner TEXT NOT NULL)""")

#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS users (
#         user_id INTEGER PRIMARY KEY AUTOINCREMENT,
#         username TEXT NOT NULL UNIQUE,
#         user_email TEXT NOT NULL,
#         user_password TEXT NOT NULL)""")
    
#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS events_registrations (
#         registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
#         event_id INTEGER,
#         username TEXT NOT NULL)""")


#     add_sample_users(cursor)
#     add_sample_events(cursor)
#     add_sample_events_registrations(cursor)

#     connection.commit()
#     connection.close()

if __name__ == "__main__":
    main()