"""app/__init__.py"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

from app.models import User
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def create_app():
    app = Flask(__name__, static_folder="../static")
    
    # configurations
    app.config['SECRET_KEY'] = "app_secret_key"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
    # initialisations
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # login configurations
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please login to access this page."
    login_manager.login_message_category = "info"
 
    # register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    return app