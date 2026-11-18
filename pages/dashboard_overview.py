"""
SocialPulse AI - Page 1: Dashboard Overview
Main dashboard showing KPIs, trends, format performance, top posts, and AI synthesis.
"""
import streamlit as st
import pandas as pd
from utils.session_manager import (
    get_dataframe, get_mapped_col, has_column, get_platform,
    is_data_loaded, get_dataset_info, init_session_state
)
from utils.constants import (
    STD_DATE, STD_REACH, STD_IMPRESSIONS, STD_LIKES,
    STD_COMMENTS, STD_SHARES, STD_SAVES, STD_FOLLOWERS,
    STD_POST_TYPE, STD_POST, STD_ENGAGEMENT_RATE,
    PRIMARY, SUCCESS, SECONDARY, DANGER, TEXT_PRIMARY, TEXT_MUTED
)
from utils.formatters import format_number, format_percentage, format_date_range, format_change, truncate_text
from services.analytics_engine import (
    calculate_kpis, calculate_daily_metrics, calculate_weekly_metrics,
    calculate_format_performance, get_top_posts, get_peak_performance,
    calculate_save_reach_ratio, calculate_comment_like_ratio,
    get_engagement_distribution
)
from services.comparison_engine import compare_periods, get_comparison_summary


def render():
    init_session_state()
    
    if not is_data_loaded():
        _render_empty_state()
        return
    
    df = get_dataframe()
    mapped = st.session_state.mapped_columns
    platform = get_platform()
    
    # Calculate all metrics
    kpis = calculate_kpis(df, mapped)
    comparison = compare_periods(df, mapped) if st.session_state.comparison_enabled else {}
    comp_summary = get_comparison_summary(comparison) if comparison else {}
    
    # ── Status Strip ────────────────────────────────────────────────────
    _render_status_strip(platform, df, mapped, kpis, comparison, comp_summary)
    
    # ── KPI Cards ───────────────────────────────────────────────────────
    _render_kpi_cards(kpis, comparison)
    
    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
    
    # ── Performance Trends & Format Performance ─────────────────────────
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        _render_performance_trends(df, mapped)
    
    with col_right:
        _render_format_performance(df, mapped, kpis)
    
    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
    
    # ── Top Posts & AI Synthesis ─────────────────────────────────────────
    col_left2, col_right2 = st.columns([1, 1])
    
    with col_left2:
        _render_top_posts_preview(df, mapped)
    
    with col_right2:
        _render_ai_synthesis_preview(kpis, comparison, df, mapped, platform)


def _render_empty_state():
    """Show empty state when no data is loaded."""
    st.markdown("""
    <div style="text-align: center; padding: 80px 20px;">
        <div style="font-size: 4rem; margin-bottom: 16px;">📊</div>
        <h2 style="color: #141B2B; margin-bottom: 8px;">Welcome to SocialPulse AI</h2>
        <p style="color: #767586; font-size: 1.1rem; margin-bottom: 32px;">
            Upload your social media analytics CSV to get started with performance analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📁 Upload CSV Data", use_container_width=True, type="primary"):
            st.session_state.current_page = "CSV Upload & Prep"
            st.rerun()
    
    # Show sample data option
    st.markdown("---")
    st.markdown("##### Or try with sample data:")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("📸 Load Instagram Sample", use_container_width=True):
            _load_sample_data("instagram")
    with c2:
        if st.button("💼 Load LinkedIn Sample", use_container_width=True):
            _load_sample_data("linkedin")


def _load_sample_data(platform_key: str):
    """Load sample data for quick demo."""
    import os
    from services.csv_loader import load_csv_from_path
    from services.column_mapper import auto_map_columns
    from services.data_cleaner import clean_dataset, calculate_missing_engagement_rate
    from services.data_validator import validate_dataset
    from utils.session_manager import set_dataframe, set_platform, set_mapped_columns, set_date_range, set_validation_results
    from utils.helpers import get_date_range
    
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in dir() else os.getcwd()
    
    if platform_key == "instagram":
        path = os.path.join(base, "data", "sample_instagram_data.csv")
        set_platform("Instagram")
    else:
        path = os.path.join(base, "data", "sample_linkedin_data.csv")
        set_platform("LinkedIn")
    
    df, error = load_csv_from_path(path)
    if error:
        st.error(f"Could not load sample data: {error}")
        return
    
    mapped, unmapped = auto_map_columns(df)
    set_mapped_columns(mapped)
    
    validation = validate_dataset(df, mapped)
    set_validation_results(validation)
    
    cleaned = clean_dataset(df, mapped)
    cleaned = calculate_missing_engagement_rate(cleaned, mapped)
    
    date_start, date_end = get_date_range(cleaned, mapped.get(STD_DATE, ""))
    if date_start and date_end:
        set_date_range(date_start, date_end)
    
    name = "sample_instagram_data.csv" if platform_key == "instagram" else "sample_linkedin_data.csv"
    set_dataframe(cleaned, name)
    st.session_state.raw_df = df
    st.rerun()


def _render_status_strip(platform, df, mapped, kpis, comparison, comp_summary):
    """Render the status and insight strip at top of dashboard."""
    dataset_info = get_dataset_info()
    date_range_str = ""
    if dataset_info["date_range"]:
        date_range_str = format_date_range(dataset_info["date_range"][0], dataset_info["date_range"][1])
    
    # Overall change
    overall_change_html = ""
    if comparison:
        reach_comp = comparison.get("total_reach", {})
        if reach_comp.get("available"):
            pct = reach_comp.get("percentage_change", 0)
            color = SUCCESS if pct and pct >= 0 else DANGER
            arrow = "↑" if pct and pct >= 0 else "↓"
            bg_color = "#E6F4ED" if pct and pct >= 0 else "#FDE8EA"
            overall_change_html = f'<div style="display:inline-flex;align-items:center;gap:6px;padding:6px 14px;background:{bg_color};border-radius:20px;"><span style="color:{color};font-weight:600;">{arrow} {abs(pct or 0):.1f}% prev 30d</span></div>'

    num_recs = 0
    if st.session_state.ai_insights:
        recs = st.session_state.ai_insights.get("recommendations", [])
        num_recs = len(recs)

    recs_badge = f'<div style="color:#E8E8F0;">|</div><div style="font-size:0.85rem;color:{PRIMARY};">⚡ {num_recs} actionable AI recommendations available</div>' if num_recs > 0 else ''

    status_html = (
        f'<div style="display:flex;align-items:center;gap:16px;padding:12px 20px;'
        f'background:white;border-radius:10px;margin-bottom:20px;border:1px solid #E8E8F0;flex-wrap:wrap;">'
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="width:8px;height:8px;border-radius:50%;background:{SUCCESS};display:inline-block;"></span>'
        f'<span style="font-size:0.85rem;color:{TEXT_MUTED};">ACTIVE CHANNEL:</span>'
        f'<span style="font-size:0.85rem;font-weight:600;color:{TEXT_PRIMARY};">@{dataset_info.get("name", "dataset")} ({platform})</span>'
        f'</div>'
        f'<div style="color:#E8E8F0;">|</div>'
        f'<div style="display:flex;align-items:center;gap:6px;">'
        f'<span style="font-size:0.85rem;color:{TEXT_MUTED};">📅</span>'
        f'<span style="font-size:0.85rem;color:{TEXT_PRIMARY};">{date_range_str}</span>'
        f'</div>'
        f'{recs_badge}'
        f'<div style="flex:1;"></div>'
        f'{overall_change_html}'
        f'</div>'
    )
    st.markdown(status_html, unsafe_allow_html=True)


def _render_kpi_cards(kpis, comparison):
    """Render the 5 main KPI cards."""
    cols = st.columns(5)
    
    kpi_configs = [
        ("total_reach", "Total Reach", "👁️"),
        ("total_impressions", "Impressions", "📈"),
        ("total_engagements", "Total Engagements", "💬"),
        ("avg_engagement_rate", "Avg Eng. Rate", "⚡"),
        ("net_follower_growth", "Net Growth", "👥"),
    ]
    
    for i, (key, label, icon) in enumerate(kpi_configs):
        with cols[i]:
            kpi = kpis.get(key, {})
            value = kpi.get("value")
            available = kpi.get("available", False)
            
            if key == "avg_engagement_rate":
                display_val = format_percentage(value) if available else "N/A"
            elif key == "net_follower_growth" and available:
                sign = "+" if value >= 0 else ""
                display_val = f"{sign}{format_number(value)}"
            else:
                display_val = format_number(value) if available else "N/A"
            
            # Comparison change
            change_html = ""
            if comparison and key in comparison:
                comp_data = comparison[key]
                if comp_data.get("available"):
                    pct = comp_data.get("percentage_change")
                    if pct is not None:
                        color = SUCCESS if pct >= 0 else DANGER
                        arrow = "↑" if pct >= 0 else "↓"
                        change_html = f'<div style="display:flex;align-items:center;gap:4px;margin-top:4px;"><span style="color:{color};font-size:0.8rem;font-weight:600;">{arrow} {abs(pct):.1f}%</span></div>'

            # Additional info for follower growth
            extra_html = ""
            if key == "net_follower_growth" and kpis.get("latest_followers", {}).get("available"):
                total = kpis["latest_followers"]["value"]
                extra_html = f'<div style="font-size:0.75rem;color:{TEXT_MUTED};margin-top:2px;">Total: {format_number(total)}</div>'

            card_html = (
                f'<div style="background:white;border-radius:12px;padding:20px;'
                f'box-shadow:0 2px 8px rgba(0,0,0,0.06);border:1px solid #F0F0F5;height:140px;">'
                f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;">'
                f'<span style="font-size:0.85rem;color:{TEXT_MUTED};font-weight:500;">{label}</span>'
                f'<span>{icon}</span>'
                f'</div>'
                f'<div style="font-size:1.75rem;font-weight:700;color:{TEXT_PRIMARY};line-height:1.2;">'
                f'{display_val}'
                f'</div>'
                f'{change_html}'
                f'{extra_html}'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)


def _render_performance_trends(df, mapped):
    """Render the Performance Trends chart section."""
    st.markdown(f"""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #F0F0F5;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <div>
                <h4 style="margin: 0; font-size: 1.1rem;">Performance Trends</h4>
                <p style="color: {TEXT_MUTED}; font-size: 0.8rem; margin: 0;">
                    Daily reach and engagement trajectory
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # View toggle
    view = st.radio("View", ["Daily", "Weekly", "Cumulative"], horizontal=True, label_visibility="collapsed", key="trend_view")
    
    if view == "Daily":
        trend_df = calculate_daily_metrics(df, mapped)
    elif view == "Weekly":
        trend_df = calculate_weekly_metrics(df, mapped)
    else:
        trend_df = calculate_daily_metrics(df, mapped)
    
    if trend_df is not None and not trend_df.empty:
        from components.charts import render_performance_trend
        render_performance_trend(trend_df, view)
        
        # Peak stats below chart
        peak = get_peak_performance(df, mapped)
        c1, c2, c3 = st.columns(3)
        with c1:
            if peak.get("peak_daily_reach"):
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: {TEXT_MUTED};">PEAK DAY REACH</div>
                    <div style="font-size: 1.2rem; font-weight: 700;">{format_number(peak['peak_daily_reach'])}</div>
                    <div style="font-size: 0.7rem; color: {TEXT_MUTED};">{peak.get('peak_daily_reach_date', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        with c2:
            if peak.get("avg_daily_reach"):
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: {TEXT_MUTED};">AVG DAILY REACH</div>
                    <div style="font-size: 1.2rem; font-weight: 700;">{format_number(peak['avg_daily_reach'])}</div>
                    <div style="font-size: 0.7rem; color: {TEXT_MUTED};">Steady momentum</div>
                </div>
                """, unsafe_allow_html=True)
        with c3:
            if peak.get("engagement_to_reach_ratio"):
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: {TEXT_MUTED};">ENGAGEMENT / REACH</div>
                    <div style="font-size: 1.2rem; font-weight: 700;">{peak['engagement_to_reach_ratio']}%</div>
                    <div style="font-size: 0.7rem; color: {SUCCESS};">Efficiency ratio</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No trend data available. Ensure your dataset has date and metric columns.")


def _render_format_performance(df, mapped, kpis):
    """Render the Format Performance section."""
    total_posts = kpis.get("total_posts", {}).get("value", len(df))
    
    st.markdown(f"""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #F0F0F5;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
                <h4 style="margin: 0; font-size: 1.1rem;">Format Performance</h4>
                <p style="color: {TEXT_MUTED}; font-size: 0.8rem; margin: 0;">Volume and interaction distribution</p>
            </div>
            <span style="font-size: 0.8rem; color: {TEXT_MUTED};">{total_posts} Total Posts</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    format_df = calculate_format_performance(df, mapped)
    
    if format_df is not None and not format_df.empty:
        from utils.constants import POST_TYPE_ICONS
        
        for idx, row in format_df.iterrows():
            post_type = str(idx)
            icon = POST_TYPE_ICONS.get(post_type, "📌")
            count = int(row.get("post_count", 0))
            pct = row.get("pct_contribution", 0)
            er = row.get("eng_rate_by_reach", 0)
            
            # Progress bar width
            max_count = format_df["post_count"].max()
            bar_width = (count / max_count * 100) if max_count > 0 else 0
            
            st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span>{icon}</span>
                        <span style="font-weight: 600; font-size: 0.85rem;">{post_type} ({count})</span>
                    </div>
                    <div style="display: flex; gap: 16px; font-size: 0.8rem;">
                        <span style="color: {TEXT_MUTED};">Eng. Rate: <b>{er:.2f}%</b></span>
                        <span style="color: {TEXT_MUTED};">{pct:.1f}%</span>
                    </div>
                </div>
                <div style="background: #F0F0FF; border-radius: 4px; height: 6px; overflow: hidden;">
                    <div style="background: {PRIMARY}; height: 100%; width: {bar_width}%; border-radius: 4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Ratio cards
        st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        
        save_ratio = calculate_save_reach_ratio(df, mapped)
        comment_ratio = calculate_comment_like_ratio(df, mapped)
        
        with r1:
            if save_ratio is not None:
                st.markdown(f"""
                <div style="background: #F9F9FF; border-radius: 8px; padding: 12px;">
                    <div style="font-size: 0.75rem; color: {TEXT_MUTED};">SAVE / REACH RATIO</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: {PRIMARY};">{save_ratio}%</div>
                </div>
                """, unsafe_allow_html=True)
        
        with r2:
            if comment_ratio is not None:
                st.markdown(f"""
                <div style="background: #F9F9FF; border-radius: 8px; padding: 12px;">
                    <div style="font-size: 0.75rem; color: {TEXT_MUTED};">COMMENT / LIKE RATIO</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: {SECONDARY};">{comment_ratio}%</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No post type data available. Add a 'Post Type' column to your CSV for format analysis.")


def _render_top_posts_preview(df, mapped):
    """Render top 3 posts quick view."""
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div>
            <h4 style="margin: 0; font-size: 1.1rem;">🏆 Top Performing Posts</h4>
            <p style="color: {TEXT_MUTED}; font-size: 0.8rem; margin: 0;">Ranked by engagement score</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    top = get_top_posts(df, mapped, sort_by="engagements", n=3)
    
    if top is not None and not top.empty:
        for i, (_, row) in enumerate(top.iterrows()):
            post_col = mapped.get(STD_POST, "")
            caption = truncate_text(str(row.get(post_col, "Untitled Post")), 60) if post_col else "Untitled Post"
            
            type_col = mapped.get(STD_POST_TYPE, "")
            post_type = str(row.get(type_col, "")) if type_col else ""
            
            date_col = mapped.get(STD_DATE, "")
            post_date = str(row.get(date_col, ""))[:10] if date_col else ""
            
            reach_col = mapped.get(STD_REACH, "")
            reach = format_number(row.get(reach_col)) if reach_col else "N/A"
            
            likes_col = mapped.get(STD_LIKES, "")
            likes = format_number(row.get(likes_col)) if likes_col else "N/A"
            
            comments_col = mapped.get(STD_COMMENTS, "")
            comments = format_number(row.get(comments_col)) if comments_col else "N/A"
            
            shares_col = mapped.get(STD_SHARES, "")
            shares = format_number(row.get(shares_col)) if shares_col else "N/A"
            
            er_col = mapped.get(STD_ENGAGEMENT_RATE, "")
            er = f"{row.get(er_col, 0):.2f}%" if er_col and pd.notna(row.get(er_col)) else "N/A"
            
            type_badge = f'<span style="background: #F0F0FF; color: {PRIMARY}; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 600;">{post_type}</span>' if post_type else ""
            
            st.markdown(f"""
            <div style="background: white; border-radius: 10px; padding: 16px; margin-bottom: 10px;
                        box-shadow: 0 1px 4px rgba(0,0,0,0.05); border: 1px solid #F0F0F5;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 0.9rem; color: {TEXT_PRIMARY}; margin-bottom: 4px;">
                            {caption}
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            {type_badge}
                            <span style="font-size: 0.75rem; color: {TEXT_MUTED};">{post_date}</span>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.1rem; font-weight: 700; color: {PRIMARY};">{er}</span>
                        <span style="font-size: 0.7rem; color: {TEXT_MUTED};"> ER</span>
                    </div>
                </div>
                <div style="display: flex; gap: 16px; font-size: 0.8rem; color: {TEXT_MUTED};">
                    <span>👁️ {reach}</span>
                    <span>❤️ {likes}</span>
                    <span>💬 {comments}</span>
                    <span>🔄 {shares}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("View All →", key="view_all_posts"):
            st.session_state.current_page = "Top Posts Explorer"
            st.rerun()
    else:
        st.info("No post data available.")


def _render_ai_synthesis_preview(kpis, comparison, df, mapped, platform):
    """Render AI synthesis quick view."""
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div>
            <h4 style="margin: 0; font-size: 1.1rem;">🤖 AI Synthesis</h4>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for cached insights
    insights = st.session_state.ai_insights
    
    if insights is None:
        # Generate insights
        from services.analytics_engine import calculate_format_performance, calculate_posting_frequency, get_peak_performance
        format_perf = calculate_format_performance(df, mapped)
        posting_freq = calculate_posting_frequency(df, mapped)
        peak_perf = get_peak_performance(df, mapped)
        
        from services.ai_insights import generate_ai_insights
        insights = generate_ai_insights(kpis, comparison, format_perf, posting_freq, peak_perf, platform)
        st.session_state.ai_insights = insights
    
    source = insights.get("source", "rule_based")
    source_label = "AI-Powered" if source == "ai" else "Rule-Based Analysis"
    source_color = SUCCESS if source == "ai" else "#F59E0B"
    
    primary_takeaway = insights.get("primary_takeaway", "Upload data for insights.")
    
    card_html = (
        f'<div style="background:white;border-radius:12px;padding:20px;'
        f'border:1px solid #E8E8F0;border-left:4px solid {PRIMARY};box-shadow:0 2px 6px rgba(0,0,0,0.02);">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">'
        f'<div style="font-weight:700;font-size:0.95rem;color:{TEXT_PRIMARY};display:flex;align-items:center;gap:6px;">'
        f'<span style="color:{PRIMARY};">✨</span> AI Synthesis'
        f'</div>'
        f'<span style="background:{source_color};color:white;padding:2px 10px;border-radius:12px;font-size:0.7rem;font-weight:600;">{source_label}</span>'
        f'</div>'
        f'<div style="background:#F0F0FF;border:1px solid #E0E2FF;border-radius:8px;padding:12px 14px;margin-bottom:12px;">'
        f'<div style="font-size:0.68rem;font-weight:800;color:{PRIMARY};letter-spacing:0.5px;margin-bottom:4px;">PRIMARY TAKEAWAY</div>'
        f'<p style="font-size:0.88rem;line-height:1.55;margin:0;color:{TEXT_PRIMARY};font-weight:500;">{primary_takeaway}</p>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Show top recommendations
    recs = insights.get("recommendations", [])[:2]
    if recs:
        st.markdown(f"<div style='margin-top: 12px; font-size: 0.85rem; font-weight: 600; color: {TEXT_PRIMARY};'>Recommendations:</div>", unsafe_allow_html=True)
        for rec in recs:
            title = rec.get("title", "") if isinstance(rec, dict) else str(rec)
            st.markdown(f"""
            <div style="display: flex; align-items: start; gap: 8px; padding: 8px 0; font-size: 0.85rem;">
                <span style="color: {SUCCESS};">✦</span>
                <span style="color: {TEXT_PRIMARY};">{title}</span>
            </div>
            """, unsafe_allow_html=True)
    
    if st.button("View Full AI Insights →", key="view_ai"):
        st.session_state.current_page = "AI Insights"
        st.rerun()
