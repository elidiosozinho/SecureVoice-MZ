import os
from datetime import datetime
from io import BytesIO

from flask import current_app, render_template


def _logo_path():
    return "logo.png"


def _render_pdf(template_name, report):
    try:
        from weasyprint import HTML

        html = render_template(
            template_name,
            report=report,
            logo_path=_logo_path(),
            export_date=datetime.now().strftime("%d/%m/%Y %H:%M"),
        )
        return HTML(
            string=html,
            base_url=os.path.abspath("app/static/"),
        ).write_pdf()
    except (ImportError, OSError):
        current_app.logger.warning(
            "WeasyPrint indisponível; usando gerador PDF compatível."
        )
        return _fallback_pdf(report, template_name == "pdf_admin.html")


def generate_user_pdf(report):
    return _render_pdf("pdf_receipt.html", report)


def generate_admin_pdf(report):
    return _render_pdf("pdf_admin.html", report)


def _fallback_pdf(report, admin_report=False):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader

    buffer = BytesIO()
    document = canvas.Canvas(buffer, pagesize=A4)
    _, page_height = A4
    title = "RELATÓRIO OFICIAL" if admin_report else "COMPROVATIVO DE DENÚNCIA"
    document.setTitle(f"{title} {report.tracking_code}")
    left = 52
    width = A4[0] - 104
    y_position = page_height - 54
    logo_path = os.path.join(current_app.root_path, "static", "logo.png")
    if os.path.exists(logo_path):
        document.drawImage(ImageReader(logo_path), A4[0] - 142, page_height - 82, width=86, height=38, preserveAspectRatio=True, mask="auto")
    document.setFillColor(colors.HexColor("#0b3d91"))
    document.setFont("Helvetica-Bold", 18)
    document.drawString(left, y_position, "SecureVoice MZ")
    document.setFillColor(colors.HexColor("#64748b"))
    document.setFont("Helvetica", 9)
    document.drawString(left, y_position - 16, "A sua voz. Um Moçambique melhor")
    document.setStrokeColor(colors.HexColor("#0b3d91"))
    document.setLineWidth(2)
    document.line(left, y_position - 28, left + width, y_position - 28)
    y_position -= 72
    document.setFillColor(colors.HexColor("#0b3d91"))
    document.setFont("Helvetica-Bold", 17)
    document.drawCentredString(A4[0] / 2, y_position, title)
    y_position -= 34
    document.setFillColor(colors.HexColor("#e6f0ff"))
    document.roundRect(left, y_position - 38, width, 38, 5, fill=1, stroke=0)
    document.setFillColor(colors.HexColor("#0b3d91"))
    document.setFont("Helvetica-Bold", 19)
    document.drawCentredString(A4[0] / 2, y_position - 25, report.tracking_code)
    y_position -= 62

    def section_heading(text):
        nonlocal y_position
        document.setFillColor(colors.HexColor("#0b3d91"))
        document.setFont("Helvetica-Bold", 11)
        document.drawString(left, y_position, text)
        y_position -= 18

    def wrapped_text(text, max_chars=92):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 > max_chars:
                lines.append(current)
                current = word
            else:
                current = f"{current} {word}".strip()
        if current:
            lines.append(current)
        return lines or [""]

    section_heading("Informações")
    document.setFillColor(colors.HexColor("#f7f7f7"))
    document.roundRect(left, y_position - 72, width, 72, 5, fill=1, stroke=0)
    document.setFillColor(colors.HexColor("#172033"))
    document.setFont("Helvetica", 9)
    info = [
        f"Categoria: {report.category}", f"Província: {report.province or '—'}",
        f"Distrito: {report.district or '—'}", f"Data: {report.created_at.strftime('%d/%m/%Y %H:%M')}",
        f"Urgência: {report.urgency or 'Média'}", f"Status: {report.status}",
    ]
    for index, line in enumerate(info):
        x = left + 12 if index % 2 == 0 else left + width / 2
        y = y_position - 18 - (index // 2) * 18
        document.drawString(x, y, line[:48])
    y_position -= 92
    section_heading("Descrição")
    description_lines = wrapped_text(report.description)
    box_height = max(44, 16 * len(description_lines) + 18)
    document.setFillColor(colors.HexColor("#fafafa"))
    document.roundRect(left, y_position - box_height, width, box_height, 4, fill=1, stroke=0)
    document.setFillColor(colors.HexColor("#172033"))
    document.setFont("Helvetica", 9)
    for index, line in enumerate(description_lines):
        document.drawString(left + 12, y_position - 18 - index * 16, line)
    y_position -= box_height + 18
    if report.admin_notes or admin_report:
        section_heading("Resposta da Equipa" if not admin_report else "Gestão Administrativa")
        note_text = report.admin_notes or "Sem notas internas."
        note_lines = wrapped_text(note_text)
        box_height = max(40, 16 * len(note_lines) + 16)
        document.setFillColor(colors.HexColor("#fff8e8"))
        document.roundRect(left, y_position - box_height, width, box_height, 4, fill=1, stroke=0)
        document.setFillColor(colors.HexColor("#172033"))
        document.setFont("Helvetica", 9)
        for index, line in enumerate(note_lines):
            document.drawString(left + 12, y_position - 16 - index * 16, line)
        y_position -= box_height + 18
    if not admin_report:
        trust_y = max(y_position - 4, 96)
        document.setFillColor(colors.HexColor("#f5f5f5"))
        document.roundRect(left, trust_y - 34, width, 34, 4, fill=1, stroke=0)
        document.setFillColor(colors.HexColor("#64748b"))
        document.setFont("Helvetica", 8)
        document.drawCentredString(A4[0] / 2, trust_y - 14, "Este sistema protege a sua identidade.")
        document.drawCentredString(A4[0] / 2, trust_y - 25, "Nenhuma informação pessoal é exposta sem consentimento.")
    document.setFillColor(colors.HexColor("#64748b"))
    document.setFont("Helvetica", 8)
    document.drawCentredString(A4[0] / 2, 36, "SecureVoice MZ - A sua voz. A sua segurança. | Email: securevoicemz@gmail.com")
    document.save()
    buffer.seek(0)
    return buffer.read()
