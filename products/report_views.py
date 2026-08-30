from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from .models import ComplianceScan


def scan_report_pdf(request, scan_id):
    scan = get_object_or_404(ComplianceScan, id=scan_id)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'ReportTitle', parent=styles['Title'], fontSize=18, spaceAfter=6
    )
    story.append(Paragraph("Legal Metrology Compliance Report", title_style))
    story.append(Paragraph(
        "Generated under Legal Metrology (Packaged Commodities) Rules, 2011",
        styles['Normal']
    ))
    story.append(Spacer(1, 16))

    # --- Product / scan metadata ---
    meta_data = [
        ["Product Name", scan.product.name],
        ["Manufacturer (declared)", scan.product.manufacturer_name or "Not specified"],
        ["Category", scan.product.category or "Not specified"],
        ["Scan Date", scan.scanned_at.strftime("%d %B %Y, %H:%M")],
        ["Scanned By", str(scan.scanned_by) if scan.scanned_by else "N/A"],
    ]
    meta_table = Table(meta_data, colWidths=[2 * inch, 4 * inch])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 16))

    # --- Compliance verdict ---
    status = scan.compliance_status
    status_color = colors.green if status == "COMPLIANT" else (
        colors.red if status == "NON_COMPLIANT" else colors.grey
    )
    status_style = ParagraphStyle(
        'Status', parent=styles['Heading2'], textColor=status_color
    )
    story.append(Paragraph(f"Compliance Status: {status}", status_style))
    story.append(Spacer(1, 10))

    # --- Violations ---
    if scan.violations:
        story.append(Paragraph("Violations Found", styles['Heading3']))
        for i, v in enumerate(scan.violations, 1):
            story.append(Paragraph(f"{i}. {v}", styles['Normal']))
        story.append(Spacer(1, 12))
    else:
        story.append(Paragraph("No violations found in the checked declarations.", styles['Normal']))
        story.append(Spacer(1, 12))

    # --- Extracted fields table ---
    story.append(Paragraph("Extracted Declarations", styles['Heading3']))

    fields = scan.extracted_fields or {}
    mrp = fields.get("mrp")
    license_no = fields.get("license_no")
    manufacturer = fields.get("manufacturer")
    dates = fields.get("dates", [])

    mfg_date = next((d["value"] for d in dates if d.get("label") == "mfg_date"), "Not found")
    exp_date = next((d["value"] for d in dates if d.get("label") == "expiry_date"), "Not found")

    field_data = [
        ["Field", "Extracted Value"],
        ["MRP", mrp["value"] if mrp else "Not found"],
        ["Manufacturing Date", mfg_date],
        ["Expiry Date", exp_date],
        ["License Number", license_no["value"] if license_no else "Not found"],
        ["Manufacturer Address", (manufacturer[:150] + "...") if manufacturer and len(manufacturer) > 150 else (manufacturer or "Not found")],
    ]
    field_table = Table(field_data, colWidths=[2 * inch, 4 * inch])
    field_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(field_table)
    story.append(Spacer(1, 16))

    # --- Scanned image ---
    try:
        story.append(Paragraph("Scanned Label Image", styles['Heading3']))
        story.append(Spacer(1, 6))
        img = Image(scan.image.path, width=3 * inch, height=4 * inch, kind='proportional')
        story.append(img)
    except Exception:
        story.append(Paragraph("(Image could not be embedded)", styles['Normal']))

    story.append(Spacer(1, 20))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
    story.append(Paragraph(
        "This report is system-generated based on automated OCR extraction and rule-based "
        "checks. It covers a subset of Legal Metrology (Packaged Commodities) Rules, 2011 "
        "declarations (Rule 6) and does not constitute a complete regulatory compliance audit.",
        footer_style
    ))

    doc.build(story)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"compliance_report_scan_{scan.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
