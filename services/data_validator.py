"""
SocialPulse AI - Data Validator
Validates uploaded CSV data for completeness, correctness, and quality.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from utils.constants import (
    STD_DATE, STD_REACH, STD_IMPRESSIONS, STD_LIKES,
    STD_COMMENTS, STD_SHARES, STD_SAVES, STD_FOLLOWERS,
    STD_POST_TYPE, STD_POST, REQUIRED_COLUMNS, RECOMMENDED_COLUMNS
)


def validate_dataset(df: pd.DataFrame, mapped_columns: Dict[str, str]) -> dict:
    """
    Comprehensive dataset validation.
    
    Returns a validation report dictionary with:
    - is_valid: bool
    - total_records, valid_records, invalid_records
    - issues: list of issue descriptions
    - warnings: list of warning descriptions
    - column_checks: per-column validation results
    - duplicates: count of duplicate rows
    - missing_values: summary of missing values
    - health_score: 0-100 data quality percentage
    """
    report = {
        "is_valid": True,
        "total_records": len(df),
        "valid_records": len(df),
        "invalid_records": 0,
        "corrupted_records": 0,
        "duplicate_records": 0,
        "issues": [],
        "warnings": [],
        "column_checks": {},
        "missing_values": {},
        "health_score": 100,
        "date_range_start": None,
        "date_range_end": None,
        "has_required_columns": True,
    }

    if df is None or df.empty:
        report["is_valid"] = False
        report["health_score"] = 0
        report["issues"].append("Dataset is empty.")
        return report

    # ── Check required columns ──────────────────────────────────────────
    for req_col in REQUIRED_COLUMNS:
        if req_col not in mapped_columns:
            report["issues"].append(f"Required column '{req_col}' could not be mapped from your CSV.")
            report["has_required_columns"] = False
            report["is_valid"] = False

    # ── Check recommended columns ───────────────────────────────────────
    for rec_col in RECOMMENDED_COLUMNS:
        if rec_col not in mapped_columns:
            report["warnings"].append(
                f"Recommended column '{rec_col}' not found. Some metrics will be unavailable."
            )

    # ── Validate date column ────────────────────────────────────────────
    if STD_DATE in mapped_columns:
        date_col = mapped_columns[STD_DATE]
        if date_col in df.columns:
            dates = pd.to_datetime(df[date_col], errors="coerce")
            invalid_dates = dates.isna().sum()
            original_na = df[date_col].isna().sum()
            bad_dates = invalid_dates - original_na

            if bad_dates > 0:
                report["warnings"].append(
                    f"{bad_dates} record(s) have invalid or unparseable dates."
                )

            valid_dates = dates.dropna()
            if not valid_dates.empty:
                report["date_range_start"] = valid_dates.min()
                report["date_range_end"] = valid_dates.max()

            report["column_checks"]["date"] = {
                "column": date_col,
                "valid": int(len(df) - invalid_dates),
                "invalid": int(invalid_dates),
                "status": "ok" if bad_dates == 0 else "warning"
            }

    # ── Validate numeric columns ────────────────────────────────────────
    numeric_standards = [
        STD_REACH, STD_IMPRESSIONS, STD_LIKES, STD_COMMENTS,
        STD_SHARES, STD_SAVES, STD_FOLLOWERS
    ]

    total_issues = 0
    for std_name in numeric_standards:
        if std_name in mapped_columns:
            col = mapped_columns[std_name]
            if col in df.columns:
                numeric_vals = pd.to_numeric(df[col], errors="coerce")
                na_count = numeric_vals.isna().sum()
                negative_count = (numeric_vals < 0).sum()

                issues_for_col = []
                if na_count > 0:
                    issues_for_col.append(f"{na_count} non-numeric/missing values")
                if negative_count > 0:
                    issues_for_col.append(f"{negative_count} negative values")
                    report["warnings"].append(
                        f"Column '{col}' ({std_name}) has {negative_count} negative values."
                    )

                total_issues += na_count + negative_count

                report["column_checks"][std_name] = {
                    "column": col,
                    "valid": int(len(df) - na_count),
                    "invalid": int(na_count),
                    "negatives": int(negative_count),
                    "status": "ok" if na_count == 0 and negative_count == 0 else "warning"
                }

                # Track missing values
                if na_count > 0:
                    report["missing_values"][col] = int(na_count)

    # ── Check for duplicate rows ────────────────────────────────────────
    duplicate_count = df.duplicated().sum()
    report["duplicate_records"] = int(duplicate_count)
    if duplicate_count > 0:
        report["warnings"].append(f"{duplicate_count} duplicate record(s) found.")

    # ── Check post type column ──────────────────────────────────────────
    if STD_POST_TYPE in mapped_columns:
        type_col = mapped_columns[STD_POST_TYPE]
        if type_col in df.columns:
            type_na = df[type_col].isna().sum()
            unique_types = df[type_col].dropna().nunique()
            report["column_checks"]["post_type"] = {
                "column": type_col,
                "unique_values": int(unique_types),
                "missing": int(type_na),
                "detected_types": df[type_col].dropna().unique().tolist(),
                "status": "ok"
            }

    # ── Calculate health score ──────────────────────────────────────────
    total_cells = len(df) * len(mapped_columns)
    if total_cells > 0:
        total_missing = sum(report["missing_values"].values())
        completeness = max(0, (1 - total_missing / total_cells)) * 100

        # Deductions
        deductions = 0
        if not report["has_required_columns"]:
            deductions += 20
        if duplicate_count > 0:
            deductions += min(10, duplicate_count / len(df) * 100)
        if total_issues > 0:
            deductions += min(15, total_issues / len(df) * 50)
        for issue in report["issues"]:
            deductions += 5

        report["health_score"] = max(0, min(100, completeness - deductions))
    else:
        report["health_score"] = 0

    # ── Count valid vs invalid records ──────────────────────────────────
    # A record is "invalid" if it has any critical missing values
    critical_cols = []
    for std in [STD_DATE, STD_REACH, STD_IMPRESSIONS]:
        if std in mapped_columns and mapped_columns[std] in df.columns:
            critical_cols.append(mapped_columns[std])

    if critical_cols:
        invalid_mask = df[critical_cols].isna().any(axis=1)
        report["invalid_records"] = int(invalid_mask.sum())
        report["valid_records"] = int(len(df) - invalid_mask.sum())
    
    report["corrupted_records"] = report["invalid_records"]

    # Overall validity
    if report["health_score"] < 20:
        report["is_valid"] = False

    return report


def get_health_rating(score: float) -> str:
    """Get a text rating for the health score."""
    if score >= 90:
        return "OPTIMAL"
    elif score >= 75:
        return "GOOD"
    elif score >= 50:
        return "FAIR"
    elif score >= 25:
        return "POOR"
    else:
        return "CRITICAL"


def get_health_color(score: float) -> str:
    """Get color for health score."""
    if score >= 75:
        return "#00885D"
    elif score >= 50:
        return "#F59E0B"
    else:
        return "#DC3545"
