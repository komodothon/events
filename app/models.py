"""app/models.py"""


from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from app import db

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


    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id'), nullable=False, default=3)

    # addition of auth_method to distinguish between OAuth 2.0 and regular signup/login
    auth_method = db.Column(db.String(), nullable=False, default="password")

    # relationships
    password = db.relationship("Password", uselist=False, lazy="joined")
    events_owned = db.relationship("Event", back_populates="owner")
    events_registered_for = db.relationship("Event", secondary="event_registrations", back_populates="registrants")
    role = db.relationship("Role", back_populates="users")


    def __str__(self):
        return self.username

    def __repr__(self):
        return f"<User(id={self.id}, name={self.username}, email={self.email})>"
    
    @classmethod
    def headers(cls):
        return [column.name for column in cls.__table__.columns]
    
    @property
    def role_name(self):
        return self.role.name if self.role else None
    

class Password(db.Model):
    __tablename__ = 'passwords'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    password = db.Column(db.String(), nullable=False)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    owner = db.relationship('User', back_populates='events_owned')
 
    registrants = db.relationship('User', secondary=event_registrations, back_populates='events_registered_for')

    
    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<Event(id={self.id}, name={self.title})>"
    
    @classmethod
    def headers(cls):
        return [column.name for column in cls.__table__.columns]
    
class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(120), nullable=False)

    users = db.relationship("User", back_populates="role")

    def __str__(self):
        return self.name
    


def add_user_roles():
    roles = {
        "admin": "Administrator with full access",
        "moderator": "Moderator with limited admin access",
        "user": "Regular user with basic privileges",
        "guest": "Guest with minimal access"
    }
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            name = role_name
            description = roles[role_name]
            role = Role(name=name, description=description)        
            db.session.add(role)
        db.session.commit()
