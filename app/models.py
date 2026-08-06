from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)
    tracking_code = db.Column(db.String(50), nullable=False, unique=True)
    status = db.Column(db.String(50), default="Recebido", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Report {self.id} - {self.category}>"
