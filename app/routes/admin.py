from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from app.models import Admin, Report, db

admin_bp = Blueprint("admin_bp", __name__)


@admin_bp.route("/admin/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session["admin_logged_in"] = True
            session["admin_username"] = username
            session["login_time"] = datetime.now().strftime("%H:%M")
            session.permanent = True
            flash("Bem-vindo, administrador.", "success")
            return redirect("/admin")
        error = "Credenciais inválidas. Tente novamente."
    return render_template("admin_login.html", error=error)


@admin_bp.route("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))


@admin_bp.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    reports = Report.query.order_by(Report.created_at.desc()).all()
    total_reports = Report.query.count()
    last_report = Report.query.order_by(Report.created_at.desc()).first()
    last_activity = last_report.created_at.strftime("%d/%m/%Y %H:%M") if last_report else "—"
    return render_template(
        "admin.html",
        reports=reports,
        admin_username=session.get("admin_username"),
        login_time=session.get("login_time"),
        total_reports=total_reports,
        last_activity=last_activity,
    )


@admin_bp.route("/admin/report/<int:report_id>/status", methods=["POST"])
def update_status(report_id):
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    report = Report.query.get_or_404(report_id)
    new_status = request.form.get("status")
    if new_status in {"Recebido", "Em análise", "Resolvido"}:
        report.status = new_status
        db.session.commit()
    return redirect(url_for("admin_bp.admin"))
