"""
SocialPulse AI - Data Cleaner
Cleans and preprocesses validated CSV data for analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
from utils.constants import (
    STD_DATE, STD_REACH, STD_IMPRESSIONS, STD_LIKES,
    STD_COMMENTS, STD_SHARES, STD_SAVES, STD_FOLLOWERS,
    STD_POST_TYPE, STD_ENGAGEMENT_RATE
)
from services.column_mapper import normalize_post_types


def clean_dataset(df: pd.DataFrame, mapped_columns: Dict[str, str]) -> pd.DataFrame:
    """
    Clean and preprocess the dataset:
    - Parse dates
    - Convert numeric columns
    - Handle missing values (mark as NaN, not zero)
    - Remove complete duplicate rows
    - Normalize post types
    - Sort by date
    
    Important: Missing metrics are kept as NaN, NOT defaulted to 0.
    This ensures we never silently treat a missing metric as zero.
    """
    cleaned = df.copy()

    # ── Parse dates ─────────────────────────────────────────────────────
    if STD_DATE in mapped_columns:
        date_col = mapped_columns[STD_DATE]
        if date_col in cleaned.columns:
            cleaned[date_col] = pd.to_datetime(cleaned[date_col], errors="coerce")
            # Drop rows with unparseable dates
            before = len(cleaned)
            cleaned = cleaned.dropna(subset=[date_col])
            dropped = before - len(cleaned)

    # ── Convert numeric columns ─────────────────────────────────────────
    numeric_standards = [
        STD_REACH, STD_IMPRESSIONS, STD_LIKES, STD_COMMENTS,
        STD_SHARES, STD_SAVES, STD_FOLLOWERS, STD_ENGAGEMENT_RATE
    ]

    for std_name in numeric_standards:
        if std_name in mapped_columns:
            col = mapped_columns[std_name]
            if col in cleaned.columns:
                # Convert to numeric, keeping NaN for non-numeric values
                cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
                # Replace negatives with NaN for metrics that can't be negative
                if std_name not in [STD_FOLLOWERS]:  # Follower growth can be negative
                    cleaned.loc[cleaned[col] < 0, col] = np.nan

    # ── Remove exact duplicate rows ─────────────────────────────────────
    cleaned = cleaned.drop_duplicates()

    # ── Normalize post types ────────────────────────────────────────────
    if STD_POST_TYPE in mapped_columns:
        type_col = mapped_columns[STD_POST_TYPE]
        if type_col in cleaned.columns:
            cleaned = normalize_post_types(cleaned, type_col)

    # ── Sort by date ────────────────────────────────────────────────────
    if STD_DATE in mapped_columns:
        date_col = mapped_columns[STD_DATE]
        if date_col in cleaned.columns:
            cleaned = cleaned.sort_values(date_col).reset_index(drop=True)

    # ── Strip whitespace from string columns ────────────────────────────
    for col in cleaned.select_dtypes(include=["object"]).columns:
        cleaned[col] = cleaned[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    return cleaned


def calculate_missing_engagement_rate(
    df: pd.DataFrame, mapped_columns: Dict[str, str]
) -> pd.DataFrame:
    """
    Calculate engagement rate per post if not already present.
    
    Formula: Engagement Rate = (Likes + Comments + Shares + Saves) / Reach * 100
    
    Only calculates using available interaction columns.
    Sets to NaN if reach is 0 or missing.
    """
    df = df.copy()

    # Check if engagement rate column already exists and is populated
    er_col = mapped_columns.get(STD_ENGAGEMENT_RATE)
    if er_col and er_col in df.columns:
        # Already has engagement rate, check if populated
        if df[er_col].notna().sum() > 0:
            return df

    # Calculate from components
    engagement_cols = []
    for std in [STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES]:
        if std in mapped_columns and mapped_columns[std] in df.columns:
            engagement_cols.append(mapped_columns[std])

    reach_col = mapped_columns.get(STD_REACH)

    if not engagement_cols or not reach_col or reach_col not in df.columns:
        return df

    # Sum engagement (treating NaN as 0 within row but only if at least one value exists)
    engagement_sum = df[engagement_cols].sum(axis=1, min_count=1)
    reach = df[reach_col]

    # Calculate rate - NaN where reach is 0 or missing
    calc_col = "_calculated_engagement_rate"
    df[calc_col] = np.where(
        (reach > 0) & reach.notna() & engagement_sum.notna(),
        (engagement_sum / reach) * 100,
        np.nan
    )

    # Update or create the engagement rate column
    if er_col and er_col in df.columns:
        # Fill in missing values in existing column
        df[er_col] = df[er_col].fillna(df[calc_col])
        df = df.drop(columns=[calc_col])
    else:
        # Create new column
        er_new_col = "Engagement_Rate"
        df[er_new_col] = df[calc_col]
        df = df.drop(columns=[calc_col])
        mapped_columns[STD_ENGAGEMENT_RATE] = er_new_col

    return df


def get_cleaning_summary(original_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> dict:
    """Generate a summary of cleaning operations performed."""
    return {
        "original_rows": len(original_df),
        "cleaned_rows": len(cleaned_df),
        "rows_removed": len(original_df) - len(cleaned_df),
        "duplicates_removed": len(original_df) - len(original_df.drop_duplicates()),
        "columns": len(cleaned_df.columns),
    }
