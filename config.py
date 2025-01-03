"""config.py"""

from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Secret key for session management 
    SECRET_KEY = "app_secret_key"

    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///events.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email server configurations (for email features)
    MAIL_SERVER = "sandbox.smtp.mailtrap.io"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = ('JVNK events', 'support@jvnkevents.com')
    # MAIL_SUPPRESS_SEND = False
    # MAIL_MAX_EMAILS = None
    # MAIL_ASCII_ATTACHMENTS = False

    # Google OAuth 2.0 credentials
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

class DevConfig(Config):
    DEBUG = True
    MAIL_DEBUG = True


class ProdConfig(Config):
    DEBUG = False
    MAIL_DEBUG = False
    MAIL_SERVER = "smtp.gmail.com"
