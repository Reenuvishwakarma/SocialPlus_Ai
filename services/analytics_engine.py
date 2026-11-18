"""
SocialPulse AI - Analytics Engine
Core metric calculations and analysis functions.

All calculations are documented with their formulas and assumptions.
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Any
from utils.constants import (
    STD_DATE, STD_REACH, STD_IMPRESSIONS, STD_LIKES,
    STD_COMMENTS, STD_SHARES, STD_SAVES, STD_FOLLOWERS,
    STD_POST_TYPE, STD_ENGAGEMENT_RATE, STD_POST
)
from utils.helpers import safe_divide


def calculate_kpis(df: pd.DataFrame, mapped_columns: Dict[str, str]) -> dict:
    """
    Calculate key performance indicators from the dataset.
    
    Metrics calculated:
    - Total Reach: Sum of post-level reach values (aggregate, not unique audience)
    - Total Impressions: Sum of post-level impression values
    - Total Engagements: Sum of Likes + Comments + Shares + Saves
    - Avg Engagement Rate: Mean of per-post engagement rates
      Formula: Mean of ((Likes+Comments+Shares+Saves)/Reach × 100) per post
    - Net Follower Growth: Latest follower count minus earliest follower count
    
    Returns dict with metric values and availability flags.
    """
    kpis = {
        "total_reach": {"value": None, "available": False},
        "total_impressions": {"value": None, "available": False},
        "total_engagements": {"value": None, "available": False},
        "avg_engagement_rate": {"value": None, "available": False},
        "net_follower_growth": {"value": None, "available": False},
        "total_likes": {"value": None, "available": False},
        "total_comments": {"value": None, "available": False},
        "total_shares": {"value": None, "available": False},
        "total_saves": {"value": None, "available": False},
        "total_posts": {"value": len(df), "available": True},
        "latest_followers": {"value": None, "available": False},
    }

    if df is None or df.empty:
        return kpis

    # ── Total Reach ─────────────────────────────────────────────────────
    reach_col = mapped_columns.get(STD_REACH)
    if reach_col and reach_col in df.columns:
        total_reach = df[reach_col].sum()
        if not pd.isna(total_reach):
            kpis["total_reach"] = {"value": float(total_reach), "available": True}

    # ── Total Impressions ───────────────────────────────────────────────
    imp_col = mapped_columns.get(STD_IMPRESSIONS)
    if imp_col and imp_col in df.columns:
        total_imp = df[imp_col].sum()
        if not pd.isna(total_imp):
            kpis["total_impressions"] = {"value": float(total_imp), "available": True}

    # ── Engagement components ───────────────────────────────────────────
    eng_components = {}
    for std, key in [(STD_LIKES, "total_likes"), (STD_COMMENTS, "total_comments"),
                     (STD_SHARES, "total_shares"), (STD_SAVES, "total_saves")]:
        col = mapped_columns.get(std)
        if col and col in df.columns:
            total = df[col].sum()
            if not pd.isna(total):
                kpis[key] = {"value": float(total), "available": True}
                eng_components[std] = col

    # ── Total Engagements ───────────────────────────────────────────────
    # Sum of all available engagement components
    if eng_components:
        eng_cols = list(eng_components.values())
        total_eng = df[eng_cols].sum(axis=1, min_count=1).sum()
        if not pd.isna(total_eng):
            kpis["total_engagements"] = {"value": float(total_eng), "available": True}

            # Note which components are included
            included = [std for std in eng_components.keys()]
            excluded = [s for s in [STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES]
                       if s not in eng_components]
            kpis["total_engagements"]["components_included"] = included
            if excluded:
                kpis["total_engagements"]["components_excluded"] = excluded

    # ── Average Engagement Rate ─────────────────────────────────────────
    # Calculated as mean of per-post engagement rates
    er_col = mapped_columns.get(STD_ENGAGEMENT_RATE)
    if er_col and er_col in df.columns:
        valid_rates = df[er_col].dropna()
        if not valid_rates.empty:
            kpis["avg_engagement_rate"] = {
                "value": float(valid_rates.mean()),
                "available": True
            }
    elif kpis["total_engagements"]["available"] and kpis["total_reach"]["available"]:
        # Calculate from totals as fallback
        total_eng = kpis["total_engagements"]["value"]
        total_reach = kpis["total_reach"]["value"]
        if total_reach > 0:
            kpis["avg_engagement_rate"] = {
                "value": float(safe_divide(total_eng, total_reach) * 100),
                "available": True,
                "note": "Calculated from aggregate totals, not per-post average"
            }

    # ── Net Follower Growth ─────────────────────────────────────────────
    fol_col = mapped_columns.get(STD_FOLLOWERS)
    date_col = mapped_columns.get(STD_DATE)
    if fol_col and fol_col in df.columns and date_col and date_col in df.columns:
        fol_df = df[[date_col, fol_col]].dropna()
        if not fol_df.empty:
            fol_df = fol_df.sort_values(date_col)
            earliest = fol_df[fol_col].iloc[0]
            latest = fol_df[fol_col].iloc[-1]
            kpis["net_follower_growth"] = {
                "value": float(latest - earliest),
                "available": True
            }
            kpis["latest_followers"] = {
                "value": float(latest),
                "available": True
            }

    return kpis


def calculate_daily_metrics(df: pd.DataFrame, mapped_columns: Dict[str, str]) -> pd.DataFrame:
    """
    Aggregate metrics by day for trend charts.
    Returns a dataframe with date as index and daily sums.
    """
    date_col = mapped_columns.get(STD_DATE)
    if not date_col or date_col not in df.columns:
        return pd.DataFrame()

    metric_cols = {}
    for std, label in [(STD_REACH, "Reach"), (STD_IMPRESSIONS, "Impressions")]:
        col = mapped_columns.get(std)
        if col and col in df.columns:
            metric_cols[col] = label

    # Calculate engagements
    eng_cols = []
    for std in [STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES]:
        col = mapped_columns.get(std)
        if col and col in df.columns:
            eng_cols.append(col)

    if not metric_cols and not eng_cols:
        return pd.DataFrame()

    daily = df.copy()
    daily[date_col] = pd.to_datetime(daily[date_col])

    agg_dict = {col: "sum" for col in metric_cols.keys()}
    for col in eng_cols:
        agg_dict[col] = "sum"

    result = daily.groupby(daily[date_col].dt.date).agg(agg_dict).reset_index()
    result.columns = [date_col] + [metric_cols.get(c, c) for c in list(agg_dict.keys())]

    # Add engagements column
    if eng_cols:
        eng_renamed = [metric_cols.get(c, c) for c in eng_cols]
        result["Engagements"] = result[eng_renamed].sum(axis=1)
        # Drop individual engagement columns from the result
        for c in eng_renamed:
            if c not in ["Reach", "Impressions"]:
                result = result.drop(columns=[c], errors="ignore")

    result = result.rename(columns={date_col: "Date"})
    return result


def calculate_weekly_metrics(df: pd.DataFrame, mapped_columns: Dict[str, str]) -> pd.DataFrame:
    """Aggregate metrics by week."""
    date_col = mapped_columns.get(STD_DATE)
    if not date_col or date_col not in df.columns:
        return pd.DataFrame()

    metric_cols = {}
    for std, label in [(STD_REACH, "Reach"), (STD_IMPRESSIONS, "Impressions")]:
        col = mapped_columns.get(std)
        if col and col in df.columns:
            metric_cols[col] = label

    eng_cols = []
    for std in [STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES]:
        col = mapped_columns.get(std)
        if col and col in df.columns:
            eng_cols.append(col)

    weekly = df.copy()
    weekly[date_col] = pd.to_datetime(weekly[date_col])
    weekly = weekly.set_index(date_col)

    agg_cols = list(metric_cols.keys()) + eng_cols
    agg_cols = [c for c in agg_cols if c in weekly.columns]

    if not agg_cols:
        return pd.DataFrame()

    result = weekly[agg_cols].resample("W").sum().reset_index()
    rename_map = {date_col: "Date"}
    rename_map.update(metric_cols)
    result = result.rename(columns=rename_map)

    # Add engagements
    eng_renamed = [metric_cols.get(c, c) for c in eng_cols if c in result.columns or metric_cols.get(c, c) in result.columns]
    remaining_eng = [c for c in result.columns if c not in ["Date", "Reach", "Impressions"]]
    if remaining_eng:
        result["Engagements"] = result[remaining_eng].sum(axis=1)
        result = result.drop(columns=remaining_eng, errors="ignore")

    return result


def calculate_format_performance(df: pd.DataFrame, mapped_columns: Dict[str, str]) -> pd.DataFrame:
    """
    Calculate performance metrics grouped by content format/type.
    Returns a dataframe with post type as index and aggregated metrics.
    """
    type_col = mapped_columns.get(STD_POST_TYPE)
    if not type_col or type_col not in df.columns:
        return pd.DataFrame()

    agg_dict = {}
    reach_col = mapped_columns.get(STD_REACH)
    imp_col = mapped_columns.get(STD_IMPRESSIONS)

    if reach_col and reach_col in df.columns:
        agg_dict[reach_col] = ["sum", "mean"]
    if imp_col and imp_col in df.columns:
        agg_dict[imp_col] = ["sum", "mean"]

    eng_cols = []
    for std in [STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES]:
        col = mapped_columns.get(std)
        if col and col in df.columns:
            eng_cols.append(col)
            agg_dict[col] = "sum"

    er_col = mapped_columns.get(STD_ENGAGEMENT_RATE)
    if er_col and er_col in df.columns:
        agg_dict[er_col] = "mean"

    if not agg_dict:
        return pd.DataFrame()

    grouped = df.groupby(type_col).agg(agg_dict)
    grouped.columns = ["_".join(col).strip("_") for col in grouped.columns]

    # Add post count
    post_counts = df.groupby(type_col).size().rename("post_count")
    grouped = grouped.join(post_counts)

    # Calculate percentage contribution
    total_posts = len(df)
    grouped["pct_contribution"] = (grouped["post_count"] / total_posts * 100).round(1)

    # Calculate total engagements per type
    if eng_cols:
        eng_sum_cols = [f"{c}_sum" for c in eng_cols if f"{c}_sum" in grouped.columns]
        if eng_sum_cols:
            grouped["total_engagements"] = grouped[eng_sum_cols].sum(axis=1)

    # Calculate engagement rate by reach per type
    reach_sum_col = f"{reach_col}_sum" if reach_col else None
    if reach_sum_col and reach_sum_col in grouped.columns and "total_engagements" in grouped.columns:
        grouped["eng_rate_by_reach"] = (
            grouped["total_engagements"] / grouped[reach_sum_col] * 100
        ).round(2)

    # Calculate save-to-reach ratio
    saves_col = mapped_columns.get(STD_SAVES)
    if saves_col and f"{saves_col}_sum" in grouped.columns and reach_sum_col in grouped.columns:
        grouped["save_to_reach"] = (
            grouped[f"{saves_col}_sum"] / grouped[reach_sum_col] * 100
        ).round(2)

    grouped = grouped.sort_values("post_count", ascending=False)
    return grouped


def get_top_posts(
    df: pd.DataFrame,
    mapped_columns: Dict[str, str],
    sort_by: str = "reach",
    n: int = 10,
    post_type_filter: Optional[str] = None,
    search_query: Optional[str] = None,
) -> pd.DataFrame:
    """
    Get top performing posts sorted by specified metric.
    
    sort_by options: reach, engagements, engagement_rate, likes, shares, comments
    """
    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()

    # Apply post type filter
    type_col = mapped_columns.get(STD_POST_TYPE)
    if post_type_filter and post_type_filter != "All" and type_col and type_col in result.columns:
        result = result[result[type_col] == post_type_filter]

    # Apply search filter
    post_col = mapped_columns.get(STD_POST)
    if search_query and post_col and post_col in result.columns:
        result = result[
            result[post_col].fillna("").str.contains(search_query, case=False, na=False)
        ]

    # Calculate total engagements for sorting
    eng_cols = []
    for std in [STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES]:
        col = mapped_columns.get(std)
        if col and col in result.columns:
            eng_cols.append(col)

    if eng_cols:
        result["_total_engagements"] = result[eng_cols].sum(axis=1, min_count=1)
    else:
        result["_total_engagements"] = 0

    # Determine sort column
    sort_map = {
        "reach": mapped_columns.get(STD_REACH),
        "engagements": "_total_engagements",
        "engagement_rate": mapped_columns.get(STD_ENGAGEMENT_RATE),
        "likes": mapped_columns.get(STD_LIKES),
        "shares": mapped_columns.get(STD_SHARES),
        "comments": mapped_columns.get(STD_COMMENTS),
        "impressions": mapped_columns.get(STD_IMPRESSIONS),
    }

    sort_col = sort_map.get(sort_by)
    if sort_col and sort_col in result.columns:
        result = result.sort_values(sort_col, ascending=False, na_position="last")
    elif mapped_columns.get(STD_REACH) and mapped_columns[STD_REACH] in result.columns:
        result = result.sort_values(mapped_columns[STD_REACH], ascending=False, na_position="last")

    return result.head(n)


def calculate_viral_score(row: pd.Series, mapped_columns: Dict[str, str], df_stats: dict) -> float:
    """
    Calculate a normalized performance score (0-100) for a post.
    
    Formula: Weighted average of normalized metrics:
    - Reach (30% weight)
    - Engagement rate (30% weight)
    - Total engagements (25% weight)
    - Shares (15% weight)
    
    Each metric is normalized: (value - min) / (max - min) * 100
    
    This score ranks posts relative to others in the dataset.
    It is NOT an absolute measure of virality.
    """
    score = 0
    weights_used = 0

    metric_weights = [
        (STD_REACH, 0.30),
        (STD_ENGAGEMENT_RATE, 0.30),
        ("_total_engagements", 0.25),
        (STD_SHARES, 0.15),
    ]

    for metric, weight in metric_weights:
        col = mapped_columns.get(metric, metric)
        if col in row.index and pd.notna(row.get(col)):
            val = float(row[col])
            stats = df_stats.get(col, {})
            min_v = stats.get("min", 0)
            max_v = stats.get("max", 1)
            if max_v > min_v:
                normalized = (val - min_v) / (max_v - min_v) * 100
            else:
                normalized = 50
            score += normalized * weight
            weights_used += weight

    if weights_used > 0:
        score = score / weights_used
    return round(score, 1)


def get_engagement_distribution(df: pd.DataFrame, mapped_columns: Dict[str, str]) -> dict:
    """Get distribution of engagement types."""
    distribution = {}
    for std, label in [(STD_LIKES, "Likes"), (STD_COMMENTS, "Comments"),
                       (STD_SHARES, "Shares"), (STD_SAVES, "Saves")]:
        col = mapped_columns.get(std)
        if col and col in df.columns:
            total = df[col].sum()
            if not pd.isna(total):
                distribution[label] = float(total)
    return distribution


def calculate_posting_frequency(df: pd.DataFrame, mapped_columns: Dict[str, str]) -> dict:
    """Calculate posting frequency metrics."""
    date_col = mapped_columns.get(STD_DATE)
    if not date_col or date_col not in df.columns:
        return {"posts_per_day": None, "posts_per_week": None}

    dates = pd.to_datetime(df[date_col]).dropna()
    if dates.empty:
        return {"posts_per_day": None, "posts_per_week": None}

    date_range = (dates.max() - dates.min()).days
    if date_range == 0:
        date_range = 1

    total_posts = len(df)
    return {
        "posts_per_day": round(total_posts / date_range, 2),
        "posts_per_week": round(total_posts / max(date_range / 7, 1), 2),
        "total_days": date_range,
        "total_posts": total_posts,
    }


def get_peak_performance(df: pd.DataFrame, mapped_columns: Dict[str, str]) -> dict:
    """Find peak performance metrics."""
    result = {
        "peak_daily_reach": None,
        "peak_daily_reach_date": None,
        "avg_daily_reach": None,
        "engagement_to_reach_ratio": None,
    }

    date_col = mapped_columns.get(STD_DATE)
    reach_col = mapped_columns.get(STD_REACH)

    if date_col and reach_col and date_col in df.columns and reach_col in df.columns:
        daily = df.groupby(pd.to_datetime(df[date_col]).dt.date)[reach_col].sum()
        if not daily.empty:
            result["peak_daily_reach"] = float(daily.max())
            result["peak_daily_reach_date"] = str(daily.idxmax())
            result["avg_daily_reach"] = float(daily.mean())

    # Engagement to reach ratio
    eng_total = 0
    reach_total = 0
    for std in [STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES]:
        col = mapped_columns.get(std)
        if col and col in df.columns:
            eng_total += df[col].sum()
    if reach_col and reach_col in df.columns:
        reach_total = df[reach_col].sum()
    if reach_total > 0:
        result["engagement_to_reach_ratio"] = round(eng_total / reach_total * 100, 2)

    return result


def calculate_save_reach_ratio(df: pd.DataFrame, mapped_columns: Dict[str, str]) -> Optional[float]:
    """Calculate save-to-reach ratio."""
    saves_col = mapped_columns.get(STD_SAVES)
    reach_col = mapped_columns.get(STD_REACH)
    if saves_col and reach_col and saves_col in df.columns and reach_col in df.columns:
        total_saves = df[saves_col].sum()
        total_reach = df[reach_col].sum()
        if total_reach > 0:
            return round(total_saves / total_reach * 100, 2)
    return None


def calculate_comment_like_ratio(df: pd.DataFrame, mapped_columns: Dict[str, str]) -> Optional[float]:
    """Calculate comment-to-like ratio."""
    comments_col = mapped_columns.get(STD_COMMENTS)
    likes_col = mapped_columns.get(STD_LIKES)
    if comments_col and likes_col and comments_col in df.columns and likes_col in df.columns:
        total_comments = df[comments_col].sum()
        total_likes = df[likes_col].sum()
        if total_likes > 0:
            return round(total_comments / total_likes * 100, 2)
    return None
