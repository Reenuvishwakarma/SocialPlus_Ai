"""Integration test for SocialPulse AI pipeline."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from services.csv_loader import load_csv_from_path
from services.column_mapper import auto_map_columns
from services.data_validator import validate_dataset
from services.data_cleaner import clean_dataset, calculate_missing_engagement_rate
from services.analytics_engine import calculate_kpis, calculate_format_performance, get_top_posts
from services.comparison_engine import compare_periods
from services.ai_insights import generate_ai_insights
from services.pdf_generator import generate_pdf_report
from utils.helpers import get_date_range

# Load Instagram sample
df, err = load_csv_from_path("data/sample_instagram_data.csv")
print(f"Loaded: {len(df)} rows, error={err}")

# Map columns
mapped, unmapped = auto_map_columns(df)
print(f"Mapped: {len(mapped)} columns: {list(mapped.keys())}")

# Validate
val = validate_dataset(df, mapped)
print(f"Valid: {val['is_valid']}, Health: {val['health_score']:.0f}%")

# Clean
cleaned = clean_dataset(df, mapped)
cleaned = calculate_missing_engagement_rate(cleaned, mapped)
print(f"Cleaned: {len(cleaned)} rows")

# KPIs
kpis = calculate_kpis(cleaned, mapped)
print(f"Total Reach: {kpis['total_reach']['value']:,.0f}")
print(f"Total Engagements: {kpis['total_engagements']['value']:,.0f}")
print(f"Avg ER: {kpis['avg_engagement_rate']['value']:.2f}%")
print(f"Follower Growth: {kpis['net_follower_growth']['value']:+,.0f}")

# Format performance
fmt = calculate_format_performance(cleaned, mapped)
print(f"Format types: {list(fmt.index)}")

# Top posts
top = get_top_posts(cleaned, mapped, sort_by="reach", n=3)
print(f"Top 3 posts by reach: {list(top[mapped['reach']].values)}")

# Period comparison
comp = compare_periods(cleaned, mapped)
reach_comp = comp.get("total_reach", {})
pct = reach_comp.get("percentage_change", 0)
print(f"Reach comparison: {reach_comp.get('direction')} ({pct:.1f}%)")

# AI insights (rule-based, since no API key)
insights = generate_ai_insights(kpis, comp, fmt, {}, {}, "Instagram")
print(f"Insights source: {insights['source']}")
takeaway = insights.get("primary_takeaway", "")[:80]
print(f"Primary takeaway: {takeaway}...")

# PDF generation
dr = get_date_range(cleaned, mapped.get("date", ""))
pdf_bytes = generate_pdf_report(kpis, comp, fmt, top, insights, mapped, "Instagram", dr)
print(f"PDF generated: {len(pdf_bytes):,} bytes")

# LinkedIn test
df2, err2 = load_csv_from_path("data/sample_linkedin_data.csv")
mapped2, _ = auto_map_columns(df2)
val2 = validate_dataset(df2, mapped2)
print(f"\nLinkedIn - Loaded: {len(df2)} rows, Mapped: {len(mapped2)} columns, Health: {val2['health_score']:.0f}%")

print("\n=== ALL INTEGRATION TESTS PASSED ===")
