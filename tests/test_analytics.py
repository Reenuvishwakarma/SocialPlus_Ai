"""
SocialPulse AI - Tests for Analytics Engine
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.analytics_engine import (
    calculate_kpis, calculate_daily_metrics, calculate_format_performance,
    get_top_posts, get_engagement_distribution, calculate_posting_frequency,
    get_peak_performance
)
from utils.constants import (
    STD_DATE, STD_REACH, STD_IMPRESSIONS, STD_LIKES,
    STD_COMMENTS, STD_SHARES, STD_SAVES, STD_FOLLOWERS,
    STD_POST_TYPE, STD_ENGAGEMENT_RATE
)


@pytest.fixture
def sample_df():
    """Create a sample dataframe for testing."""
    data = {
        "Date": pd.to_datetime([
            "2024-08-01", "2024-08-02", "2024-08-03", "2024-08-04", "2024-08-05",
            "2024-08-06", "2024-08-07", "2024-08-08", "2024-08-09", "2024-08-10"
        ]),
        "Caption": [
            "Post about AI", "Marketing tips", "Product launch", "Behind scenes",
            "Tutorial video", "Client story", "Industry news", "Team update",
            "Quick tip", "Weekend vibes"
        ],
        "Post_Type": ["REELS", "CAROUSEL", "STATIC", "REELS", "CAROUSEL",
                      "STATIC", "REELS", "CAROUSEL", "STATIC", "REELS"],
        "Reach": [15000, 12000, 5000, 20000, 18000, 4000, 25000, 10000, 3000, 30000],
        "Impressions": [22000, 18000, 7500, 30000, 27000, 6000, 37000, 15000, 4500, 45000],
        "Likes": [800, 600, 200, 1200, 900, 150, 1500, 500, 100, 2000],
        "Comments": [50, 40, 10, 80, 60, 8, 100, 30, 5, 120],
        "Shares": [30, 25, 5, 50, 40, 3, 70, 20, 2, 80],
        "Saves": [20, 50, 8, 30, 80, 5, 40, 60, 3, 50],
        "Followers": [42000, 42020, 42030, 42050, 42080, 42090, 42120, 42150, 42160, 42200],
        "Engagement_Rate": [6.0, 5.96, 4.46, 6.8, 6.0, 4.15, 6.84, 6.1, 3.67, 7.5],
    }
    return pd.DataFrame(data)


@pytest.fixture
def mapped_columns():
    """Standard column mapping for the sample data."""
    return {
        STD_DATE: "Date",
        "post": "Caption",
        STD_POST_TYPE: "Post_Type",
        STD_REACH: "Reach",
        STD_IMPRESSIONS: "Impressions",
        STD_LIKES: "Likes",
        STD_COMMENTS: "Comments",
        STD_SHARES: "Shares",
        STD_SAVES: "Saves",
        STD_FOLLOWERS: "Followers",
        STD_ENGAGEMENT_RATE: "Engagement_Rate",
    }


class TestCalculateKPIs:
    def test_total_reach(self, sample_df, mapped_columns):
        kpis = calculate_kpis(sample_df, mapped_columns)
        assert kpis["total_reach"]["available"] is True
        assert kpis["total_reach"]["value"] == 142000  # sum of all reach

    def test_total_impressions(self, sample_df, mapped_columns):
        kpis = calculate_kpis(sample_df, mapped_columns)
        assert kpis["total_impressions"]["available"] is True
        assert kpis["total_impressions"]["value"] == 212000

    def test_total_engagements(self, sample_df, mapped_columns):
        kpis = calculate_kpis(sample_df, mapped_columns)
        assert kpis["total_engagements"]["available"] is True
        # Sum: likes + comments + shares + saves
        expected = sum([800,600,200,1200,900,150,1500,500,100,2000]) + \
                   sum([50,40,10,80,60,8,100,30,5,120]) + \
                   sum([30,25,5,50,40,3,70,20,2,80]) + \
                   sum([20,50,8,30,80,5,40,60,3,50])
        assert kpis["total_engagements"]["value"] == expected

    def test_follower_growth(self, sample_df, mapped_columns):
        kpis = calculate_kpis(sample_df, mapped_columns)
        assert kpis["net_follower_growth"]["available"] is True
        assert kpis["net_follower_growth"]["value"] == 200  # 42200 - 42000

    def test_avg_engagement_rate(self, sample_df, mapped_columns):
        kpis = calculate_kpis(sample_df, mapped_columns)
        assert kpis["avg_engagement_rate"]["available"] is True
        expected = sample_df["Engagement_Rate"].mean()
        assert abs(kpis["avg_engagement_rate"]["value"] - expected) < 0.01

    def test_empty_dataframe(self, mapped_columns):
        empty = pd.DataFrame()
        kpis = calculate_kpis(empty, mapped_columns)
        assert kpis["total_reach"]["available"] is False

    def test_missing_columns(self, sample_df):
        minimal_map = {STD_DATE: "Date", STD_REACH: "Reach"}
        kpis = calculate_kpis(sample_df, minimal_map)
        assert kpis["total_reach"]["available"] is True
        assert kpis["total_saves"]["available"] is False


class TestDailyMetrics:
    def test_daily_aggregation(self, sample_df, mapped_columns):
        daily = calculate_daily_metrics(sample_df, mapped_columns)
        assert not daily.empty
        assert "Date" in daily.columns
        assert "Reach" in daily.columns

    def test_no_date_column(self, sample_df):
        daily = calculate_daily_metrics(sample_df, {})
        assert daily.empty


class TestFormatPerformance:
    def test_format_grouping(self, sample_df, mapped_columns):
        fmt = calculate_format_performance(sample_df, mapped_columns)
        assert not fmt.empty
        assert "post_count" in fmt.columns

    def test_no_type_column(self, sample_df):
        fmt = calculate_format_performance(sample_df, {STD_REACH: "Reach"})
        assert fmt.empty


class TestTopPosts:
    def test_top_posts_default(self, sample_df, mapped_columns):
        top = get_top_posts(sample_df, mapped_columns, sort_by="reach", n=3)
        assert len(top) == 3
        # First post should have highest reach
        reach_col = mapped_columns[STD_REACH]
        assert top.iloc[0][reach_col] == 30000

    def test_top_posts_by_engagement(self, sample_df, mapped_columns):
        top = get_top_posts(sample_df, mapped_columns, sort_by="engagements", n=3)
        assert len(top) == 3

    def test_filter_by_post_type(self, sample_df, mapped_columns):
        top = get_top_posts(sample_df, mapped_columns, post_type_filter="REELS", n=10)
        type_col = mapped_columns[STD_POST_TYPE]
        assert all(top[type_col] == "REELS")

    def test_search_filter(self, sample_df, mapped_columns):
        top = get_top_posts(sample_df, mapped_columns, search_query="AI", n=10)
        assert len(top) >= 1


class TestEngagementDistribution:
    def test_distribution(self, sample_df, mapped_columns):
        dist = get_engagement_distribution(sample_df, mapped_columns)
        assert "Likes" in dist
        assert "Comments" in dist
        assert dist["Likes"] > 0


class TestPostingFrequency:
    def test_frequency(self, sample_df, mapped_columns):
        freq = calculate_posting_frequency(sample_df, mapped_columns)
        assert freq["total_posts"] == 10
        assert freq["posts_per_day"] is not None


class TestPeakPerformance:
    def test_peak(self, sample_df, mapped_columns):
        peak = get_peak_performance(sample_df, mapped_columns)
        assert peak["peak_daily_reach"] is not None
        assert peak["avg_daily_reach"] is not None
