"""
SocialPulse AI - Page 4: Top Posts Explorer
Dedicated content discovery page with ranking, search, and filtering.
"""
import streamlit as st
import pandas as pd
import numpy as np
from utils.session_manager import (
    init_session_state, get_dataframe, is_data_loaded, get_platform
)
from utils.constants import (
    STD_DATE, STD_POST, STD_REACH, STD_IMPRESSIONS, STD_LIKES,
    STD_COMMENTS, STD_SHARES, STD_SAVES, STD_POST_TYPE, STD_ENGAGEMENT_RATE,
    PRIMARY, SUCCESS, SECONDARY, DANGER, TEXT_PRIMARY, TEXT_MUTED, POST_TYPE_ICONS
)
from utils.formatters import format_number, format_percentage, truncate_text
from services.analytics_engine import get_top_posts, calculate_viral_score
from components.post_cards import render_top_posts_row, _extract_post_data, render_top_post_card
from components.filters import render_post_type_filter, render_sort_filter, render_search_filter


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

    st.markdown("# Top-Performing Content Explorer")
    st.markdown(f"<p style='color:{TEXT_MUTED};font-size:0.88rem;'>Auditing multi-metric engagement dynamics, algorithmic reach multipliers, and post resonance.</p>", unsafe_allow_html=True)

    # ── Ranking Tabs ────────────────────────────────────────────────────
    tab_labels = ["🏆 Ranking by Engagement", "📊 Sort by Total Reach",
                  "⚡ Sort by Eng Rate", "❤️ Sort by Likes"]
    tabs = st.tabs(tab_labels)

    sort_map = {0: "engagements", 1: "reach", 2: "engagement_rate", 3: "likes"}

    # ── Filters Row ─────────────────────────────────────────────────────
    fc1, fc2, fc3, fc4 = st.columns([2, 1, 1, 1])
    with fc1:
        search_q = render_search_filter(key="top_search")
    with fc2:
        post_type_filter = render_post_type_filter(df, mapped, key="top_type")
    with fc3:
        limit_options = {"Top 10": 10, "Top 25": 25, "Top 50": 50, "All": len(df)}
        limit_label = st.selectbox("Limit", list(limit_options.keys()), key="top_limit")
        limit = limit_options[limit_label]
    with fc4:
        st.markdown(f"<div style='padding-top:28px;font-size:0.82rem;color:{TEXT_MUTED};'>📊 {len(df)} total posts</div>", unsafe_allow_html=True)

    # ── Calculate Viral Scores ──────────────────────────────────────────
    _add_viral_scores(df, mapped)

    for tab_idx, tab in enumerate(tabs):
        with tab:
            sort_by = sort_map.get(tab_idx, "engagements")
            top_df = get_top_posts(df, mapped, sort_by=sort_by, n=limit,
                                   post_type_filter=post_type_filter,
                                   search_query=search_q if search_q else None)

            if top_df.empty:
                st.info("No posts match the current filters.")
                continue

            # ── Top 3 Viral Outliers ────────────────────────────────────
            st.markdown(f"""
            <div style="margin:16px 0 8px 0;">
                <h3 style="font-size:1.05rem;margin:0;">🏅 Top 3 Viral Outliers</h3>
                <p style="color:{TEXT_MUTED};font-size:0.8rem;margin:0;">
                    Posts generating {'>'}1% of total discovery during the entire dataset timespan
                </p>
            </div>
            """, unsafe_allow_html=True)

            render_top_posts_row(top_df, mapped, n=3)

            # ── Full Posts Table ────────────────────────────────────────
            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <h4 style="font-size:1rem;">📋 Rank-Tier Performance Ledger</h4>
            <p style="color:{TEXT_MUTED};font-size:0.8rem;">
                Sortable ranked table with cross-dimension verification summary
            </p>
            """, unsafe_allow_html=True)

            _render_posts_table(top_df, mapped, sort_by)

    # ── Viral Score Explanation ─────────────────────────────────────────
    with st.expander("ℹ️ How is the Performance Score calculated?"):
        st.markdown(f"""
        The **Performance Score** (0–100) is a **relative ranking** of each post against
        others in this dataset. It is **not** an absolute virality measure.

        **Formula:** Weighted average of normalized metrics:
        - **Reach** (30% weight)
        - **Engagement Rate** (30% weight)
        - **Total Engagements** (25% weight)
        - **Shares** (15% weight)

        Each metric is normalized: `(value − min) / (max − min) × 100`

        A score of 95 means that post outperforms 95% of other posts in the dataset
        on the weighted combination of these metrics. When data is insufficient for
        some metrics, only available metrics are used with proportional re-weighting.
        """)


def _add_viral_scores(df, mapped):
    """Add viral scores to dataframe if not present."""
    if "_viral_score" in df.columns:
        return

    # Calculate engagements
    eng_cols = []
    for std in [STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES]:
        col = mapped.get(std)
        if col and col in df.columns:
            eng_cols.append(col)
    if eng_cols:
        df["_total_engagements"] = df[eng_cols].sum(axis=1, min_count=1)
    else:
        df["_total_engagements"] = 0

    # Gather stats for normalization
    df_stats = {}
    for std in [STD_REACH, STD_ENGAGEMENT_RATE, STD_SHARES]:
        col = mapped.get(std)
        if col and col in df.columns:
            df_stats[col] = {"min": df[col].min(), "max": df[col].max()}
    if "_total_engagements" in df.columns:
        df_stats["_total_engagements"] = {
            "min": df["_total_engagements"].min(),
            "max": df["_total_engagements"].max()
        }

    df["_viral_score"] = df.apply(
        lambda row: calculate_viral_score(row, mapped, df_stats), axis=1
    )


def _render_posts_table(top_df, mapped, sort_by):
    """Render sortable posts table."""
    rows = []
    for rank, (_, row) in enumerate(top_df.iterrows(), 1):
        data = _extract_post_data(row, mapped)
        entry = {
            "#": rank,
            "Caption": truncate_text(str(data.get("caption", "")), 55),
            "Type": data.get("post_type", ""),
            "Date": str(data.get("date", ""))[:10],
        }

        reach = data.get("reach")
        if reach is not None and not pd.isna(reach):
            entry["Reach"] = f"{reach:,.0f}"

        imp = data.get("impressions")
        if imp is not None and not pd.isna(imp):
            entry["Impressions"] = f"{imp:,.0f}"

        likes = data.get("likes")
        if likes is not None and not pd.isna(likes):
            entry["Likes"] = f"{likes:,.0f}"

        comments = data.get("comments")
        if comments is not None and not pd.isna(comments):
            entry["Comments"] = f"{comments:,.0f}"

        shares = data.get("shares")
        if shares is not None and not pd.isna(shares):
            entry["Shares"] = f"{shares:,.0f}"

        er = data.get("engagement_rate")
        if er is not None and not pd.isna(er):
            entry["ER%"] = f"{er:.2f}%"

        score = row.get("_viral_score") if "_viral_score" in row.index else None
        if score is not None:
            entry["Score"] = f"{score:.0f}/100"

        rows.append(entry)

    if rows:
        table_df = pd.DataFrame(rows)
        st.dataframe(table_df, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("No data to display.")
