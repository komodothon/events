"""app/services/auth_utils.py"""

from app import db, bcrypt
from app.models import User, Role, Password

def get_all_users():
    users = User.query.all()
    return users

def get_all_roles():
    roles = Role.query.all()
    return roles

def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

def create_new_user(username, email, password):
    
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    
    # User to be created and id assigned in database before Password instance is created
    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.flush() # Ensures `new_user.id` is assigned before proceeding
    
    new_password = Password(user_id=new_user.id, password=hashed_password)
    db.session.add(new_password)

    db.session.commit()

    return new_user

def authenticate_user(username, password):

    user = db.session.query(User).filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password.password, password):
        return user  
    else:
        return None

def change_password(user, password):
    hashed_password = hash_password(password)

    user.password.password = hashed_password

    db.session.commit()


def hash_password(password):
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    return hashed_password

def check_password_hash(input_password, hashed_password):
    return bcrypt.check_password_hash(input_password, hashed_password)
