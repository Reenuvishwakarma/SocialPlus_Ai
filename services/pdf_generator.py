"""
PDF Report Generator for SocialPulse AI.

Generates professional A4 PDF reports with branded styling,
KPI tables, engagement breakdowns, top posts, AI insights,
and optional chart images.
"""

import io
import textwrap
from datetime import datetime
from typing import Optional

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch, mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from utils.formatters import format_number, format_percentage

# ---------------------------------------------------------------------------
# Brand colours
# ---------------------------------------------------------------------------
PRIMARY = HexColor("#4648D4")
SUCCESS = HexColor("#00885D")
TEXT_COLOR = HexColor("#141B2B")
MUTED = HexColor("#767586")
CARD_BG = HexColor("#F9F9FF")
WHITE = colors.white
LIGHT_GREY = HexColor("#E8E8F0")
TABLE_HEADER_BG = PRIMARY
TABLE_ALT_ROW = CARD_BG

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 1.8 * cm
RIGHT_MARGIN = 1.8 * cm
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN


# ---------------------------------------------------------------------------
# Helpers – safe value access
# ---------------------------------------------------------------------------

def _safe_get(data: Optional[dict], key: str, default="N/A"):
    """Return *data[key]* if available, otherwise *default*."""
    if data is None:
        return default
    val = data.get(key, default)
    if val is None:
        return default
    return val


def _safe_num(data: Optional[dict], key: str, fmt: bool = True):
    """Return a formatted number from *data[key]*, or 'N/A'."""
    raw = _safe_get(data, key, None)
    if raw is None:
        return "N/A"
    try:
        num = float(raw)
        return format_number(num) if fmt else str(num)
    except (TypeError, ValueError):
        return str(raw)


def _safe_pct(data: Optional[dict], key: str):
    """Return a formatted percentage from *data[key]*, or 'N/A'."""
    raw = _safe_get(data, key, None)
    if raw is None:
        return "N/A"
    try:
        return format_percentage(float(raw))
    except (TypeError, ValueError):
        return str(raw)


def _truncate(text: str, max_len: int = 80) -> str:
    """Truncate *text* to *max_len* characters, adding '…' if trimmed."""
    if not text:
        return ""
    text = str(text).replace("\n", " ").replace("\r", " ")
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


# ---------------------------------------------------------------------------
# Paragraph styles
# ---------------------------------------------------------------------------

def _build_styles() -> dict:
    """Return a dict of named ParagraphStyles used throughout the report."""
    base = getSampleStyleSheet()
    styles: dict[str, ParagraphStyle] = {}

    styles["title"] = ParagraphStyle(
        "CoverTitle",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=32,
        leading=38,
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    styles["subtitle"] = ParagraphStyle(
        "CoverSubtitle",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=14,
        leading=20,
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    styles["section_heading"] = ParagraphStyle(
        "SectionHeading",
        parent=base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=22,
        textColor=PRIMARY,
        spaceBefore=18,
        spaceAfter=8,
        borderPadding=(0, 0, 4, 0),
    )
    styles["sub_heading"] = ParagraphStyle(
        "SubHeading",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=TEXT_COLOR,
        spaceBefore=10,
        spaceAfter=4,
    )
    styles["body"] = ParagraphStyle(
        "BodyText",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=TEXT_COLOR,
        spaceAfter=6,
    )
    styles["body_muted"] = ParagraphStyle(
        "BodyMuted",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=MUTED,
        spaceAfter=4,
    )
    styles["bullet"] = ParagraphStyle(
        "Bullet",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=TEXT_COLOR,
        leftIndent=18,
        bulletIndent=6,
        spaceAfter=3,
    )
    styles["table_header"] = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=WHITE,
        alignment=TA_CENTER,
    )
    styles["table_cell"] = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=TEXT_COLOR,
        alignment=TA_CENTER,
    )
    styles["table_cell_left"] = ParagraphStyle(
        "TableCellLeft",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=TEXT_COLOR,
        alignment=TA_LEFT,
    )
    styles["footer"] = ParagraphStyle(
        "Footer",
        fontName="Helvetica",
        fontSize=7,
        leading=10,
        textColor=MUTED,
        alignment=TA_CENTER,
    )
    return styles


# ---------------------------------------------------------------------------
# Page template callbacks
# ---------------------------------------------------------------------------

def _page_footer(canvas, doc):
    """Draw page number and branding footer on every page."""
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(
        PAGE_WIDTH / 2,
        1.0 * cm,
        f"SocialPulse AI Report  •  Page {doc.page}",
    )
    canvas.restoreState()


def _cover_background(canvas, doc):
    """Draw the branded cover page background."""
    canvas.saveState()
    # Full-page primary background
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=True, stroke=False)
    # Decorative lighter band at top
    canvas.setFillColor(HexColor("#5B5DE0"))
    canvas.rect(0, PAGE_HEIGHT - 4 * cm, PAGE_WIDTH, 4 * cm, fill=True, stroke=False)
    canvas.restoreState()


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _build_cover(
    styles: dict,
    platform: str,
    date_range: Optional[tuple],
) -> list:
    """Return flowables for the cover page."""
    elements: list = []
    elements.append(Spacer(1, 7 * cm))
    elements.append(Paragraph("SocialPulse AI", styles["title"]))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(
        Paragraph("Social Media Analytics Report", styles["subtitle"])
    )
    elements.append(Spacer(1, 1.2 * cm))
    elements.append(Paragraph(f"Platform: {platform}", styles["subtitle"]))

    if date_range and len(date_range) == 2:
        start, end = date_range
        elements.append(
            Paragraph(f"Reporting Period: {start} – {end}", styles["subtitle"])
        )
    elements.append(Spacer(1, 0.6 * cm))
    gen_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    elements.append(
        Paragraph(f"Generated: {gen_date}", styles["subtitle"])
    )
    elements.append(PageBreak())
    return elements


def _section_line() -> list:
    """Return a thin horizontal rule as a table-based separator."""
    t = Table([[""]],colWidths=[CONTENT_WIDTH], rowHeights=[1])
    t.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, LIGHT_GREY),
    ]))
    return [t, Spacer(1, 4)]


def _build_executive_summary(
    styles: dict,
    kpis: dict,
    ai_insights: dict,
    platform: str,
) -> list:
    """Executive Summary section."""
    elements: list = []
    elements.append(Paragraph("Executive Summary", styles["section_heading"]))
    elements.extend(_section_line())

    summary_text = _safe_get(ai_insights, "summary", None)
    if summary_text:
        elements.append(Paragraph(str(summary_text), styles["body"]))
    else:
        reach = _safe_num(kpis, "total_reach")
        eng = _safe_num(kpis, "total_engagements")
        er = _safe_pct(kpis, "avg_engagement_rate")
        elements.append(
            Paragraph(
                f"This report provides a comprehensive analysis of {platform} "
                f"performance during the selected reporting period. "
                f"Total reach was <b>{reach}</b>, with <b>{eng}</b> total "
                f"engagements and an average engagement rate of <b>{er}</b>.",
                styles["body"],
            )
        )
    elements.append(Spacer(1, 6))
    return elements


def _make_table(
    headers: list[str],
    rows: list[list],
    col_widths: Optional[list] = None,
    left_align_first: bool = False,
    extra_commands: Optional[list] = None,
) -> Table:
    """Build a styled Table with alternating row colours."""
    style_commands = [
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        # Body rows
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        # Grid
        ("GRID", (0, 0), (-1, -1), 0.4, LIGHT_GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]
    if left_align_first:
        style_commands.append(("ALIGN", (0, 0), (0, -1), "LEFT"))

    # Alternating row colours
    for i in range(1, len(rows) + 1):
        if i % 2 == 0:
            style_commands.append(
                ("BACKGROUND", (0, i), (-1, i), TABLE_ALT_ROW)
            )

    if extra_commands:
        style_commands.extend(extra_commands)

    all_rows = [headers] + rows
    t = Table(all_rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle(style_commands))
    return t


def _build_kpi_table(styles: dict, kpis: dict) -> list:
    """KPI Overview table."""
    elements: list = []
    elements.append(Paragraph("KPI Overview", styles["section_heading"]))
    elements.extend(_section_line())

    headers = ["Metric", "Value"]
    rows = [
        ["Total Reach", _safe_num(kpis, "total_reach")],
        ["Impressions", _safe_num(kpis, "total_impressions")],
        ["Engagements", _safe_num(kpis, "total_engagements")],
        ["Avg Engagement Rate", _safe_pct(kpis, "avg_engagement_rate")],
        ["Net Follower Growth", _safe_num(kpis, "net_growth")],
    ]
    col_widths = [CONTENT_WIDTH * 0.55, CONTENT_WIDTH * 0.45]
    t = _make_table(headers, rows, col_widths, left_align_first=True)
    elements.append(t)
    elements.append(Spacer(1, 12))
    return elements


def _build_comparison_table(styles: dict, comparison: dict) -> list:
    """Period Comparison table (current vs previous with % change)."""
    elements: list = []
    elements.append(
        Paragraph("Period Comparison", styles["section_heading"])
    )
    elements.extend(_section_line())

    if not comparison:
        elements.append(
            Paragraph(
                "No comparison data available for this report.",
                styles["body_muted"],
            )
        )
        elements.append(Spacer(1, 12))
        return elements

    headers = ["Metric", "Current", "Previous", "Change (%)"]

    metric_keys = [
        ("Reach", "reach"),
        ("Impressions", "impressions"),
        ("Engagements", "engagements"),
        ("Engagement Rate", "engagement_rate"),
        ("Follower Growth", "net_growth"),
    ]

    rows: list[list[str]] = []
    for label, key in metric_keys:
        current_val = _safe_get(comparison, f"{key}_current", None)
        previous_val = _safe_get(comparison, f"{key}_previous", None)
        change_val = _safe_get(comparison, f"{key}_change", None)

        # Also check nested dict style: comparison[key] = {current, previous, change}
        nested = _safe_get(comparison, key, None)
        if isinstance(nested, dict):
            current_val = current_val or nested.get("current")
            previous_val = previous_val or nested.get("previous")
            change_val = change_val or nested.get("change")

        def _fmt(v):
            if v is None:
                return "N/A"
            try:
                return format_number(float(v))
            except (TypeError, ValueError):
                return str(v)

        def _fmt_change(v):
            if v is None:
                return "N/A"
            try:
                return format_percentage(float(v))
            except (TypeError, ValueError):
                return str(v)

        rows.append([label, _fmt(current_val), _fmt(previous_val), _fmt_change(change_val)])

    col_widths = [
        CONTENT_WIDTH * 0.30,
        CONTENT_WIDTH * 0.23,
        CONTENT_WIDTH * 0.23,
        CONTENT_WIDTH * 0.24,
    ]
    t = _make_table(headers, rows, col_widths, left_align_first=True)
    elements.append(t)
    elements.append(Spacer(1, 12))
    return elements


def _build_engagement_breakdown(
    styles: dict,
    kpis: dict,
    format_performance,  # DataFrame | None
) -> list:
    """Engagement Metrics breakdown: Likes, Comments, Shares, Saves."""
    elements: list = []
    elements.append(
        Paragraph("Engagement Metrics Breakdown", styles["section_heading"])
    )
    elements.extend(_section_line())

    # Try to pull totals from kpis first, then aggregate from DataFrame
    engagement_metrics = {
        "Likes": _safe_get(kpis, "total_likes", None),
        "Comments": _safe_get(kpis, "total_comments", None),
        "Shares": _safe_get(kpis, "total_shares", None),
        "Saves": _safe_get(kpis, "total_saves", None),
    }

    # If a DataFrame is provided, try summing columns for missing values
    if format_performance is not None and isinstance(format_performance, pd.DataFrame):
        col_map = {
            "Likes": ["likes", "Likes", "like_count"],
            "Comments": ["comments", "Comments", "comment_count"],
            "Shares": ["shares", "Shares", "share_count"],
            "Saves": ["saves", "Saves", "save_count"],
        }
        for metric, candidates in col_map.items():
            if engagement_metrics[metric] is None:
                for col_name in candidates:
                    if col_name in format_performance.columns:
                        try:
                            engagement_metrics[metric] = (
                                format_performance[col_name]
                                .astype(float)
                                .sum()
                            )
                        except (TypeError, ValueError):
                            pass
                        break

    headers = ["Metric", "Total"]
    rows: list[list[str]] = []
    grand_total = 0
    for metric, val in engagement_metrics.items():
        if val is not None:
            try:
                num = float(val)
                grand_total += num
                rows.append([metric, format_number(num)])
            except (TypeError, ValueError):
                rows.append([metric, str(val)])
        else:
            rows.append([metric, "N/A"])

    rows.append(["Total Engagements", format_number(grand_total) if grand_total else "N/A"])

    col_widths = [CONTENT_WIDTH * 0.55, CONTENT_WIDTH * 0.45]
    total_row_idx = len(rows)  # 0-indexed header + rows → last data row
    extra = [
        ("FONTNAME", (0, total_row_idx), (-1, total_row_idx), "Helvetica-Bold"),
        ("BACKGROUND", (0, total_row_idx), (-1, total_row_idx), LIGHT_GREY),
    ]
    t = _make_table(headers, rows, col_widths, left_align_first=True, extra_commands=extra)

    elements.append(t)
    elements.append(Spacer(1, 12))
    return elements


def _build_top_posts(
    styles: dict,
    top_posts,  # DataFrame | None
    mapped_columns: dict,
) -> list:
    """Top Performing Posts table (5-10 posts)."""
    elements: list = []
    elements.append(
        Paragraph("Top Performing Posts", styles["section_heading"])
    )
    elements.extend(_section_line())

    if top_posts is None or (isinstance(top_posts, pd.DataFrame) and top_posts.empty):
        elements.append(
            Paragraph("No post-level data available.", styles["body_muted"])
        )
        elements.append(Spacer(1, 12))
        return elements

    df = top_posts.copy()

    # Resolve mapped column names with safe fallbacks
    caption_col = mapped_columns.get("caption", "caption")
    type_col = mapped_columns.get("type", "type")
    date_col = mapped_columns.get("date", "date")
    reach_col = mapped_columns.get("reach", "reach")
    engagements_col = mapped_columns.get("engagements", "engagements")
    er_col = mapped_columns.get("engagement_rate", "engagement_rate")

    # Limit to top 10
    df = df.head(10)

    headers = ["#", "Caption", "Type", "Date", "Reach", "Eng.", "ER (%)"]

    rows: list[list[str]] = []
    for idx, (_, row) in enumerate(df.iterrows(), start=1):
        caption = _truncate(str(row.get(caption_col, "")), 45)
        post_type = str(row.get(type_col, "—"))
        date_val = str(row.get(date_col, "—"))
        try:
            reach_val = format_number(float(row.get(reach_col, 0)))
        except (TypeError, ValueError):
            reach_val = str(row.get(reach_col, "—"))
        try:
            eng_val = format_number(float(row.get(engagements_col, 0)))
        except (TypeError, ValueError):
            eng_val = str(row.get(engagements_col, "—"))
        try:
            er_val = format_percentage(float(row.get(er_col, 0)))
        except (TypeError, ValueError):
            er_val = str(row.get(er_col, "—"))

        rows.append([str(idx), caption, post_type, date_val, reach_val, eng_val, er_val])

    col_widths = [
        CONTENT_WIDTH * 0.05,  # #
        CONTENT_WIDTH * 0.30,  # Caption
        CONTENT_WIDTH * 0.10,  # Type
        CONTENT_WIDTH * 0.14,  # Date
        CONTENT_WIDTH * 0.14,  # Reach
        CONTENT_WIDTH * 0.13,  # Eng
        CONTENT_WIDTH * 0.14,  # ER
    ]
    extra = [("ALIGN", (1, 1), (1, -1), "LEFT")]
    t = _make_table(headers, rows, col_widths, left_align_first=False, extra_commands=extra)

    elements.append(t)
    elements.append(Spacer(1, 12))
    return elements


def _build_ai_insights(styles: dict, ai_insights: dict) -> list:
    """AI-Generated Insights section."""
    elements: list = []
    elements.append(
        Paragraph("AI-Generated Insights", styles["section_heading"])
    )
    elements.extend(_section_line())

    if not ai_insights:
        elements.append(
            Paragraph("No AI insights available.", styles["body_muted"])
        )
        elements.append(Spacer(1, 12))
        return elements

    # Summary
    summary = _safe_get(ai_insights, "summary", None)
    if summary:
        elements.append(Paragraph("<b>Summary</b>", styles["sub_heading"]))
        elements.append(Paragraph(str(summary), styles["body"]))
        elements.append(Spacer(1, 4))

    # Recommendations
    recs = _safe_get(ai_insights, "recommendations", None)
    if recs:
        elements.append(
            Paragraph("<b>Recommendations</b>", styles["sub_heading"])
        )
        if isinstance(recs, list):
            for rec in recs:
                elements.append(
                    Paragraph(f"• {rec}", styles["bullet"])
                )
        else:
            elements.append(Paragraph(str(recs), styles["body"]))
        elements.append(Spacer(1, 4))

    # Strengths
    strengths = _safe_get(ai_insights, "strengths", None)
    if strengths:
        elements.append(
            Paragraph("<b>Strengths</b>", styles["sub_heading"])
        )
        if isinstance(strengths, list):
            for s in strengths:
                elements.append(
                    Paragraph(f"• {s}", styles["bullet"])
                )
        else:
            elements.append(Paragraph(str(strengths), styles["body"]))
        elements.append(Spacer(1, 4))

    # Weaknesses
    weaknesses = _safe_get(ai_insights, "weaknesses", None)
    if weaknesses:
        elements.append(
            Paragraph("<b>Weaknesses</b>", styles["sub_heading"])
        )
        if isinstance(weaknesses, list):
            for w in weaknesses:
                elements.append(
                    Paragraph(f"• {w}", styles["bullet"])
                )
        else:
            elements.append(Paragraph(str(weaknesses), styles["body"]))
        elements.append(Spacer(1, 4))

    elements.append(Spacer(1, 12))
    return elements


def _build_data_limitations(
    styles: dict,
    dataset_info: Optional[dict],
) -> list:
    """Data Limitations and Assumptions section."""
    elements: list = []
    elements.append(
        Paragraph("Data Limitations & Assumptions", styles["section_heading"])
    )
    elements.extend(_section_line())

    bullets: list[str] = []

    if dataset_info:
        total_rows = _safe_get(dataset_info, "total_rows", None)
        if total_rows is not None:
            bullets.append(
                f"Dataset contained <b>{total_rows}</b> rows at time of analysis."
            )
        missing = _safe_get(dataset_info, "missing_columns", None)
        if missing:
            if isinstance(missing, list):
                bullets.append(
                    "The following expected columns were missing from the dataset: "
                    + ", ".join(str(c) for c in missing)
                    + "."
                )
            else:
                bullets.append(f"Missing columns note: {missing}")
        date_gaps = _safe_get(dataset_info, "date_gaps", None)
        if date_gaps:
            bullets.append(f"Date gaps detected: {date_gaps}")

        custom_notes = _safe_get(dataset_info, "notes", None)
        if custom_notes:
            if isinstance(custom_notes, list):
                bullets.extend(str(n) for n in custom_notes)
            else:
                bullets.append(str(custom_notes))

    # Default caveats
    bullets.extend([
        "Engagement rate calculations use the formula: (Engagements / Reach) × 100.",
        "Metrics reflect the data as uploaded and may not account for delayed platform updates.",
        "AI-generated insights are based on statistical patterns and should be validated with domain expertise.",
    ])

    for b in bullets:
        elements.append(Paragraph(f"• {b}", styles["bullet"]))

    elements.append(Spacer(1, 12))
    return elements


def _build_chart_section(
    styles: dict,
    chart_images: list,
) -> list:
    """Optional section: embed chart images (Plotly exports etc.)."""
    if not chart_images:
        return []

    elements: list = []
    elements.append(
        Paragraph("Visual Analytics", styles["section_heading"])
    )
    elements.extend(_section_line())

    for chart in chart_images:
        # Each chart can be: bytes, a file path string, or a BytesIO
        if isinstance(chart, dict):
            img_data = chart.get("image")
            caption = chart.get("caption", "")
        else:
            img_data = chart
            caption = ""

        try:
            if isinstance(img_data, bytes):
                img_buf = io.BytesIO(img_data)
            elif isinstance(img_data, io.BytesIO):
                img_buf = img_data
                img_buf.seek(0)
            elif isinstance(img_data, str):
                # Treat as file path
                img_buf = img_data
            else:
                continue

            img = Image(img_buf, width=CONTENT_WIDTH, height=CONTENT_WIDTH * 0.56)
            img.hAlign = "CENTER"
            elements.append(img)

            if caption:
                elements.append(
                    Paragraph(str(caption), styles["body_muted"])
                )
            elements.append(Spacer(1, 10))
        except Exception:
            # Skip unreadable images silently
            continue

    return elements


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def generate_pdf_report(
    kpis: dict,
    comparison: dict,
    format_performance,  # DataFrame or None
    top_posts,  # DataFrame or None
    ai_insights: dict,
    mapped_columns: dict,
    platform: str = "Instagram",
    date_range: tuple = None,
    dataset_info: dict = None,
    chart_images: list = None,
) -> bytes:
    """Generate a branded SocialPulse AI PDF report and return it as bytes.

    Parameters
    ----------
    kpis : dict
        Aggregated KPI values (total_reach, total_impressions,
        total_engagements, avg_engagement_rate, net_growth, etc.).
    comparison : dict
        Period-over-period comparison data with current/previous/change
        values per metric.
    format_performance : DataFrame | None
        Per-format (or per-post) performance breakdown DataFrame.
    top_posts : DataFrame | None
        Top performing posts DataFrame (sorted descending by engagements
        or engagement rate).
    ai_insights : dict
        AI-generated insights dict with keys: summary, recommendations,
        strengths, weaknesses.
    mapped_columns : dict
        Mapping of logical column names (caption, type, date, reach,
        engagements, engagement_rate) to actual DataFrame column names.
    platform : str
        Social media platform name (default ``"Instagram"``).
    date_range : tuple | None
        ``(start_date_str, end_date_str)`` for the reporting period.
    dataset_info : dict | None
        Metadata about the dataset (total_rows, missing_columns, etc.)
        used in the Data Limitations section.
    chart_images : list | None
        Optional list of chart image objects to embed. Each item may be
        raw ``bytes``, a ``BytesIO``, a file-path string, or a dict
        ``{"image": <data>, "caption": "..."}``.

    Returns
    -------
    bytes
        The finished PDF document as an in-memory byte string.
    """
    # Ensure mutable defaults are safe
    kpis = kpis or {}
    comparison = comparison or {}
    ai_insights = ai_insights or {}
    mapped_columns = mapped_columns or {}
    chart_images = chart_images or []

    buf = io.BytesIO()
    styles = _build_styles()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
        title="SocialPulse AI Report",
        author="SocialPulse AI",
    )

    # ----- Collect flowables -----
    story: list = []

    # 1. Cover page
    story.extend(_build_cover(styles, platform, date_range))

    # 2. Executive Summary
    story.extend(_build_executive_summary(styles, kpis, ai_insights, platform))

    # 3. KPI Overview
    story.extend(_build_kpi_table(styles, kpis))

    # 4. Period Comparison
    story.extend(_build_comparison_table(styles, comparison))

    # 5. Engagement Metrics Breakdown
    story.extend(
        _build_engagement_breakdown(styles, kpis, format_performance)
    )

    # 6. Top Performing Posts
    story.extend(_build_top_posts(styles, top_posts, mapped_columns))

    # 7. Charts (optional)
    if chart_images:
        story.extend(_build_chart_section(styles, chart_images))

    # 8. AI-Generated Insights
    story.extend(_build_ai_insights(styles, ai_insights))

    # 9. Data Limitations & Assumptions
    story.extend(_build_data_limitations(styles, dataset_info))

    # ----- Build PDF -----
    # Use the cover background only on the first page; standard footer
    # on all pages.

    def _first_page(canvas, doc):
        _cover_background(canvas, doc)

    def _later_pages(canvas, doc):
        _page_footer(canvas, doc)

    doc.build(story, onFirstPage=_first_page, onLaterPages=_later_pages)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes
