from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()

# association table
event_registrations = db.Table(
    'event_registrations',
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.username}, email={self.email})>"
    
    @classmethod
    def headers(cls):
        return [column.name for column in cls.__table__.columns]
    

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    owner = db.relationship('User', backref='events_owned')
 
    registrants = db.relationship('User', secondary=event_registrations, backref='events_registered_for')

    def __repr__(self):
        return f"<Event(id={self.id}, name={self.title})>"
    
    @classmethod
    def headers(cls):
        return [column.name for column in cls.__table__.columns]
    
