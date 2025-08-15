# PDF Generation for Billing Service
import io
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors

def generate_invoice_pdf(invoice_data: Dict[str, Any]) -> io.BytesIO:
    """Generate PDF for an invoice"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_invoice_pdf(c, invoice_data)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def _draw_invoice_pdf(c: canvas.Canvas, inv: Dict[str, Any]):
    """Draw invoice content on PDF canvas"""
    width, height = A4
    margin = 15 * mm
    y = height - margin

    # Header
    c.setFillColor(colors.HexColor('#1f2937'))  # gray-800
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, y, "CYBERSEC TOOLKIT PRO 2025")
    y -= 10 * mm
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(margin, y, f"Facture: {inv.get('invoice_id')}")
    y -= 6 * mm
    c.drawString(margin, y, f"Client: {inv.get('client_id')}")
    y -= 6 * mm
    c.drawString(margin, y, f"Créée le: {inv.get('created_at','')[:19].replace('T',' ')}  •  Échéance: {(inv.get('due_date','')[:19].replace('T',' '))}")
    y -= 10 * mm

    # Table header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Description")
    c.drawString(margin + 110*mm, y, "Qté")
    c.drawString(margin + 130*mm, y, "PU")
    c.drawString(margin + 160*mm, y, "Montant")
    y -= 5 * mm
    c.line(margin, y, width - margin, y)
    y -= 4 * mm

    c.setFont("Helvetica", 11)
    total = 0.0
    for it in inv.get('items', []):
        if y < 40 * mm:  # new page if needed
            c.showPage()
            y = height - margin
        qte = float(it.get('quantity', 0))
        pu = float(it.get('unit_price', 0.0))
        montant = qte * pu
        total += montant
        c.drawString(margin, y, str(it.get('description',''))[:60])
        c.drawRightString(margin + 125*mm, y, f"{qte:g}")
        c.drawRightString(margin + 155*mm, y, f"{pu:,.2f}")
        c.drawRightString(width - margin, y, f"{montant:,.2f}")
        y -= 6 * mm

    # Total
    y -= 6 * mm
    c.line(margin, y, width - margin, y)
    y -= 8 * mm
    c.setFont("Helvetica-Bold", 12)
    currency = inv.get('currency', 'EUR')
    c.drawRightString(width - margin, y, f"Total {currency}: {total:,.2f}")
    y -= 12 * mm

    # Footer
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor('#6b7280'))  # gray-500
    c.drawString(margin, 20 * mm, "Document généré automatiquement par CyberSec Toolkit Pro 2025")