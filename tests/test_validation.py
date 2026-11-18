"""
SocialPulse AI - Tests for Data Validation
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.data_validator import validate_dataset, get_health_rating
from utils.constants import (
    STD_DATE, STD_REACH, STD_IMPRESSIONS, STD_LIKES,
    STD_COMMENTS, STD_POST_TYPE
)


@pytest.fixture
def valid_df():
    return pd.DataFrame({
        "Date": ["2024-08-01", "2024-08-02", "2024-08-03"],
        "Reach": [1000, 2000, 3000],
        "Impressions": [1500, 3000, 4500],
        "Likes": [100, 200, 300],
        "Comments": [10, 20, 30],
    })


@pytest.fixture
def valid_mapping():
    return {
        STD_DATE: "Date",
        STD_REACH: "Reach",
        STD_IMPRESSIONS: "Impressions",
        STD_LIKES: "Likes",
        STD_COMMENTS: "Comments",
    }


class TestValidation:
    def test_valid_dataset(self, valid_df, valid_mapping):
        result = validate_dataset(valid_df, valid_mapping)
        assert result["is_valid"] is True
        assert result["total_records"] == 3
        assert result["health_score"] > 50

    def test_empty_dataset(self, valid_mapping):
        result = validate_dataset(pd.DataFrame(), valid_mapping)
        assert result["is_valid"] is False
        assert result["health_score"] == 0

    def test_missing_required_columns(self, valid_df):
        result = validate_dataset(valid_df, {})  # No date column mapped
        assert result["has_required_columns"] is False
        assert len(result["issues"]) > 0

    def test_invalid_dates(self, valid_mapping):
        df = pd.DataFrame({
            "Date": ["2024-08-01", "not-a-date", "2024-08-03"],
            "Reach": [1000, 2000, 3000],
            "Impressions": [1500, 3000, 4500],
            "Likes": [100, 200, 300],
            "Comments": [10, 20, 30],
        })
        result = validate_dataset(df, valid_mapping)
        assert len(result["warnings"]) > 0

    def test_negative_values(self, valid_mapping):
        df = pd.DataFrame({
            "Date": ["2024-08-01", "2024-08-02"],
            "Reach": [1000, -500],
            "Impressions": [1500, 3000],
            "Likes": [100, 200],
            "Comments": [10, 20],
        })
        result = validate_dataset(df, valid_mapping)
        assert len(result["warnings"]) > 0

    def test_duplicates(self, valid_mapping):
        df = pd.DataFrame({
            "Date": ["2024-08-01", "2024-08-01", "2024-08-02"],
            "Reach": [1000, 1000, 2000],
            "Impressions": [1500, 1500, 3000],
            "Likes": [100, 100, 200],
            "Comments": [10, 10, 20],
        })
        result = validate_dataset(df, valid_mapping)
        assert result["duplicate_records"] > 0

    def test_missing_values(self, valid_mapping):
        df = pd.DataFrame({
            "Date": ["2024-08-01", "2024-08-02", "2024-08-03"],
            "Reach": [1000, None, 3000],
            "Impressions": [1500, 3000, None],
            "Likes": [100, 200, 300],
            "Comments": [10, 20, 30],
        })
        result = validate_dataset(df, valid_mapping)
        assert len(result["missing_values"]) > 0


class TestHealthRating:
    def test_optimal(self):
        assert get_health_rating(95) == "OPTIMAL"

    def test_good(self):
        assert get_health_rating(80) == "GOOD"

    def test_fair(self):
        assert get_health_rating(60) == "FAIR"

    def test_poor(self):
        assert get_health_rating(30) == "POOR"

    def test_critical(self):
        assert get_health_rating(10) == "CRITICAL"
