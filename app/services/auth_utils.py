"""app/services/auth_utils.py"""

from app import db, bcrypt
from app.models import User, Role

def get_all_users():
    users = User.query.all()
    return users

def get_all_roles():
    roles = Role.query.all()
    return roles

def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)

def create_new_user(username, email, password):
    
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    
    new_user = User(username=username, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return new_user

def authenticate_user(username, password):

    user = db.session.query(User).filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return user  
    else:
        return None

def hash_password(password):
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    return hashed_password

def check_password_hash(input_password, hashed_password):
    return bcrypt.check_password_hash(input_password, hashed_password)
