import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'instance/event_user_data.db'

def get_db_connection():
    db_connection = sqlite3.connect(DATABASE)
    return db_connection


connection = get_db_connection()
cursor = connection.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    event_name TEXT NOT NULL, 
    event_date TEXT NOT NULL, 
    event_location TEXT NOT NULL, 
    event_description TEXT NOT NULL)"""
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    user_email TEXT NOT NULL,
    user_password TEXT NOT NULL)"""
)

for i in range(1,21):
    event_name = f'event_name{i}'
    event_date =f'event_date{i}'
    event_location =f'event_location{i}'
    event_description =f'event_description{i}'

    prepped_data = (event_name, event_date, event_location, event_description)

    cursor.execute(
        """
        INSERT INTO events 
        (event_name, event_date, event_location, event_description) 
        VALUES (?, ?, ?, ?)""", prepped_data)
    
for j in range(1,11):
    username = f'username{j}'
    user_email = f'user{j}@sample.com'
    user_password = f'Hello{j}'
    hashed_password = generate_password_hash(user_password)

    prepped_data = (username, user_email, hashed_password)

    cursor.execute(
        """
        INSERT INTO users
        (username, user_email, user_password)
        VALUES (?, ?, ?)""", prepped_data)

connection.commit()
connection.close()
