"""
SocialPulse AI - Page 6: Export & PDF Reports
Professional report generation and download page.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.session_manager import (
    init_session_state, get_dataframe, is_data_loaded, get_platform, get_dataset_info
)
from utils.constants import (
    PRIMARY, SUCCESS, SECONDARY, TEXT_PRIMARY, TEXT_MUTED
)
from utils.formatters import format_date_range, format_number
from services.analytics_engine import (
    calculate_kpis, calculate_format_performance, get_top_posts
)
from services.comparison_engine import compare_periods
from services.pdf_generator import generate_pdf_report


def render():
    init_session_state()

    if not is_data_loaded():
        st.warning("📁 No dataset loaded. Please upload a CSV file first.")
        if st.button("Go to Upload Page"):
            st.session_state.current_page = "CSV Upload & Prep"
            st.rerun()
        return

    df = get_dataframe()
    mapped = st.session_state.mapped_columns
    platform = get_platform()
    info = get_dataset_info()

    st.markdown("# 📄 Export & PDF Reports")
    st.markdown(f"<p style='color:{TEXT_MUTED};font-size:0.9rem;'>Generate and download a comprehensive performance report as a professional PDF.</p>", unsafe_allow_html=True)

    # ── Report Preview ──────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:24px;border:1px solid #E8E8F0;margin-bottom:20px;">
        <h3 style="font-size:1.1rem;margin-bottom:16px;">📋 Report Contents Preview</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div style="display:flex;align-items:center;gap:8px;font-size:0.88rem;">
                <span style="color:{SUCCESS};">✅</span> SocialPulse AI Branding & Cover
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.88rem;">
                <span style="color:{SUCCESS};">✅</span> Report Title & Platform
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.88rem;">
                <span style="color:{SUCCESS};">✅</span> Reporting Period & Date Range
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.88rem;">
                <span style="color:{SUCCESS};">✅</span> Dataset Summary & Health
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.88rem;">
                <span style="color:{SUCCESS};">✅</span> KPI Overview Table
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.88rem;">
                <span style="color:{SUCCESS};">✅</span> Engagement Metrics Breakdown
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.88rem;">
                <span style="color:{SUCCESS};">✅</span> Period Comparison Analysis
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.88rem;">
                <span style="color:{SUCCESS};">✅</span> Top Performing Posts
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.88rem;">
                <span style="color:{SUCCESS};">✅</span> AI-Generated Summary & Insights
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.88rem;">
                <span style="color:{SUCCESS};">✅</span> Actionable Recommendations
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.88rem;">
                <span style="color:{SUCCESS};">✅</span> Data Limitations & Assumptions
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.88rem;">
                <span style="color:{SUCCESS};">✅</span> Page Numbers & Footer
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Report Configuration ────────────────────────────────────────────
    st.markdown(f"<h4 style='font-size:1rem;'>⚙️ Report Configuration</h4>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div style="background:white;border-radius:10px;padding:16px;border:1px solid #E8E8F0;">
            <div style="font-size:0.78rem;color:{TEXT_MUTED};margin-bottom:4px;">PLATFORM</div>
            <div style="font-size:1.1rem;font-weight:600;color:{TEXT_PRIMARY};">
                {'📸' if platform == 'Instagram' else '💼'} {platform}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        dr = info.get("date_range")
        dr_str = format_date_range(dr[0], dr[1]) if dr else "Not available"
        st.markdown(f"""
        <div style="background:white;border-radius:10px;padding:16px;border:1px solid #E8E8F0;">
            <div style="font-size:0.78rem;color:{TEXT_MUTED};margin-bottom:4px;">REPORTING PERIOD</div>
            <div style="font-size:0.95rem;font-weight:600;color:{TEXT_PRIMARY};">📅 {dr_str}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div style="background:white;border-radius:10px;padding:16px;border:1px solid #E8E8F0;">
            <div style="font-size:0.78rem;color:{TEXT_MUTED};margin-bottom:4px;">DATASET</div>
            <div style="font-size:0.95rem;font-weight:600;color:{TEXT_PRIMARY};">
                📊 {info.get('rows', 0):,} posts from {info.get('name', 'dataset')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Quick KPI Summary ───────────────────────────────────────────────
    kpis = calculate_kpis(df, mapped)

    st.markdown(f"<h4 style='font-size:1rem;'>📊 Data Summary (will be included in PDF)</h4>", unsafe_allow_html=True)

    kpi_cols = st.columns(5)
    kpi_items = [
        ("total_reach", "Total Reach"),
        ("total_impressions", "Impressions"),
        ("total_engagements", "Engagements"),
        ("avg_engagement_rate", "Avg ER"),
        ("net_follower_growth", "Net Growth"),
    ]
    for i, (key, label) in enumerate(kpi_items):
        with kpi_cols[i]:
            kpi = kpis.get(key, {})
            val = kpi.get("value")
            if key == "avg_engagement_rate":
                disp = f"{val:.2f}%" if val is not None else "N/A"
            else:
                disp = format_number(val) if val is not None else "N/A"
            st.metric(label, disp)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Generate & Download Button ──────────────────────────────────────
    col_btn, col_info = st.columns([2, 3])

    with col_btn:
        if st.button("📥 Generate & Download PDF Report", type="primary",
                      use_container_width=True, key="gen_pdf"):
            with st.spinner("Generating professional PDF report..."):
                try:
                    comparison = compare_periods(df, mapped)
                    format_perf = calculate_format_performance(df, mapped)
                    top_posts = get_top_posts(df, mapped, sort_by="engagements", n=10)
                    ai_insights = st.session_state.get("ai_insights", {})

                    # Generate if no AI insights cached
                    if not ai_insights:
                        from services.ai_insights import generate_ai_insights
                        from services.analytics_engine import calculate_posting_frequency, get_peak_performance
                        posting_freq = calculate_posting_frequency(df, mapped)
                        peak_perf = get_peak_performance(df, mapped)
                        ai_insights = generate_ai_insights(
                            kpis, comparison, format_perf, posting_freq, peak_perf, platform
                        )
                        st.session_state.ai_insights = ai_insights

                    dataset_info_pdf = {
                        "total_rows": info.get("rows", 0),
                        "platform": platform,
                        "source_file": info.get("name", ""),
                        "available_metrics": info.get("available_metrics", []),
                        "missing_metrics": info.get("missing_metrics", []),
                    }

                    pdf_bytes = generate_pdf_report(
                        kpis=kpis,
                        comparison=comparison,
                        format_performance=format_perf,
                        top_posts=top_posts,
                        ai_insights=ai_insights,
                        mapped_columns=mapped,
                        platform=platform,
                        date_range=info.get("date_range"),
                        dataset_info=dataset_info_pdf,
                    )

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"SocialPulse_AI_Report_{platform}_{timestamp}.pdf"

                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True,
                        key="download_pdf"
                    )
                    st.success(f"✅ Report generated successfully! Click above to download.")

                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
                    st.exception(e)

    with col_info:
        st.markdown(f"""
        <div style="background:#F0F0FF;border-radius:10px;padding:16px;font-size:0.85rem;">
            <b>📋 Report includes:</b><br/>
            • Professional cover page with SocialPulse AI branding<br/>
            • Complete KPI overview and engagement breakdown<br/>
            • Period comparison analysis<br/>
            • Top performing posts table<br/>
            • AI-generated summary and recommendations<br/>
            • Data limitations and methodology notes<br/>
            • Page numbers on every page
        </div>
        """, unsafe_allow_html=True)

    # ── Export History ───────────────────────────────────────────────────
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="padding:12px 16px;background:#F9F9FF;border-radius:8px;font-size:0.82rem;color:{TEXT_MUTED};">
        <b>ℹ️ Note:</b> PDF reports reflect the currently loaded dataset and any active filters.
        Each generated report includes the exact timestamp of generation and the data source file name
        for audit trail purposes.
    </div>
    """, unsafe_allow_html=True)
