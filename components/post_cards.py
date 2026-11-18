"""
SocialPulse AI - Post Card Components
"""
import streamlit as st
import pandas as pd
from utils.formatters import format_number, format_percentage, truncate_text
from utils.constants import (
    STD_POST, STD_POST_TYPE, STD_DATE, STD_REACH, STD_IMPRESSIONS,
    STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES, STD_ENGAGEMENT_RATE,
    PRIMARY, SUCCESS, SECONDARY, TEXT_PRIMARY, TEXT_MUTED, POST_TYPE_ICONS
)


def render_top_post_card(post_data: dict, rank: int, mapped_columns: dict):
    """Render a single top post card."""
    caption = truncate_text(str(post_data.get("caption", "Untitled Post")), 70)
    post_type = str(post_data.get("post_type", ""))
    date_str = str(post_data.get("date", ""))[:10]
    reach = format_number(post_data.get("reach"))
    impressions = format_number(post_data.get("impressions"))
    likes = format_number(post_data.get("likes"))
    comments = format_number(post_data.get("comments"))
    shares = format_number(post_data.get("shares"))
    saves = format_number(post_data.get("saves"))
    er = post_data.get("engagement_rate")
    er_str = f"{er:.2f}%" if er and not pd.isna(er) else "N/A"
    viral_score = post_data.get("viral_score")
    icon = POST_TYPE_ICONS.get(post_type, "📌")

    rank_colors = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}
    rank_bg = rank_colors.get(rank, "#E8E8F0")

    score_html = ""
    if viral_score is not None:
        score_html = f"""
        <div style="background:#F0F0FF;border-radius:8px;padding:6px 10px;text-align:center;margin-top:8px;">
            <span style="font-size:1.1rem;font-weight:700;color:{PRIMARY};">{viral_score}/100</span>
            <span style="font-size:0.7rem;color:{TEXT_MUTED};"> Score</span>
        </div>"""

    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:20px;
                box-shadow:0 2px 10px rgba(0,0,0,0.08);border:1px solid #F0F0F5;
                transition:transform 0.2s;">
        <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:10px;">
            <span style="background:{rank_bg};color:white;width:28px;height:28px;border-radius:50%;
                         display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.85rem;">
                {rank}
            </span>
            <span style="background:#F0F0FF;color:{PRIMARY};padding:3px 10px;border-radius:12px;
                         font-size:0.72rem;font-weight:600;">{icon} {post_type}</span>
        </div>
        <div style="font-weight:600;font-size:0.92rem;color:{TEXT_PRIMARY};margin-bottom:6px;
                    line-height:1.4;min-height:40px;">{caption}</div>
        <div style="font-size:0.75rem;color:{TEXT_MUTED};margin-bottom:12px;">Published {date_str}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.8rem;">
            <div>👁️ <b>{reach}</b> <span style="color:{TEXT_MUTED};">reach</span></div>
            <div>📈 <b>{impressions}</b> <span style="color:{TEXT_MUTED};">imp</span></div>
            <div>❤️ <b>{likes}</b> <span style="color:{TEXT_MUTED};">likes</span></div>
            <div>💬 <b>{comments}</b> <span style="color:{TEXT_MUTED};">comments</span></div>
            <div>🔄 <b>{shares}</b> <span style="color:{TEXT_MUTED};">shares</span></div>
            <div>🔖 <b>{saves}</b> <span style="color:{TEXT_MUTED};">saves</span></div>
        </div>
        <div style="margin-top:12px;padding-top:10px;border-top:1px solid #F0F0F5;
                    display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:0.75rem;color:{TEXT_MUTED};">Engagement Rate</span>
            <span style="font-size:1.2rem;font-weight:700;color:{PRIMARY};">{er_str}</span>
        </div>
        {score_html}
    </div>
    """, unsafe_allow_html=True)


def render_top_posts_row(posts_df: pd.DataFrame, mapped_columns: dict, n: int = 3):
    """Render top N posts in columns."""
    if posts_df is None or posts_df.empty:
        st.info("No posts to display.")
        return

    cols = st.columns(min(n, len(posts_df)))
    for i, (_, row) in enumerate(posts_df.head(n).iterrows()):
        with cols[i]:
            post_data = _extract_post_data(row, mapped_columns)
            render_top_post_card(post_data, rank=i + 1, mapped_columns=mapped_columns)


def _extract_post_data(row: pd.Series, mapped_columns: dict) -> dict:
    """Extract post data from a dataframe row using mapped columns."""
    def _get(std):
        col = mapped_columns.get(std)
        if col and col in row.index:
            return row[col]
        return None

    er = _get(STD_ENGAGEMENT_RATE)
    if er is None:
        # Calculate if possible
        likes = _get(STD_LIKES) or 0
        comments = _get(STD_COMMENTS) or 0
        shares = _get(STD_SHARES) or 0
        saves = _get(STD_SAVES) or 0
        reach = _get(STD_REACH) or 0
        if reach > 0:
            er = (likes + comments + shares + saves) / reach * 100

    return {
        "caption": _get(STD_POST) or "Untitled Post",
        "post_type": _get(STD_POST_TYPE) or "Post",
        "date": _get(STD_DATE),
        "reach": _get(STD_REACH),
        "impressions": _get(STD_IMPRESSIONS),
        "likes": _get(STD_LIKES),
        "comments": _get(STD_COMMENTS),
        "shares": _get(STD_SHARES),
        "saves": _get(STD_SAVES),
        "engagement_rate": er,
        "viral_score": row.get("_viral_score") if "_viral_score" in row.index else None,
    }
