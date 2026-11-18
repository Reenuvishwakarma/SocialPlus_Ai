"""
SocialPulse AI - Helper Utilities
Common helper functions for data processing, calculations, and validation.
"""
import pandas as pd
import numpy as np
from typing import Optional, Tuple, List, Any
from datetime import datetime


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safe division handling zero and None values."""
    try:
        a = float(a) if a is not None else 0
        b = float(b) if b is not None else 0
        if b == 0:
            return default
        return a / b
    except (ValueError, TypeError):
        return default


def calculate_percentage_change(current: float, previous: float) -> Optional[float]:
    """
    Calculate percentage change: ((current - previous) / |previous|) * 100.
    Returns None if previous is zero or values are invalid.
    """
    try:
        current = float(current)
        previous = float(previous)
        if previous == 0:
            return None
        return ((current - previous) / abs(previous)) * 100
    except (ValueError, TypeError):
        return None


def get_date_range(df: pd.DataFrame, date_col: str) -> Tuple[Optional[Any], Optional[Any]]:
    """Get min and max dates from dataframe column."""
    if df is None or date_col not in df.columns:
        return None, None
    try:
        dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
        if dates.empty:
            return None, None
        return dates.min(), dates.max()
    except Exception:
        return None, None


def split_period(df: pd.DataFrame, date_col: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split dataframe into current period (second half) and previous period (first half)
    based on the date column midpoint.
    """
    if df is None or date_col not in df.columns or df.empty:
        return pd.DataFrame(), pd.DataFrame()

    try:
        df_sorted = df.copy()
        df_sorted[date_col] = pd.to_datetime(df_sorted[date_col], errors="coerce")
        df_sorted = df_sorted.dropna(subset=[date_col]).sort_values(date_col)

        if df_sorted.empty:
            return pd.DataFrame(), pd.DataFrame()

        min_date = df_sorted[date_col].min()
        max_date = df_sorted[date_col].max()
        mid_date = min_date + (max_date - min_date) / 2

        current = df_sorted[df_sorted[date_col] > mid_date]
        previous = df_sorted[df_sorted[date_col] <= mid_date]

        return current, previous
    except Exception:
        return pd.DataFrame(), pd.DataFrame()


def filter_by_date_range(
    df: pd.DataFrame, date_col: str, start=None, end=None
) -> pd.DataFrame:
    """Filter dataframe by date range."""
    if df is None or date_col not in df.columns:
        return df if df is not None else pd.DataFrame()

    try:
        filtered = df.copy()
        filtered[date_col] = pd.to_datetime(filtered[date_col], errors="coerce")

        if start is not None:
            start = pd.to_datetime(start)
            filtered = filtered[filtered[date_col] >= start]
        if end is not None:
            end = pd.to_datetime(end)
            filtered = filtered[filtered[date_col] <= end]

        return filtered
    except Exception:
        return df


def detect_post_types(df: pd.DataFrame, type_col: str) -> List[str]:
    """Return unique post types from dataframe."""
    if df is None or type_col not in df.columns:
        return []
    try:
        types = df[type_col].dropna().unique().tolist()
        return [str(t) for t in types if str(t).strip()]
    except Exception:
        return []


def get_color_for_change(val: Optional[float]) -> str:
    """Return color string based on change direction."""
    if val is None:
        return "#767586"
    if val > 0:
        return "#00885D"
    elif val < 0:
        return "#DC3545"
    return "#767586"


def clean_column_name(name: str) -> str:
    """Clean a column name by stripping whitespace and normalizing."""
    if not isinstance(name, str):
        return str(name)
    return name.strip()


def validate_numeric_column(series: pd.Series) -> pd.Series:
    """Convert series to numeric, coercing errors to NaN."""
    return pd.to_numeric(series, errors="coerce")


def compute_rolling_average(series: pd.Series, window: int = 7) -> pd.Series:
    """Compute rolling average over a window."""
    return series.rolling(window=window, min_periods=1).mean()


def calculate_weekly_aggregates(df: pd.DataFrame, date_col: str, metric_cols: List[str]) -> pd.DataFrame:
    """Aggregate metrics by week."""
    if df is None or date_col not in df.columns:
        return pd.DataFrame()

    try:
        weekly = df.copy()
        weekly[date_col] = pd.to_datetime(weekly[date_col], errors="coerce")
        weekly = weekly.set_index(date_col)

        agg_dict = {col: "sum" for col in metric_cols if col in weekly.columns}
        if not agg_dict:
            return pd.DataFrame()

        result = weekly.resample("W")[list(agg_dict.keys())].sum().reset_index()
        return result
    except Exception:
        return pd.DataFrame()


def calculate_cumulative(series: pd.Series) -> pd.Series:
    """Calculate cumulative sum of a series."""
    return series.cumsum()


def normalize_score(value: float, min_val: float, max_val: float) -> float:
    """Normalize a value to 0-100 scale."""
    if max_val == min_val:
        return 50.0
    return max(0, min(100, ((value - min_val) / (max_val - min_val)) * 100))
