import os
import uuid

from flask import Blueprint, current_app, redirect, render_template, request, url_for, flash
from werkzeug.utils import secure_filename

from app.models import Report, db

report_bp = Blueprint("report_bp", __name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE = 2 * 1024 * 1024


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _save_upload(uploaded_file):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    ext = os.path.splitext(secure_filename(uploaded_file.filename))[1].lower()
    if not _allowed_file(uploaded_file.filename):
        raise ValueError("Tipo de ficheiro não permitido.")

    if uploaded_file.content_length and uploaded_file.content_length > MAX_FILE_SIZE:
        raise ValueError("O ficheiro é demasiado grande.")

    filename = f"{uuid.uuid4().hex}{ext}"
    uploaded_file.save(os.path.join(upload_folder, filename))
    return filename


@report_bp.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        phone = request.form.get("phone", "").strip() or None
        email = request.form.get("email", "").strip() or None
        uploaded_file = request.files.get("image")

        if not category or not description:
            return render_template("report.html", error="Preencha a categoria e a descrição.")

        image_filename = None
        if uploaded_file and uploaded_file.filename:
            try:
                image_filename = _save_upload(uploaded_file)
            except ValueError as exc:
                return render_template("report.html", error=str(exc))

        tracking_code = uuid.uuid4().hex[:8].upper()
        report = Report(
            category=category,
            description=description,
            phone=phone,
            email=email,
            image_filename=image_filename,
            tracking_code=tracking_code,
            status="Recebido",
        )
        db.session.add(report)
        db.session.commit()

        return redirect(url_for("main.success", tracking_code=tracking_code))

    return render_template("report.html")
