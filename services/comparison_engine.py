"""
SocialPulse AI - Comparison Engine
Handles period-over-period comparison calculations.
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from utils.constants import (
    STD_DATE, STD_REACH, STD_IMPRESSIONS, STD_LIKES,
    STD_COMMENTS, STD_SHARES, STD_SAVES, STD_FOLLOWERS,
    STD_ENGAGEMENT_RATE
)
from utils.helpers import safe_divide, calculate_percentage_change
from services.analytics_engine import calculate_kpis


def split_into_periods(
    df: pd.DataFrame, 
    mapped_columns: Dict[str, str]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split the dataset into two equal periods for comparison.
    
    Strategy: Split by the midpoint of the date range.
    - Previous period: First half of the date range
    - Current period: Second half of the date range
    
    Returns: (current_period_df, previous_period_df)
    """
    date_col = mapped_columns.get(STD_DATE)
    if not date_col or date_col not in df.columns:
        return df, pd.DataFrame()

    df_sorted = df.copy()
    df_sorted[date_col] = pd.to_datetime(df_sorted[date_col], errors="coerce")
    df_sorted = df_sorted.dropna(subset=[date_col]).sort_values(date_col)

    if df_sorted.empty:
        return df, pd.DataFrame()

    min_date = df_sorted[date_col].min()
    max_date = df_sorted[date_col].max()
    mid_date = min_date + (max_date - min_date) / 2

    current = df_sorted[df_sorted[date_col] > mid_date].copy()
    previous = df_sorted[df_sorted[date_col] <= mid_date].copy()

    return current, previous


def compare_periods(
    df: pd.DataFrame, 
    mapped_columns: Dict[str, str]
) -> dict:
    """
    Compare current period vs previous period for all KPIs.
    
    Returns a dict with each metric containing:
    - current_value: current period metric value
    - previous_value: previous period metric value
    - absolute_change: current - previous
    - percentage_change: ((current - previous) / |previous|) × 100
    - direction: "up", "down", or "neutral"
    """
    current_df, previous_df = split_into_periods(df, mapped_columns)

    comparison = {}

    if current_df.empty or previous_df.empty:
        return comparison

    current_kpis = calculate_kpis(current_df, mapped_columns)
    previous_kpis = calculate_kpis(previous_df, mapped_columns)

    # Date ranges
    date_col = mapped_columns.get(STD_DATE)
    if date_col:
        comparison["current_period"] = {
            "start": current_df[date_col].min(),
            "end": current_df[date_col].max(),
            "posts": len(current_df),
        }
        comparison["previous_period"] = {
            "start": previous_df[date_col].min(),
            "end": previous_df[date_col].max(),
            "posts": len(previous_df),
        }

    # Compare each KPI
    metrics_to_compare = [
        "total_reach", "total_impressions", "total_engagements",
        "avg_engagement_rate", "net_follower_growth",
        "total_likes", "total_comments", "total_shares", "total_saves"
    ]

    for metric in metrics_to_compare:
        curr = current_kpis.get(metric, {})
        prev = previous_kpis.get(metric, {})

        curr_val = curr.get("value") if curr.get("available") else None
        prev_val = prev.get("value") if prev.get("available") else None

        metric_comparison = {
            "current_value": curr_val,
            "previous_value": prev_val,
            "absolute_change": None,
            "percentage_change": None,
            "direction": "neutral",
            "available": curr_val is not None and prev_val is not None,
        }

        if curr_val is not None and prev_val is not None:
            metric_comparison["absolute_change"] = curr_val - prev_val
            metric_comparison["percentage_change"] = calculate_percentage_change(curr_val, prev_val)

            if curr_val > prev_val:
                metric_comparison["direction"] = "up"
            elif curr_val < prev_val:
                metric_comparison["direction"] = "down"

        comparison[metric] = metric_comparison

    return comparison


def get_comparison_summary(comparison: dict) -> dict:
    """
    Generate a human-readable comparison summary.
    """
    summary = {
        "improving_metrics": [],
        "declining_metrics": [],
        "stable_metrics": [],
        "overall_direction": "neutral",
    }

    metric_labels = {
        "total_reach": "Total Reach",
        "total_impressions": "Total Impressions",
        "total_engagements": "Total Engagements",
        "avg_engagement_rate": "Avg Engagement Rate",
        "net_follower_growth": "Net Follower Growth",
        "total_likes": "Total Likes",
        "total_comments": "Total Comments",
        "total_shares": "Total Shares",
        "total_saves": "Total Saves",
    }

    improving = 0
    declining = 0

    for metric, label in metric_labels.items():
        data = comparison.get(metric, {})
        if not data.get("available", False):
            continue

        pct = data.get("percentage_change")
        direction = data.get("direction", "neutral")

        if direction == "up":
            summary["improving_metrics"].append({
                "label": label,
                "change": pct,
            })
            improving += 1
        elif direction == "down":
            summary["declining_metrics"].append({
                "label": label,
                "change": pct,
            })
            declining += 1
        else:
            summary["stable_metrics"].append({"label": label})

    if improving > declining:
        summary["overall_direction"] = "improving"
    elif declining > improving:
        summary["overall_direction"] = "declining"
    else:
        summary["overall_direction"] = "mixed"

    return summary
