"""
SocialPulse AI - KPI Card Components
"""
import streamlit as st
from utils.formatters import format_number, format_percentage
from utils.constants import PRIMARY, SUCCESS, DANGER, TEXT_PRIMARY, TEXT_MUTED


def render_kpi_cards(kpis: dict, comparison: dict = None):
    """Render all 5 KPI cards in a row."""
    configs = [
        ("total_reach", "Total Reach", "👁️"),
        ("total_impressions", "Impressions", "📈"),
        ("total_engagements", "Total Engagements", "💬"),
        ("avg_engagement_rate", "Avg Eng. Rate", "⚡"),
        ("net_follower_growth", "Net Growth", "👥"),
    ]
    cols = st.columns(len(configs))
    for i, (key, label, icon) in enumerate(configs):
        with cols[i]:
            kpi = kpis.get(key, {})
            val = kpi.get("value")
            avail = kpi.get("available", False)
            if key == "avg_engagement_rate":
                disp = format_percentage(val) if avail else "N/A"
            elif key == "net_follower_growth" and avail:
                sign = "+" if val >= 0 else ""
                disp = f"{sign}{format_number(val)}"
            else:
                disp = format_number(val) if avail else "N/A"

            change_html = ""
            if comparison and key in comparison:
                cd = comparison[key]
                if isinstance(cd, dict) and cd.get("available"):
                    pct = cd.get("percentage_change")
                    if pct is not None:
                        clr = SUCCESS if pct >= 0 else DANGER
                        arr = "↑" if pct >= 0 else "↓"
                        change_html = f'<div style="color:{clr};font-size:0.8rem;font-weight:600;margin-top:4px;">{arr} {abs(pct):.1f}%</div>'

            render_single_kpi(label, disp, icon=icon, change_html=change_html)


def render_single_kpi(label: str, value: str, icon: str = "📊", change_html: str = ""):
    """Render one KPI card."""
    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:20px;
                box-shadow:0 2px 8px rgba(0,0,0,0.06);border:1px solid #F0F0F5;height:130px;">
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;">
            <span style="font-size:0.85rem;color:{TEXT_MUTED};font-weight:500;">{label}</span>
            <span>{icon}</span>
        </div>
        <div style="font-size:1.75rem;font-weight:700;color:{TEXT_PRIMARY};line-height:1.2;">{value}</div>
        {change_html}
    </div>
    """, unsafe_allow_html=True)
