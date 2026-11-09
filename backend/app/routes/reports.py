"""
PDF Threat Report generation endpoint using ReportLab.
GET /api/reports/weekly  → returns a downloadable PDF with current stats.
"""
import io
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.threat_service import ThreatService

router = APIRouter(prefix="/reports", tags=["Reports"])


def _build_pdf(stats: dict, trends: list, categories: list, sources: list) -> bytes:
    """Build a professional PDF report using ReportLab and return raw bytes."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="ThreatView Weekly Threat Intelligence Report",
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        "H1", parent=styles["Heading1"],
        fontSize=20, textColor=colors.HexColor("#0EA5E9"), spaceAfter=6,
    )
    h2 = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#38BDF8"), spaceAfter=4,
    )
    normal = styles["Normal"]
    small = ParagraphStyle("Small", parent=normal, fontSize=9, textColor=colors.HexColor("#64748B"))

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    story = []

    # ── Title block ──────────────────────────────────────────────────────────
    story.append(Paragraph("ThreatView", h1))
    story.append(Paragraph("Weekly Threat Intelligence Report", styles["Heading2"]))
    story.append(Paragraph(f"Generated: {now}", small))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E293B")))
    story.append(Spacer(1, 0.4 * cm))

    # ── Summary stats table ───────────────────────────────────────────────────
    story.append(Paragraph("Executive Summary", h2))
    stat_data = [
        ["Metric", "Value"],
        ["Total Threat Indicators", str(stats.get("total_indicators", 0))],
        ["New Indicators (Last 24h)", str(stats.get("new_today", 0))],
        ["IP Indicators", str(stats.get("ip_indicators", 0))],
        ["URL Indicators", str(stats.get("url_indicators", 0))],
        ["Last Ingestion", stats.get("last_updated") or "Never"],
    ]
    stat_table = Table(stat_data, colWidths=[10 * cm, 7 * cm])
    stat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.HexColor("#38BDF8")),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#1E293B")),
        ("TEXTCOLOR",  (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#1E293B"), colors.HexColor("#0F172A")]),
        ("PADDING",    (0, 0), (-1, -1), 8),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 0.6 * cm))

    # ── Category breakdown ────────────────────────────────────────────────────
    if categories:
        story.append(Paragraph("Threat Category Distribution", h2))
        cat_data = [["Category", "Count"]] + [
            [c.get("category", "unknown").capitalize(), str(c.get("count", 0))]
            for c in categories[:10]
        ]
        cat_table = Table(cat_data, colWidths=[10 * cm, 7 * cm])
        cat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.HexColor("#38BDF8")),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#1E293B")),
            ("TEXTCOLOR",  (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#1E293B"), colors.HexColor("#0F172A")]),
            ("PADDING",    (0, 0), (-1, -1), 8),
        ]))
        story.append(cat_table)
        story.append(Spacer(1, 0.6 * cm))

    # ── Source feeds ─────────────────────────────────────────────────────────
    if sources:
        story.append(Paragraph("Intelligence Source Attribution", h2))
        src_data = [["Source Feed", "Observations"]] + [
            [s.get("source_name", "Unknown"), str(s.get("count", 0))]
            for s in sources
        ]
        src_table = Table(src_data, colWidths=[10 * cm, 7 * cm])
        src_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.HexColor("#38BDF8")),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#1E293B")),
            ("TEXTCOLOR",  (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#1E293B"), colors.HexColor("#0F172A")]),
            ("PADDING",    (0, 0), (-1, -1), 8),
        ]))
        story.append(src_table)
        story.append(Spacer(1, 0.6 * cm))

    # ── 30-day trend summary ──────────────────────────────────────────────────
    if trends:
        story.append(Paragraph("30-Day Ingestion Trend (last 10 days)", h2))
        trend_data = [["Date", "New Indicators"]] + [
            [t.get("date", ""), str(t.get("count", 0))]
            for t in trends[-10:]
        ]
        trend_table = Table(trend_data, colWidths=[10 * cm, 7 * cm])
        trend_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.HexColor("#38BDF8")),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#1E293B")),
            ("TEXTCOLOR",  (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#1E293B"), colors.HexColor("#0F172A")]),
            ("PADDING",    (0, 0), (-1, -1), 8),
        ]))
        story.append(trend_table)
        story.append(Spacer(1, 0.4 * cm))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#334155")))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "ThreatView Cybersecurity Intelligence Platform · Confidential · For internal use only.",
        small,
    ))

    doc.build(story)
    return buf.getvalue()


@router.get("/weekly")
def download_weekly_report(db: Session = Depends(get_db)):
    """
    Generate and stream a PDF threat intelligence report with current database stats.
    """
    stats = ThreatService.get_dashboard_stats(db)
    trends = ThreatService.get_trends(db, days=30)
    categories = ThreatService.get_category_distribution(db)
    sources = ThreatService.get_source_distribution(db)

    pdf_bytes = _build_pdf(stats, trends, categories, sources)

    now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    filename = f"threatview_report_{now_str}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
