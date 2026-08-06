import os
from datetime import timedelta


BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = "super_secret_key_123"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'securevoice.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
