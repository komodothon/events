"""routes/__init__.py"""

from flask import Blueprint

from .auth import auth_bp
from .events import events_bp
from .api import api_bp
from .admin import admin_bp

def register_blueprints(app):

    """
    Register all blueprints in the Flask app
    """
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(events_bp, url_prefix="/")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/admin")

