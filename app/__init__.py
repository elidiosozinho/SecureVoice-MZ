import uuid

from flask import Flask
from sqlalchemy import inspect, text

from .config import Config
from .models import Admin, Report, db
from .routes import admin_bp, main, report_bp


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

        admin_user = Admin.query.filter_by(username="elidio_sozinho_admin").first()
        if admin_user is None:
            admin_user = Admin(username="elidio_sozinho_admin")
            db.session.add(admin_user)
        admin_user.set_password("Sozinho17@2003")
        db.session.commit()

        # ------------------------------------------
        # ADMIN LOGIN DETAILS:
        # Username: elidio_sozinho_admin
        # Password: Sozinho17@2003
        # Login URL: /admin/login
        # Stored in:
        # - Admin model -> app/models.py
        # - Login logic -> app/routes/admin.py
        # - Template -> templates/admin_login.html
        # ------------------------------------------

        inspector = inspect(db.engine)
        columns = [column["name"] for column in inspector.get_columns("report")]
        if "tracking_code" not in columns:
            db.session.execute(text("ALTER TABLE report ADD COLUMN tracking_code VARCHAR(50)"))
            db.session.commit()

        columns = [column["name"] for column in inspector.get_columns("report")]
        for column_name, column_type in [("phone", "VARCHAR(50)"), ("email", "VARCHAR(255)")]:
            if column_name not in columns:
                db.session.execute(text(f"ALTER TABLE report ADD COLUMN {column_name} {column_type}"))
        db.session.commit()

        reports_without_code = Report.query.filter((Report.tracking_code.is_(None)) | (Report.tracking_code == "")).all()
        for report in reports_without_code:
            report.tracking_code = uuid.uuid4().hex[:8].upper()
        db.session.commit()

    return app
