"""
SocialPulse AI - Tests for Comparison Engine
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.comparison_engine import split_into_periods, compare_periods, get_comparison_summary
from utils.constants import (
    STD_DATE, STD_REACH, STD_IMPRESSIONS, STD_LIKES,
    STD_COMMENTS, STD_SHARES, STD_SAVES, STD_FOLLOWERS,
    STD_ENGAGEMENT_RATE
)


@pytest.fixture
def comparison_df():
    """DataFrame with clear first-half vs second-half data."""
    dates = pd.date_range("2024-08-01", periods=20, freq="D")
    data = {
        "Date": dates,
        "Reach": [1000]*10 + [2000]*10,  # Second half has double reach
        "Impressions": [1500]*10 + [3000]*10,
        "Likes": [100]*10 + [200]*10,
        "Comments": [10]*10 + [20]*10,
        "Shares": [5]*10 + [10]*10,
        "Saves": [3]*10 + [6]*10,
        "Followers": list(range(42000, 42020)),
        "Engagement_Rate": [5.0]*10 + [6.0]*10,
    }
    return pd.DataFrame(data)


@pytest.fixture
def comp_mapping():
    return {
        STD_DATE: "Date",
        STD_REACH: "Reach",
        STD_IMPRESSIONS: "Impressions",
        STD_LIKES: "Likes",
        STD_COMMENTS: "Comments",
        STD_SHARES: "Shares",
        STD_SAVES: "Saves",
        STD_FOLLOWERS: "Followers",
        STD_ENGAGEMENT_RATE: "Engagement_Rate",
    }


class TestSplitPeriods:
    def test_split_even(self, comparison_df, comp_mapping):
        current, previous = split_into_periods(comparison_df, comp_mapping)
        assert len(current) > 0
        assert len(previous) > 0
        assert len(current) + len(previous) == len(comparison_df)

    def test_split_no_date(self, comparison_df):
        current, previous = split_into_periods(comparison_df, {})
        assert len(previous) == 0  # Can't split without date


class TestComparePeriods:
    def test_comparison_direction(self, comparison_df, comp_mapping):
        result = compare_periods(comparison_df, comp_mapping)
        # Reach doubles in second half so should be "up"
        assert result["total_reach"]["direction"] == "up"
        assert result["total_reach"]["available"] is True

    def test_percentage_change(self, comparison_df, comp_mapping):
        result = compare_periods(comparison_df, comp_mapping)
        reach_pct = result["total_reach"]["percentage_change"]
        # Second half: 2000*10=20000, First half: 1000*10=10000
        # Change: (20000-10000)/10000*100 = 100%
        assert reach_pct is not None
        assert reach_pct == pytest.approx(100.0, abs=5)

    def test_empty_df(self, comp_mapping):
        result = compare_periods(pd.DataFrame(), comp_mapping)
        assert len(result) == 0


class TestComparisonSummary:
    def test_improving_summary(self, comparison_df, comp_mapping):
        comparison = compare_periods(comparison_df, comp_mapping)
        summary = get_comparison_summary(comparison)
        assert summary["overall_direction"] == "improving"
        assert len(summary["improving_metrics"]) > 0

    def test_empty_comparison(self):
        summary = get_comparison_summary({})
        # With no metrics to compare, equal counts of improving/declining (both 0) → "mixed"
        assert summary["overall_direction"] in ("neutral", "mixed")
