import os
import uuid

from flask import Flask
from sqlalchemy import inspect, text

from .config import Config
from .extensions import mail
from .models import Admin, Report, db
from .routes import admin_bp, main, report_bp

def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "default_local_fallback_secret_key_98765"
    )

    db.init_app(app)
    mail.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

        admin_username = app.config.get("ADMIN_USERNAME")
        admin_password = app.config.get("ADMIN_PASSWORD")
        if admin_username and admin_password:
            admin_user = Admin.query.filter_by(username=admin_username).first()
            if admin_user is None:
                admin_user = Admin(username=admin_username)
                db.session.add(admin_user)
            admin_user.set_password(admin_password)
            db.session.commit()

        inspector = inspect(db.engine)
        columns = [column["name"] for column in inspector.get_columns("report")]
        if "tracking_code" not in columns:
            db.session.execute(text("ALTER TABLE report ADD COLUMN tracking_code VARCHAR(50)"))
            db.session.commit()

        columns = [column["name"] for column in inspector.get_columns("report")]
        for column_name, column_type in [
            ("phone", "VARCHAR(50)"),
            ("email", "VARCHAR(255)"),
            ("province", "VARCHAR(100)"),
            ("district", "VARCHAR(100)"),
            ("status", "VARCHAR(50) DEFAULT 'Recebido'"),
            ("urgency", "VARCHAR(50) DEFAULT 'Média'"),
            ("admin_notes", "TEXT"),
        ]:
            if column_name not in columns:
                db.session.execute(text(f"ALTER TABLE report ADD COLUMN {column_name} {column_type}"))
        db.session.commit()

        db.session.execute(
            text("UPDATE report SET urgency = 'Média' WHERE urgency IS NULL OR urgency = '' OR urgency = 'Normal'")
        )
        db.session.commit()

        reports_without_code = Report.query.filter((Report.tracking_code.is_(None)) | (Report.tracking_code == "")).all()
        for report in reports_without_code:
            report.tracking_code = uuid.uuid4().hex[:8].upper()
        db.session.commit()

    return app
