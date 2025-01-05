"""app/services/auth_utils.py"""

from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer

from app import db, bcrypt
from app.models import User, Role, Password
from app.services.email import send_email


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


"""Password reset helper functions"""
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(secret_key=current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt="password-reset-salt")

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=expiration)
    except Exception:
        return None
    return email

def send_password_reset_email(user):
    token = generate_reset_token(user.email)
    print(f"generated token to send {token}")
    reset_url = url_for("auth.reset_password", token=token, _external=True)

    print(f"reset url to be sent: {reset_url}")
    recipient = [user.email]
    subject = "Reset Password request"
    body = f"""
        To reset your password, visit the following link:{reset_url}

        If you did not make this request, please ignore this email.
        """
    send_email(recipient, subject, body)