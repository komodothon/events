"""app/services/db_utils.py"""

from app import db
from app.models import Event, User


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
    user_owned_events = user.events_owned
    headers = Event.headers()
    
    return headers, user_owned_events

def get_registered_events(user):
    user_registered_events = user.events_registered_for
    headers = Event.headers()
    
    return headers, user_registered_events

def user_event_registration(event_id, user):
    event = db.session.get(Event, event_id)

    if user not in event.registrants:
        event.registrants.append(user)
        
    db.session.commit()

def get_all_events():
    return db.session.query(Event).all()


