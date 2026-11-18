"""
SocialPulse AI - Session State Manager
Manages Streamlit session state for data persistence across pages.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any


def init_session_state():
    """Initialize all session state variables if not already set."""
    defaults = {
        "df": None,                        # Main processed dataframe
        "raw_df": None,                    # Original uploaded dataframe
        "platform": "Instagram",           # Selected platform
        "mapped_columns": {},              # {standard_name: actual_col_name}
        "unmapped_columns": [],            # Columns that couldn't be mapped
        "validation_results": None,        # Validation report dict
        "date_range": None,                # (start_date, end_date)
        "current_page": "Dashboard Overview",
        "comparison_enabled": False,       # Period comparison toggle
        "ai_insights": None,               # Cached AI insights
        "dataset_name": None,              # Uploaded file name
        "upload_timestamp": None,          # When data was uploaded
        "data_quality": None,              # Data quality metrics
        "available_metrics": [],           # Which metrics are available
        "missing_metrics": [],             # Which metrics are missing
        "filters": {                       # Active filters
            "date_start": None,
            "date_end": None,
            "post_type": "All",
            "sort_by": "Reach",
        },
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def get_dataframe() -> Optional[pd.DataFrame]:
    """Get the current processed dataframe from session state."""
    init_session_state()
    return st.session_state.get("df", None)


def set_dataframe(df: pd.DataFrame, name: str = "uploaded_data"):
    """Store processed dataframe in session state."""
    init_session_state()
    st.session_state.df = df
    st.session_state.dataset_name = name
    st.session_state.upload_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Clear cached AI insights when new data is loaded
    st.session_state.ai_insights = None


def get_raw_dataframe() -> Optional[pd.DataFrame]:
    """Get the raw uploaded dataframe."""
    return st.session_state.get("raw_df", None)


def set_raw_dataframe(df: pd.DataFrame):
    """Store raw dataframe."""
    st.session_state.raw_df = df


def clear_dataset():
    """Clear all data from session state."""
    st.session_state.df = None
    st.session_state.raw_df = None
    st.session_state.mapped_columns = {}
    st.session_state.unmapped_columns = []
    st.session_state.validation_results = None
    st.session_state.date_range = None
    st.session_state.ai_insights = None
    st.session_state.dataset_name = None
    st.session_state.upload_timestamp = None
    st.session_state.data_quality = None
    st.session_state.available_metrics = []
    st.session_state.missing_metrics = []


def get_mapped_col(standard_name: str) -> Optional[str]:
    """Get the actual column name for a standard metric name."""
    init_session_state()
    return st.session_state.mapped_columns.get(standard_name, None)


def has_column(standard_name: str) -> bool:
    """Check if a standard column is available in the mapped dataset."""
    init_session_state()
    col = get_mapped_col(standard_name)
    if col is None:
        return False
    df = get_dataframe()
    if df is None:
        return False
    return col in df.columns


def get_column_values(standard_name: str) -> Optional[pd.Series]:
    """Get the series for a mapped column."""
    col = get_mapped_col(standard_name)
    df = get_dataframe()
    if col is None or df is None or col not in df.columns:
        return None
    return df[col]


def get_platform() -> str:
    """Get current platform selection."""
    init_session_state()
    return st.session_state.get("platform", "Instagram")


def set_platform(platform: str):
    """Set the current platform."""
    st.session_state.platform = platform


def set_mapped_columns(mapping: Dict[str, str]):
    """Store the column mapping."""
    st.session_state.mapped_columns = mapping

    # Determine available and missing metrics
    available = []
    missing = []
    from utils.constants import STD_REACH, STD_IMPRESSIONS, STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES, STD_FOLLOWERS
    metric_list = [STD_REACH, STD_IMPRESSIONS, STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES, STD_FOLLOWERS]

    for m in metric_list:
        if m in mapping and mapping[m]:
            available.append(m)
        else:
            missing.append(m)

    st.session_state.available_metrics = available
    st.session_state.missing_metrics = missing


def set_date_range(start, end):
    """Store the date range."""
    st.session_state.date_range = (start, end)


def set_validation_results(results: dict):
    """Store validation results."""
    st.session_state.validation_results = results


def set_data_quality(quality: dict):
    """Store data quality metrics."""
    st.session_state.data_quality = quality


def get_dataset_info() -> dict:
    """Get summary info about the current dataset."""
    init_session_state()
    df = get_dataframe()
    info = {
        "has_data": df is not None and not df.empty,
        "name": st.session_state.dataset_name,
        "timestamp": st.session_state.upload_timestamp,
        "platform": st.session_state.platform,
        "rows": len(df) if df is not None else 0,
        "columns": len(df.columns) if df is not None else 0,
        "date_range": st.session_state.date_range,
        "available_metrics": st.session_state.available_metrics,
        "missing_metrics": st.session_state.missing_metrics,
    }
    return info


def is_data_loaded() -> bool:
    """Check if data has been loaded and processed."""
    init_session_state()
    df = get_dataframe()
    return df is not None and not df.empty
