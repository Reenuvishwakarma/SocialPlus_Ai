"""
SocialPulse AI - Filter Components
Reusable filter controls for analytics pages.
"""
import streamlit as st
import pandas as pd
from utils.session_manager import init_session_state, get_dataframe
from utils.constants import STD_DATE, STD_POST_TYPE, TEXT_MUTED
from utils.helpers import detect_post_types


def render_date_filter(df: pd.DataFrame, mapped_columns: dict, key_prefix: str = "flt"):
    """Render date range filter. Returns (start_date, end_date) or (None, None)."""
    date_col = mapped_columns.get(STD_DATE)
    if not date_col or date_col not in df.columns:
        return None, None

    dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
    if dates.empty:
        return None, None

    min_d = dates.min().date()
    max_d = dates.max().date()

    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input("Start Date", value=min_d, min_value=min_d, max_value=max_d, key=f"{key_prefix}_start")
    with c2:
        end = st.date_input("End Date", value=max_d, min_value=min_d, max_value=max_d, key=f"{key_prefix}_end")

    return start, end


def render_post_type_filter(df: pd.DataFrame, mapped_columns: dict, key: str = "flt_type"):
    """Render post type selector. Returns selected type or 'All'."""
    type_col = mapped_columns.get(STD_POST_TYPE)
    if not type_col or type_col not in df.columns:
        return "All"

    types = ["All"] + sorted(detect_post_types(df, type_col))
    return st.selectbox("Post Type", types, key=key)


def render_sort_filter(key: str = "flt_sort"):
    """Render sort-by dropdown. Returns sort key."""
    options = {
        "Highest Reach": "reach",
        "Highest Engagement": "engagements",
        "Highest Engagement Rate": "engagement_rate",
        "Most Likes": "likes",
        "Most Shares": "shares",
        "Most Comments": "comments",
    }
    selected = st.selectbox("Sort By", list(options.keys()), key=key)
    return options[selected]


def render_search_filter(key: str = "flt_search"):
    """Render search input. Returns query string."""
    return st.text_input("🔍 Search posts...", placeholder="Search by caption, keyword...", key=key)


def render_analytics_filters(df: pd.DataFrame, mapped_columns: dict):
    """Render combined filter bar for Deep Analytics page. Returns filter dict."""
    with st.expander("🔧 Filters", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            start, end = render_date_filter(df, mapped_columns, key_prefix="analytics")
        with c2:
            post_type = render_post_type_filter(df, mapped_columns, key="analytics_type")
        with c3:
            sort_by = render_sort_filter(key="analytics_sort")
        with c4:
            st.markdown(f"<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
            apply = st.button("Apply Filters", type="primary", key="analytics_apply")

    return {
        "date_start": start if 'start' in dir() else None,
        "date_end": end if 'end' in dir() else None,
        "post_type": post_type if 'post_type' in dir() else "All",
        "sort_by": sort_by if 'sort_by' in dir() else "reach",
    }


def apply_filters(df: pd.DataFrame, mapped_columns: dict, filters: dict) -> pd.DataFrame:
    """Apply filter dict to dataframe and return filtered copy."""
    if df is None or df.empty:
        return df

    filtered = df.copy()

    # Date filter
    date_col = mapped_columns.get(STD_DATE)
    if date_col and date_col in filtered.columns:
        filtered[date_col] = pd.to_datetime(filtered[date_col], errors="coerce")
        if filters.get("date_start"):
            filtered = filtered[filtered[date_col] >= pd.to_datetime(filters["date_start"])]
        if filters.get("date_end"):
            filtered = filtered[filtered[date_col] <= pd.to_datetime(filters["date_end"])]

    # Post type filter
    type_col = mapped_columns.get(STD_POST_TYPE)
    if filters.get("post_type") and filters["post_type"] != "All" and type_col and type_col in filtered.columns:
        filtered = filtered[filtered[type_col] == filters["post_type"]]

    return filtered
