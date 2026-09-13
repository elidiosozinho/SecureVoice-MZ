import os
from datetime import datetime
from io import BytesIO

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, send_file, session, url_for
from sqlalchemy import func
from werkzeug.security import check_password_hash

from app.models import Admin, Report, db
from app.pdf import generate_admin_pdf

admin_bp = Blueprint("admin_bp", __name__)

REGIONS = {
    "Norte": {"Cabo Delgado", "Niassa", "Nampula"},
    "Centro": {"Zambézia", "Tete", "Manica", "Sofala"},
    "Sul": {"Inhambane", "Gaza", "Maputo Província", "Maputo Cidade"},
}


def _region_for_province(province):
    for region, provinces in REGIONS.items():
        if province in provinces:
            return region
    return "Não indicada"


@admin_bp.route("/admin/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_bp.admin"))

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
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    session.pop("login_time", None)
    return redirect(url_for("admin_bp.login"))


@admin_bp.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    selected_status = request.args.get("status", "").strip()
    query = Report.query
    if selected_status in {"Recebido", "Em análise", "Resolvido"}:
        query = query.filter_by(status=selected_status)
    reports = query.order_by(Report.created_at.desc()).all()
    total_reports = Report.query.count()
    pending_reports = Report.query.filter(Report.status.in_(["Recebido", "Em análise"])).count()
    resolved_reports = Report.query.filter_by(status="Resolvido").count()
    province_rows = db.session.query(Report.province, func.count(Report.id)).group_by(Report.province).all()
    region_totals = {}
    for province, count in province_rows:
        region = _region_for_province(province)
        region_totals[region] = region_totals.get(region, 0) + count
    top_region = max(region_totals, key=region_totals.get) if region_totals else "—"
    last_report = Report.query.order_by(Report.created_at.desc()).first()
    last_activity = last_report.created_at.strftime("%d/%m/%Y %H:%M") if last_report else "—"
    return render_template(
        "admin.html",
        reports=reports,
        admin_username=session.get("admin_username"),
        login_time=session.get("login_time"),
        total_reports=total_reports,
        last_activity=last_activity,
        selected_status=selected_status,
        pending_reports=pending_reports,
        resolved_reports=resolved_reports,
        top_region=top_region,
    )


@admin_bp.route("/admin/stats")
def stats():
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Não autorizado"}), 401

    province_counts = db.session.query(
        Report.province, func.count(Report.id)
    ).group_by(Report.province).all()
    category_counts = db.session.query(
        Report.category, func.count(Report.id)
    ).group_by(Report.category).all()
    region_counts = {region: 0 for region in REGIONS}
    region_counts["Não indicada"] = 0
    for province, count in province_counts:
        region_counts[_region_for_province(province)] += count
    return jsonify({
        "provinces": {province or "Não indicada": count for province, count in province_counts},
        "regions": region_counts,
        "categories": {category: count for category, count in category_counts},
    })


@admin_bp.route("/admin/report/<int:report_id>/status", methods=["POST"])
def update_status(report_id):
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    report = Report.query.get_or_404(report_id)
    new_status = request.form.get("status")
    admin_notes = request.form.get("admin_notes")
    if new_status in {"Recebido", "Em análise", "Resolvido"}:
        report.status = new_status
    if admin_notes is not None:
        report.admin_notes = admin_notes.strip() or None
    if new_status in {"Recebido", "Em análise", "Resolvido"} or admin_notes is not None:
        db.session.commit()
    return redirect(url_for("admin_bp.admin"))


@admin_bp.route("/admin/download/<int:id>")
def download_admin_pdf(id):
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    report = Report.query.get_or_404(id)
    pdf = generate_admin_pdf(report)
    response = send_file(
        BytesIO(pdf),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"Admin_Report_{report.tracking_code}.pdf",
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@admin_bp.route("/admin/delete/<int:id>", methods=["POST"])
def delete_report(id):
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    report = Report.query.get_or_404(id)
    if report.image_filename:
        upload_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], report.image_filename
        )
        if os.path.isfile(upload_path):
            os.remove(upload_path)
    db.session.delete(report)
    db.session.commit()
    flash("Denúncia eliminada.", "success")
    return redirect(url_for("admin_bp.admin"))
