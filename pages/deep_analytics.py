"""
SocialPulse AI - Page 3: Deep Analytics
Advanced analytics workspace with detailed metric analysis and visualizations.
"""
import streamlit as st
import pandas as pd
from utils.session_manager import (
    init_session_state, get_dataframe, is_data_loaded, get_platform
)
from utils.constants import (
    STD_DATE, STD_REACH, STD_IMPRESSIONS, STD_LIKES, STD_COMMENTS,
    STD_SHARES, STD_SAVES, STD_FOLLOWERS, STD_POST_TYPE, STD_ENGAGEMENT_RATE,
    PRIMARY, SECONDARY, SUCCESS, DANGER, TEXT_PRIMARY, TEXT_MUTED
)
from utils.formatters import format_number, format_percentage
from services.analytics_engine import (
    calculate_kpis, calculate_daily_metrics, calculate_format_performance,
    get_engagement_distribution, get_peak_performance, calculate_posting_frequency
)
from services.comparison_engine import compare_periods
from components.charts import (
    render_performance_trend, render_engagement_donut, render_format_bar_chart,
    render_follower_growth_chart, render_comparison_chart, render_metric_over_time
)
from components.filters import render_analytics_filters, apply_filters


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

    st.markdown("# Performance Trends & Deep Metric Analysis")
    st.markdown(f"<p style='color:{TEXT_MUTED};font-size:0.88rem;'>Explore daily, weekly, and engagement trending curves, format-level comparisons.</p>", unsafe_allow_html=True)

    # ── Filters ─────────────────────────────────────────────────────────
    filters = render_analytics_filters(df, mapped)
    filtered_df = apply_filters(df, mapped, filters)

    # ── KPI Overview ────────────────────────────────────────────────────
    kpis = calculate_kpis(filtered_df, mapped)
    comparison = compare_periods(filtered_df, mapped)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    kpi_items = [
        ("total_reach", "Total Reach", "👁️", "number"),
        ("total_impressions", "Impressions", "📈", "number"),
        ("avg_engagement_rate", "Avg Eng. Rate", "⚡", "pct"),
        ("total_engagements", "Total Engagements", "💬", "number"),
    ]

    cols = st.columns(len(kpi_items))
    for i, (key, label, icon, fmt) in enumerate(kpi_items):
        with cols[i]:
            kpi = kpis.get(key, {})
            val = kpi.get("value")
            avail = kpi.get("available", False)
            if fmt == "pct":
                disp = format_percentage(val) if avail else "N/A"
            else:
                disp = format_number(val) if avail else "N/A"

            # Comparison
            comp = comparison.get(key, {})
            change_html = ""
            if isinstance(comp, dict) and comp.get("available"):
                pct = comp.get("percentage_change")
                if pct is not None:
                    clr = SUCCESS if pct >= 0 else DANGER
                    arr = "↑" if pct >= 0 else "↓"
                    change_html = f'<span style="color:{clr};font-size:0.78rem;font-weight:600;">{arr} {abs(pct):.1f}%</span>'

            note = ""
            if key == "total_reach":
                ppd = calculate_posting_frequency(filtered_df, mapped)
                if ppd.get("posts_per_day"):
                    note = f"<div style='font-size:0.7rem;color:{TEXT_MUTED};'>Algorithm-fueled distribution</div>"

            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:18px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.05);border:1px solid #F0F0F5;">
                <div style="font-size:0.78rem;color:{TEXT_MUTED};margin-bottom:4px;">{icon} {label}</div>
                <div style="font-size:1.6rem;font-weight:700;color:{TEXT_PRIMARY};">{disp}</div>
                {change_html}{note}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Trend Charts ────────────────────────────────────────────────────
    st.markdown(f"""
    <h3 style="font-size:1.1rem;margin-bottom:4px;">📊 Reach & Impressions Metrics (Daily Trend)</h3>
    <p style="color:{TEXT_MUTED};font-size:0.8rem;">Composite multi-metric analysis – Reach, Impressions, Likes, Followers, and community interactions.</p>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Daily", "📊 Weekly", "📉 Cumulative"])

    with tab1:
        daily = calculate_daily_metrics(filtered_df, mapped)
        render_performance_trend(daily, "Daily")

    with tab2:
        from services.analytics_engine import calculate_weekly_metrics
        weekly = calculate_weekly_metrics(filtered_df, mapped)
        render_performance_trend(weekly, "Weekly")

    with tab3:
        daily2 = calculate_daily_metrics(filtered_df, mapped)
        render_performance_trend(daily2, "Cumulative")

    # ── Individual Metric Charts ────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    mc1, mc2 = st.columns(2)
    with mc1:
        st.markdown(f"<h4 style='font-size:1rem;'>Engagement Trends by Format</h4>", unsafe_allow_html=True)
        format_df = calculate_format_performance(filtered_df, mapped)
        if format_df is not None and not format_df.empty and "eng_rate_by_reach" in format_df.columns:
            render_format_bar_chart(format_df)
        else:
            st.info("Post type data not available for format analysis.")

    with mc2:
        st.markdown(f"<h4 style='font-size:1rem;'>Engagement Distribution</h4>", unsafe_allow_html=True)
        eng_dist = get_engagement_distribution(filtered_df, mapped)
        render_engagement_donut(eng_dist)

    # ── Follower Growth ─────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    fol_col = mapped.get(STD_FOLLOWERS)
    if fol_col and fol_col in filtered_df.columns:
        st.markdown(f"<h4 style='font-size:1rem;'>👥 Follower Growth Over Time</h4>", unsafe_allow_html=True)
        render_follower_growth_chart(filtered_df, mapped)

    # ── Period Comparison ───────────────────────────────────────────────
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='font-size:1rem;'>📊 Period Comparison (Current vs Previous Half)</h4>", unsafe_allow_html=True)
    render_comparison_chart(comparison)

    # ── Format Performance Table ────────────────────────────────────────
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <h4 style="font-size:1rem;">📋 Format Performance Correlation Matrix</h4>
    <p style="color:{TEXT_MUTED};font-size:0.8rem;">
        Shows verifiable breakdown of actual from {len(filtered_df)} verifiable sourced entries.
    </p>
    """, unsafe_allow_html=True)

    if format_df is not None and not format_df.empty:
        # Build display table
        display_data = []
        for idx, row in format_df.iterrows():
            entry = {"Post Type": str(idx), "Posts": int(row.get("post_count", 0))}
            reach_sum = None
            for c in format_df.columns:
                if "reach" in c.lower() and "sum" in c.lower():
                    reach_sum = row[c]
                    break
            if reach_sum is not None:
                entry["Total Reach"] = f"{reach_sum:,.0f}"
            imp_sum = None
            for c in format_df.columns:
                if "impression" in c.lower() and "sum" in c.lower():
                    imp_sum = row[c]
                    break
            if imp_sum is not None:
                entry["Impressions"] = f"{imp_sum:,.0f}"

            # Engagement components
            likes_sum = shares_sum = comments_sum = saves_sum = 0
            for c in format_df.columns:
                cl = c.lower()
                if "like" in cl and "sum" in cl:
                    likes_sum = row[c]
                elif "share" in cl and "sum" in cl or "repost" in cl and "sum" in cl:
                    shares_sum = row[c]
                elif "comment" in cl and "sum" in cl:
                    comments_sum = row[c]
                elif "save" in cl and "sum" in cl:
                    saves_sum = row[c]

            entry["Likes"] = f"{likes_sum:,.0f}"
            entry["Shares"] = f"{shares_sum:,.0f}"
            entry["Comments"] = f"{comments_sum:,.0f}"

            if "total_engagements" in row.index:
                entry["Engagements"] = f"{row['total_engagements']:,.0f}"
            if "eng_rate_by_reach" in row.index:
                entry["Eng Rate"] = f"{row['eng_rate_by_reach']:.2f}%"
            if "pct_contribution" in row.index:
                entry["% Share"] = f"{row['pct_contribution']:.1f}%"

            display_data.append(entry)

        if display_data:
            st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)
    else:
        st.info("Add a 'Post Type' column to see format-level breakdown.")

    # ── Assumptions Disclaimer ──────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-top:24px;padding:12px 16px;background:#F0F0FF;border-radius:8px;
                border-left:3px solid {PRIMARY};font-size:0.8rem;color:{TEXT_PRIMARY};">
        <b>⚠️ AGGREGATE DATA NOTICE:</b> All reach and impression values are post-level aggregates.
        They do not represent unique account-level audience counts. Period comparison splits the dataset
        at the midpoint of the available date range.
    </div>
    """, unsafe_allow_html=True)
