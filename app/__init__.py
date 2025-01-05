"""app/__init__.py"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mailman import Mail
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth

from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
oauth = OAuth()


from app.models import User, Event

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def create_app(config_class=Config):
    app = Flask(__name__, static_folder="../static")
    
    # configurations
    app.config.from_object(config_class)
        
    # initialisations
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    oauth.init_app(app)

   
    # login configurations
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please login to access this page."
    login_manager.login_message_category = "info"
 
    # register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    return app