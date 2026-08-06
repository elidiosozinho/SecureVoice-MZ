from flask import Blueprint, redirect, render_template, request, url_for

from app.models import Report

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/success")
def success():
    tracking_code = request.args.get("tracking_code")
    return render_template("success.html", tracking_code=tracking_code)


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

    return render_template("verify.html", report=report, error=error)
