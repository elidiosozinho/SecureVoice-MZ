import os
import uuid
from io import BytesIO

from flask import Blueprint, current_app, redirect, render_template, request, send_file, url_for
from flask_mail import Message
from werkzeug.utils import secure_filename

from app.extensions import mail
from app.models import Report, db
from app.pdf import generate_user_pdf

report_bp = Blueprint("report_bp", __name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE = 2 * 1024 * 1024


def _mail_is_configured():
    return bool(
        current_app.config.get("MAIL_USERNAME")
        and current_app.config.get("MAIL_PASSWORD")
    )


def enviar_email(destino, codigo):
    message = Message(
        subject="SecureVoice MZ - Denúncia Recebida",
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[destino],
        body=(
            "A sua denúncia foi recebida com sucesso.\n\n"
            f"Código de acompanhamento: {codigo}\n\n"
            "Guarde este código para verificar o estado da sua denúncia.\n\n"
            "A sua voz faz a diferença.\n"
            "Obrigado por contribuir para um Moçambique melhor.\n\n"
            "SecureVoice MZ\n"
            "Email: securevoicemz@gmail.com\n"
        ),
    )
    mail.send(message)


def enviar_email_com_pdf(destino, codigo, pdf_bytes):
    message = Message(
        subject="SecureVoice MZ - Comprovativo da Denúncia",
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[destino],
        body=(
            "Segue em anexo o comprovativo da sua denúncia.\n\n"
            f"Código: {codigo}\n\n"
            "SecureVoice MZ\n"
            "Email: securevoicemz@gmail.com\n"
        ),
    )
    message.attach(
        filename=f"denuncia_{codigo}.pdf",
        content_type="application/pdf",
        data=pdf_bytes,
    )
    mail.send(message)


def notificar_admin(codigo, categoria, provincia, urgencia):
    admin_address = current_app.config["MAIL_DEFAULT_SENDER"]
    admin_url = f"{current_app.config.get('WEBSITE_URL', '').rstrip('/')}/admin"
    message = Message(
        subject="Nova denúncia recebida - SecureVoice MZ",
        sender=admin_address,
        recipients=[admin_address],
        body=(
            "Nova denúncia recebida.\n\n"
            f"Código: {codigo}\n"
            f"Categoria: {categoria}\n"
            f"Província: {provincia or '—'}\n"
            f"Urgência: {urgencia}\n\n"
            f"Acesse: {admin_url}\n\n"
            "SecureVoice MZ\n"
            "Email: securevoicemz@gmail.com\n"
        ),
    )
    mail.send(message)


def _format_phone_number(phone):
    digits = "".join(character for character in phone if character.isdigit())
    if digits.startswith("258"):
        return f"+{digits}"
    return f"+258{digits}"


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
        province = request.form.get("province", "").strip() or None
        district = request.form.get("district", "").strip() or None
        urgency = request.form.get("urgency", "Média").strip()
        uploaded_file = request.files.get("image")

        if not category or not description or not phone or not email or not province or not district:
            return render_template("report.html", error="Preencha todos os campos de contacto e denúncia.")

        if urgency not in {"Baixa", "Média", "Alta", "Urgente"}:
            urgency = "Média"

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
            province=province,
            district=district,
            image_filename=image_filename,
            tracking_code=tracking_code,
            status="Recebido",
            urgency=urgency,
        )
        db.session.add(report)
        db.session.commit()

        email_sent = False
        receipt_pdf = None
        try:
            receipt_pdf = generate_user_pdf(report)
            if _mail_is_configured():
                enviar_email_com_pdf(report.email, report.tracking_code, receipt_pdf)
                email_sent = True
        except Exception:
            current_app.logger.exception("Não foi possível enviar o comprovativo por email.")

        if _mail_is_configured():
            try:
                notificar_admin(
                    report.tracking_code,
                    report.category,
                    report.province,
                    report.urgency,
                )
            except Exception:
                current_app.logger.exception("Não foi possível enviar a notificação da denúncia.")

        twilio_settings = (
            current_app.config.get("TWILIO_ACCOUNT_SID"),
            current_app.config.get("TWILIO_AUTH_TOKEN"),
            current_app.config.get("TWILIO_PHONE_NUMBER"),
        )
        if report.phone and all(twilio_settings):
            try:
                from twilio.rest import Client

                Client(twilio_settings[0], twilio_settings[1]).messages.create(
                    body=f"SecureVoice MZ: Denúncia recebida. Código: {report.tracking_code}",
                    from_=twilio_settings[2],
                    to=_format_phone_number(report.phone),
                )
            except Exception:
                current_app.logger.exception("Não foi possível enviar o SMS de confirmação.")

        return redirect(
            url_for(
                "main.success",
                tracking_code=tracking_code,
                email_sent="1" if email_sent else "0",
                report_id=report.id,
            )
        )

    return render_template("report.html")


@report_bp.route("/download/<int:id>")
def download_pdf(id):
    report = Report.query.get_or_404(id)
    pdf = generate_user_pdf(report)
    response = send_file(
        BytesIO(pdf),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"SecureVoice_{report.tracking_code}.pdf",
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response
