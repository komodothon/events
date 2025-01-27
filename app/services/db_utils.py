"""app/services/db_utils.py"""

from app import db
from app.models import Event, User, Location


def create_new_event(title, event_type, date, location_id, description, owner, image_path):
    event = Event(
        title=title,
        event_type=event_type, 
        date=date, 
        location_id=location_id, 
        description=description, 
        owner_id=owner.id,
        image_path = image_path,
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

def edit_event(event):
    pass

def delete_event(event):
    db.session.delete(event)
    db.session.commit()

def create_new_location(place_id, name, address, latitude, longitude):
    location = Location(
        place_id=place_id, 
        name=name, 
        address=address, 
        latitude=latitude, 
        longitude=longitude,
    )
    db.session.add(location)
    db.session.commit()

    return location

def get_location(place_id):
    location = Location.query.filter_by(place_id=place_id).first()
    return location
