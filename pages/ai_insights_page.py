"""
SocialPulse AI - Page 5: AI Insights
AI-powered performance analysis with executive summary, recommendations, and strategies.
"""
import streamlit as st
from utils.session_manager import (
    init_session_state, get_dataframe, is_data_loaded, get_platform
)
from utils.constants import (
    PRIMARY, SUCCESS, SECONDARY, DANGER, TEXT_PRIMARY, TEXT_MUTED
)
from utils.formatters import format_number, format_percentage, format_date_range
from services.analytics_engine import (
    calculate_kpis, calculate_format_performance,
    calculate_posting_frequency, get_peak_performance
)
from services.comparison_engine import compare_periods
from services.ai_insights import generate_ai_insights, is_ai_configured


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
    dataset_info = st.session_state.get("dataset_name", "dataset")

    # Date range display
    dr = st.session_state.get("date_range")
    dr_str = format_date_range(dr[0], dr[1]) if dr else ""

    # ── Page Header ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-bottom:4px;">
        <span style="background:{PRIMARY};color:white;padding:3px 10px;border-radius:4px;
                     font-size:0.72rem;font-weight:600;">SYNTHESIZED INSIGHTS</span>
        <span style="color:{TEXT_MUTED};font-size:0.8rem;margin-left:8px;">• Analysis Period: {dr_str}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("# AI Synthesized Performance Insights")
    st.markdown(f"<p style='color:{TEXT_MUTED};font-size:0.9rem;'>Generated via SocialPulse AI Intelligence Model – Contextual and Verified Predictions.</p>", unsafe_allow_html=True)

    # ── Generate or Load Insights ───────────────────────────────────────
    insights = st.session_state.ai_insights

    if insights is None or st.button("🔄 Regenerate Insights", key="regen_ai"):
        with st.spinner("Analyzing performance data..."):
            kpis = calculate_kpis(df, mapped)
            comparison = compare_periods(df, mapped)
            format_perf = calculate_format_performance(df, mapped)
            posting_freq = calculate_posting_frequency(df, mapped)
            peak_perf = get_peak_performance(df, mapped)

            insights = generate_ai_insights(
                kpis, comparison, format_perf, posting_freq, peak_perf, platform
            )
            st.session_state.ai_insights = insights

    source = insights.get("source", "rule_based")
    source_label = "AI-Powered" if source == "ai" else "Rule-Based Analysis"
    source_color = SUCCESS if source == "ai" else "#F59E0B"
    model_info = insights.get("model", "")

    # Source badge
    ai_config_msg = ""
    if source == "rule_based":
        ai_config_msg = f"""
        <div style="background:#FFFBEB;border-radius:8px;padding:12px 16px;margin-bottom:16px;
                    border:1px solid #FDE68A;font-size:0.85rem;">
            ⚠️ <b>Rule-based insights active.</b> These are generated using predefined rules, NOT an AI model.
            To enable AI-powered analysis, add your Groq or OpenAI API key to the <code>.env</code> file.
        </div>
        """

    st.markdown(f"""
    <div style="display:flex;gap:8px;align-items:center;margin-bottom:16px;">
        <span style="background:{source_color};color:white;padding:4px 14px;border-radius:20px;
                     font-size:0.78rem;font-weight:600;">{source_label}</span>
        {'<span style="font-size:0.78rem;color:'+TEXT_MUTED+';">Model: '+model_info+'</span>' if model_info else ''}
    </div>
    {ai_config_msg}
    """, unsafe_allow_html=True)

    # ── Executive Summary ───────────────────────────────────────────────
    exec_summary = insights.get("executive_summary", "")
    st.markdown(f"""
    <div style="background:#1A1B2E;border-radius:12px;padding:28px;color:white;margin-bottom:24px;">
        <div style="font-size:0.75rem;color:rgba(255,255,255,0.5);margin-bottom:8px;letter-spacing:1px;">
            EXECUTIVE SUMMARY
        </div>
        <p style="font-size:1rem;line-height:1.7;margin:0;color:rgba(255,255,255,0.92);">
            {exec_summary}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Primary Takeaway + Key Metrics ──────────────────────────────────
    col_l, col_r = st.columns([3, 2])

    with col_l:
        primary = insights.get("primary_takeaway", "")
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:20px;border:1px solid #E8E8F0;margin-bottom:16px;">
            <div style="font-size:0.78rem;color:{TEXT_MUTED};margin-bottom:8px;font-weight:600;">
                🎯 PRIMARY TAKEAWAY
            </div>
            <p style="font-size:0.95rem;line-height:1.6;color:{TEXT_PRIMARY};margin:0;">{primary}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_r:
        # Algorithmic trends summary
        content_strategy = insights.get("content_strategy", "")
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:20px;border:1px solid #E8E8F0;margin-bottom:16px;">
            <div style="font-size:0.78rem;color:{TEXT_MUTED};margin-bottom:8px;font-weight:600;">
                📊 CONTENT STRATEGY
            </div>
            <p style="font-size:0.88rem;line-height:1.6;color:{TEXT_PRIMARY};margin:0;">{content_strategy}</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Strengths & Weaknesses ──────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    s_col, w_col = st.columns(2)

    with s_col:
        st.markdown(f"<h4 style='font-size:1rem;color:{SUCCESS};'>✅ Strengths</h4>", unsafe_allow_html=True)
        strengths = insights.get("strengths", [])
        if strengths:
            for s in strengths:
                title = s.get("title", "") if isinstance(s, dict) else str(s)
                desc = s.get("description", "") if isinstance(s, dict) else ""
                st.markdown(f"""
                <div style="background:white;border-left:3px solid {SUCCESS};border-radius:0 8px 8px 0;
                            padding:12px 16px;margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
                    <div style="font-weight:600;font-size:0.88rem;color:{TEXT_PRIMARY};margin-bottom:4px;">{title}</div>
                    <div style="font-size:0.82rem;color:{TEXT_MUTED};line-height:1.5;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No strengths identified.")

    with w_col:
        st.markdown(f"<h4 style='font-size:1rem;color:{DANGER};'>⚠️ Weaknesses</h4>", unsafe_allow_html=True)
        weaknesses = insights.get("weaknesses", [])
        if weaknesses:
            for w in weaknesses:
                title = w.get("title", "") if isinstance(w, dict) else str(w)
                desc = w.get("description", "") if isinstance(w, dict) else ""
                st.markdown(f"""
                <div style="background:white;border-left:3px solid {DANGER};border-radius:0 8px 8px 0;
                            padding:12px 16px;margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
                    <div style="font-weight:600;font-size:0.88rem;color:{TEXT_PRIMARY};margin-bottom:4px;">{title}</div>
                    <div style="font-size:0.82rem;color:{TEXT_MUTED};line-height:1.5;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No weaknesses identified.")

    # ── Actionable Recommendations ──────────────────────────────────────
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size:1.1rem;'>🎯 Prioritized Algorithmic Action Plan</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{TEXT_MUTED};font-size:0.82rem;'>Data-backed tactical shifts to amplify reach and sustained audience growth.</p>", unsafe_allow_html=True)

    recs = insights.get("recommendations", [])
    if recs:
        rec_cols = st.columns(min(3, len(recs)))
        priority_colors = {"high": DANGER, "medium": "#F59E0B", "low": SUCCESS}

        for i, rec in enumerate(recs[:6]):
            with rec_cols[i % len(rec_cols)]:
                title = rec.get("title", "") if isinstance(rec, dict) else str(rec)
                desc = rec.get("description", "") if isinstance(rec, dict) else ""
                priority = rec.get("priority", "medium") if isinstance(rec, dict) else "medium"
                p_color = priority_colors.get(priority, "#F59E0B")

                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:18px;margin-bottom:12px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.06);border:1px solid #F0F0F5;
                            border-top:3px solid {p_color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-weight:700;font-size:0.88rem;color:{TEXT_PRIMARY};">{title}</span>
                        <span style="background:{p_color};color:white;padding:2px 8px;border-radius:12px;
                                     font-size:0.65rem;font-weight:600;text-transform:uppercase;">{priority}</span>
                    </div>
                    <p style="font-size:0.82rem;color:{TEXT_MUTED};line-height:1.5;margin:0;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No recommendations generated. Upload data with more metrics for deeper analysis.")

    # ── Strategy Insight Cards ──────────────────────────────────────────
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size:1.1rem;'>📋 Strategy Insights</h3>", unsafe_allow_html=True)

    strategies = [
        ("📝 Content Strategy", insights.get("content_strategy", "N/A")),
        ("💬 Engagement Strategy", insights.get("engagement_strategy", "N/A")),
        ("👁️ Reach Optimization", insights.get("reach_optimization", "N/A")),
        ("📅 Posting Consistency", insights.get("posting_consistency", "N/A")),
    ]

    strat_cols = st.columns(2)
    for i, (title, content) in enumerate(strategies):
        with strat_cols[i % 2]:
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:18px;margin-bottom:12px;
                        box-shadow:0 2px 6px rgba(0,0,0,0.04);border:1px solid #F0F0F5;">
                <div style="font-weight:600;font-size:0.9rem;color:{PRIMARY};margin-bottom:8px;">{title}</div>
                <p style="font-size:0.85rem;color:{TEXT_PRIMARY};line-height:1.6;margin:0;">{content}</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Data Limitations ────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="padding:14px 18px;background:#F9F9FF;border-radius:8px;border-left:3px solid {PRIMARY};
                font-size:0.82rem;color:{TEXT_PRIMARY};">
        <b>📌 Data Limitations & Disclosure:</b> Insights are generated from the uploaded dataset only.
        Reach and impressions are post-level aggregates, not unique audience counts.
        {'These insights use rule-based analysis. For AI-powered analysis, configure an API key.' if source == 'rule_based' else f'Insights generated by {model_info} AI model.'}
        All recommendations are suggestions based on observed patterns and should be validated with
        broader business context.
    </div>
    """, unsafe_allow_html=True)
