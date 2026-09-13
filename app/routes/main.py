from flask import Blueprint, redirect, render_template, request, url_for

from app.models import Report, db

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/success")
def success():
    tracking_code = request.args.get("tracking_code")
    email_sent = request.args.get("email_sent") == "1"
    report_id = request.args.get("report_id", type=int)
    return render_template(
        "success.html",
        tracking_code=tracking_code,
        email_sent=email_sent,
        report_id=report_id,
    )


@main.route("/verificar", methods=["GET", "POST"])
def verificar():
    report = None
    error = None

    if request.method == "POST":
        tracking_code = request.form.get("tracking_code", "").strip().upper()
        if tracking_code:
            report = Report.query.filter_by(tracking_code=tracking_code).first()
            if not report:
                error = "Código inválido"
        else:
            error = "Introduza um código válido"

    return render_template(
        "verify.html",
        report=report,
        report_id=report.id if report else None,
        error=error,
    )


@main.route("/test-db")
def test_db():
    try:
        reports = Report.query.count()
        return f"DB OK - {reports} reports found"
    except Exception as exc:
        db.session.rollback()
        return f"DB ERROR: {exc}", 500
