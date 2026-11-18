"""
SocialPulse AI - Column Mapper
Automatically maps CSV columns to standard metric names.
"""
import pandas as pd
from typing import Dict, List, Tuple, Optional
from utils.constants import COLUMN_MAPPING, POST_TYPE_MAPPING


def auto_map_columns(df: pd.DataFrame) -> Tuple[Dict[str, str], List[str]]:
    """
    Automatically map CSV columns to standard column names.
    
    Returns:
        Tuple of (mapped_dict, unmapped_columns)
        mapped_dict: {standard_name: actual_column_name}
        unmapped_columns: list of CSV columns that were not mapped
    """
    mapped = {}
    used_columns = set()

    csv_columns = list(df.columns)

    for standard_name, possible_names in COLUMN_MAPPING.items():
        matched = False
        # First try exact match
        for col in csv_columns:
            if col in used_columns:
                continue
            clean_col = col.strip()
            if clean_col in possible_names:
                mapped[standard_name] = col
                used_columns.add(col)
                matched = True
                break

        # Then try case-insensitive match
        if not matched:
            for col in csv_columns:
                if col in used_columns:
                    continue
                clean_col = col.strip().lower()
                for possible in possible_names:
                    if clean_col == possible.lower():
                        mapped[standard_name] = col
                        used_columns.add(col)
                        matched = True
                        break
                if matched:
                    break

        # Then try partial / contains match
        if not matched:
            for col in csv_columns:
                if col in used_columns:
                    continue
                clean_col = col.strip().lower().replace("_", " ").replace("-", " ")
                for possible in possible_names:
                    possible_clean = possible.lower().replace("_", " ").replace("-", " ")
                    if possible_clean in clean_col or clean_col in possible_clean:
                        mapped[standard_name] = col
                        used_columns.add(col)
                        matched = True
                        break
                if matched:
                    break

    unmapped = [col for col in csv_columns if col not in used_columns]

    return mapped, unmapped


def get_mapping_report(mapped: Dict[str, str], unmapped: List[str]) -> dict:
    """Generate a human-readable mapping report."""
    report = {
        "total_mapped": len(mapped),
        "total_unmapped": len(unmapped),
        "mappings": [],
        "unmapped_columns": unmapped,
    }

    from utils.constants import (
        STD_DATE, STD_POST, STD_REACH, STD_IMPRESSIONS,
        STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES,
        STD_FOLLOWERS, STD_POST_TYPE
    )

    category_map = {
        STD_DATE: "Date / Timestamp",
        STD_POST: "Post Content",
        "post_id": "Post ID / Permalink",
        STD_REACH: "Reach & Impressions",
        STD_IMPRESSIONS: "Reach & Impressions",
        STD_LIKES: "Likes, Comments, Shares, Saves",
        STD_COMMENTS: "Likes, Comments, Shares, Saves",
        STD_SHARES: "Likes, Comments, Shares, Saves",
        STD_SAVES: "Likes, Comments, Shares, Saves",
        STD_FOLLOWERS: "Audience/Cached",
        STD_POST_TYPE: "Content Type / Format",
    }

    for std_name, actual_col in mapped.items():
        category = category_map.get(std_name, "Other")
        report["mappings"].append({
            "standard": std_name,
            "actual": actual_col,
            "category": category,
            "status": "Mapped"
        })

    return report


def normalize_post_types(df: pd.DataFrame, type_col: str) -> pd.DataFrame:
    """Normalize post type values to standard names."""
    if type_col not in df.columns:
        return df

    df = df.copy()

    def normalize(val):
        if pd.isna(val):
            return "Other"
        val_str = str(val).strip()
        # Check exact match first
        if val_str in POST_TYPE_MAPPING:
            return POST_TYPE_MAPPING[val_str]
        # Case-insensitive
        val_lower = val_str.lower()
        if val_lower in POST_TYPE_MAPPING:
            return POST_TYPE_MAPPING[val_lower]
        # Contains match
        for key, normalized in POST_TYPE_MAPPING.items():
            if key.lower() in val_lower:
                return normalized
        return val_str if val_str else "Other"

    df[type_col] = df[type_col].apply(normalize)
    return df


def apply_manual_mapping(df: pd.DataFrame, manual_map: Dict[str, str]) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Apply a manual column mapping provided by the user.
    manual_map: {standard_name: csv_column_name}
    """
    mapped = {}
    for std_name, csv_col in manual_map.items():
        if csv_col and csv_col in df.columns:
            mapped[std_name] = csv_col

    return df, mapped
