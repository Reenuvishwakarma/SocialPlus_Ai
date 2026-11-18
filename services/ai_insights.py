"""
SocialPulse AI - AI Insights Service
Generates AI-powered performance analysis using Groq or OpenAI.
Falls back to rule-based insights when API keys are unavailable.
"""
import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


def _get_ai_client():
    """Get the appropriate AI client based on configuration."""
    provider = os.getenv("AI_PROVIDER", "groq").lower()
    
    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "")
        if api_key and api_key != "your_groq_api_key_here":
            try:
                from groq import Groq
                return Groq(api_key=api_key), "groq", os.getenv("AI_MODEL", "llama-3.1-70b-versatile")
            except ImportError:
                pass
    
    if provider == "openai" or provider != "groq":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key and api_key != "your_openai_api_key_here":
            try:
                from openai import OpenAI
                return OpenAI(api_key=api_key), "openai", os.getenv("AI_MODEL", "gpt-4o-mini")
            except ImportError:
                pass
    
    return None, None, None


def _build_metrics_summary(kpis: dict, comparison: dict, format_perf: dict, 
                           posting_freq: dict, peak_perf: dict) -> str:
    """Build a concise metrics summary string to send to the AI."""
    lines = ["=== SOCIAL MEDIA PERFORMANCE DATA SUMMARY ===\n"]
    
    # KPIs
    lines.append("KEY PERFORMANCE INDICATORS:")
    for key, data in kpis.items():
        if data.get("available"):
            lines.append(f"  - {key}: {data['value']}")
    
    # Comparison data
    if comparison:
        lines.append("\nPERIOD COMPARISON:")
        for key, data in comparison.items():
            if isinstance(data, dict) and data.get("available"):
                curr = data.get("current_value", "N/A")
                prev = data.get("previous_value", "N/A")
                pct = data.get("percentage_change")
                direction = data.get("direction", "neutral")
                pct_str = f"{pct:+.1f}%" if pct is not None else "N/A"
                lines.append(f"  - {key}: Current={curr}, Previous={prev}, Change={pct_str} ({direction})")
    
    # Format performance
    if format_perf is not None and not (hasattr(format_perf, 'empty') and format_perf.empty):
        lines.append("\nCONTENT FORMAT PERFORMANCE:")
        if hasattr(format_perf, 'iterrows'):
            for idx, row in format_perf.iterrows():
                count = row.get("post_count", "?")
                er = row.get("eng_rate_by_reach", "N/A")
                lines.append(f"  - {idx}: {count} posts, Eng Rate: {er}%")
    
    # Posting frequency
    if posting_freq:
        lines.append("\nPOSTING FREQUENCY:")
        lines.append(f"  - Posts per week: {posting_freq.get('posts_per_week', 'N/A')}")
        lines.append(f"  - Total posts: {posting_freq.get('total_posts', 'N/A')}")
    
    # Peak performance  
    if peak_perf:
        lines.append("\nPEAK PERFORMANCE:")
        if peak_perf.get("peak_daily_reach"):
            lines.append(f"  - Peak daily reach: {peak_perf['peak_daily_reach']}")
            lines.append(f"  - Peak date: {peak_perf.get('peak_daily_reach_date', 'N/A')}")
        if peak_perf.get("avg_daily_reach"):
            lines.append(f"  - Average daily reach: {peak_perf['avg_daily_reach']}")
    
    return "\n".join(lines)


def generate_ai_insights(kpis: dict, comparison: dict = None, format_perf=None,
                         posting_freq: dict = None, peak_perf: dict = None,
                         platform: str = "Instagram") -> dict:
    """
    Generate AI-powered insights. Falls back to rule-based insights if API unavailable.
    
    Returns dict with:
    - source: "ai" or "rule_based"
    - executive_summary: overall performance summary
    - primary_takeaway: single most important insight
    - recommendations: list of actionable recommendations
    - strengths: list of strengths
    - weaknesses: list of weaknesses  
    - content_strategy: content strategy insights
    - engagement_strategy: engagement strategy insights
    - reach_optimization: reach optimization insights
    - posting_consistency: posting consistency insights
    """
    client, provider, model = _get_ai_client()
    
    metrics_summary = _build_metrics_summary(
        kpis, comparison or {}, format_perf, posting_freq or {}, peak_perf or {}
    )
    
    if client is not None:
        return _generate_with_ai(client, provider, model, metrics_summary, platform)
    else:
        return _generate_rule_based(kpis, comparison, format_perf, posting_freq, peak_perf, platform)


def _generate_with_ai(client, provider: str, model: str, metrics_summary: str, platform: str) -> dict:
    """Generate insights using AI API."""
    system_prompt = """You are an expert social media analytics consultant. Analyze the provided performance data and generate actionable insights. 

IMPORTANT RULES:
1. Only make claims supported by the provided data
2. Be specific - reference actual numbers from the data
3. Provide practical, actionable recommendations
4. If data is insufficient for a conclusion, say so
5. Do not invent or assume data not provided

Respond in this exact JSON format:
{
    "executive_summary": "2-3 sentence overview of overall performance",
    "primary_takeaway": "Single most important insight from the data",
    "recommendations": [
        {"title": "recommendation title", "description": "detailed actionable recommendation", "priority": "high/medium/low"},
        ...
    ],
    "strengths": [
        {"title": "strength title", "description": "what is working well and evidence"},
        ...
    ],
    "weaknesses": [
        {"title": "weakness title", "description": "what needs improvement and evidence"},
        ...
    ],
    "content_strategy": "Insights about content strategy based on format performance",
    "engagement_strategy": "Insights about engagement patterns and how to improve",
    "reach_optimization": "Insights about reach patterns and optimization",
    "posting_consistency": "Insights about posting frequency and consistency"
}"""

    user_prompt = f"""Analyze this {platform} performance data and provide insights:

{metrics_summary}

Provide your analysis in the specified JSON format. Focus on data-grounded, actionable insights."""

    try:
        if provider == "groq":
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
        else:  # openai
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
        
        content = response.choices[0].message.content
        insights = json.loads(content)
        insights["source"] = "ai"
        insights["model"] = model
        insights["provider"] = provider
        return insights
    
    except Exception as e:
        # Fall back to rule-based on error
        fallback = _generate_rule_based_from_summary(metrics_summary, platform)
        fallback["ai_error"] = str(e)
        return fallback


def _generate_rule_based(kpis: dict, comparison: dict = None, format_perf=None,
                         posting_freq: dict = None, peak_perf: dict = None,
                         platform: str = "Instagram") -> dict:
    """Generate rule-based insights when AI API is unavailable."""
    insights = {
        "source": "rule_based",
        "note": "These insights are generated using rule-based analysis, not an AI model. Configure an API key in .env for AI-powered insights.",
        "executive_summary": "",
        "primary_takeaway": "",
        "recommendations": [],
        "strengths": [],
        "weaknesses": [],
        "content_strategy": "",
        "engagement_strategy": "",
        "reach_optimization": "",
        "posting_consistency": "",
    }
    
    # Build executive summary from KPIs
    summary_parts = []
    total_reach = kpis.get("total_reach", {}).get("value")
    total_eng = kpis.get("total_engagements", {}).get("value")
    avg_er = kpis.get("avg_engagement_rate", {}).get("value")
    total_posts = kpis.get("total_posts", {}).get("value", 0)
    follower_growth = kpis.get("net_follower_growth", {}).get("value")
    
    if total_reach:
        summary_parts.append(f"The account achieved a total reach of {total_reach:,.0f} across {total_posts} posts.")
    if avg_er is not None:
        if avg_er > 5:
            summary_parts.append(f"The average engagement rate of {avg_er:.2f}% is above the typical {platform} benchmark.")
        elif avg_er > 2:
            summary_parts.append(f"The average engagement rate of {avg_er:.2f}% is within the standard {platform} range.")
        else:
            summary_parts.append(f"The average engagement rate of {avg_er:.2f}% is below the typical {platform} benchmark, suggesting room for improvement.")
    if follower_growth is not None:
        if follower_growth > 0:
            summary_parts.append(f"Net follower growth of +{follower_growth:,.0f} indicates positive audience expansion.")
        elif follower_growth < 0:
            summary_parts.append(f"Net follower change of {follower_growth:,.0f} suggests audience retention challenges.")
    
    insights["executive_summary"] = " ".join(summary_parts) if summary_parts else "Upload data to generate performance insights."
    
    # Primary takeaway
    if format_perf is not None and hasattr(format_perf, 'empty') and not format_perf.empty:
        if "eng_rate_by_reach" in format_perf.columns:
            best_format = format_perf["eng_rate_by_reach"].idxmax()
            best_er = format_perf.loc[best_format, "eng_rate_by_reach"]
            insights["primary_takeaway"] = (
                f"{best_format} posts generated the highest average engagement rate ({best_er}%) "
                f"during the reporting period, suggesting this format resonates most with your audience."
            )
        elif "post_count" in format_perf.columns:
            top_format = format_perf["post_count"].idxmax()
            insights["primary_takeaway"] = f"{top_format} is the most frequently posted format."
    elif avg_er is not None:
        insights["primary_takeaway"] = f"Your average engagement rate is {avg_er:.2f}%."
    else:
        insights["primary_takeaway"] = "Upload more data with engagement metrics for deeper analysis."
    
    # Recommendations
    recs = []
    if avg_er is not None and avg_er < 3:
        recs.append({
            "title": "Improve Content Engagement",
            "description": f"Your engagement rate ({avg_er:.2f}%) is below the industry average. Consider creating more interactive content such as polls, questions, or carousel posts that encourage interaction.",
            "priority": "high"
        })
    
    if posting_freq and posting_freq.get("posts_per_week"):
        ppw = posting_freq["posts_per_week"]
        if ppw < 3:
            recs.append({
                "title": "Increase Posting Frequency",
                "description": f"At {ppw:.1f} posts per week, consider increasing to 4-5 posts per week for better algorithmic visibility and audience engagement.",
                "priority": "medium"
            })
        elif ppw > 14:
            recs.append({
                "title": "Optimize Posting Frequency",
                "description": f"At {ppw:.1f} posts per week, you may be over-posting. Consider reducing to focus on higher-quality content.",
                "priority": "medium"
            })
    
    if format_perf is not None and hasattr(format_perf, 'empty') and not format_perf.empty:
        if "eng_rate_by_reach" in format_perf.columns and len(format_perf) > 1:
            best = format_perf["eng_rate_by_reach"].idxmax()
            worst = format_perf["eng_rate_by_reach"].idxmin()
            if best != worst:
                recs.append({
                    "title": f"Increase {best} Content",
                    "description": f"{best} posts show the highest engagement rate. Consider shifting more content production toward this format.",
                    "priority": "high"
                })
    
    if comparison:
        declining = []
        for metric in ["total_reach", "total_impressions", "total_engagements"]:
            data = comparison.get(metric, {})
            if isinstance(data, dict) and data.get("direction") == "down":
                declining.append(metric.replace("total_", "").title())
        if declining:
            recs.append({
                "title": "Address Declining Metrics",
                "description": f"{', '.join(declining)} showed decline compared to the previous period. Review recent content changes and consider A/B testing new approaches.",
                "priority": "high"
            })
    
    if not recs:
        recs.append({
            "title": "Continue Current Strategy",
            "description": "Your current metrics are within normal range. Continue monitoring and experimenting with content formats to optimize performance.",
            "priority": "medium"
        })
    
    insights["recommendations"] = recs
    
    # Strengths
    strengths = []
    if avg_er is not None and avg_er > 3:
        strengths.append({
            "title": "Strong Engagement Rate",
            "description": f"Your engagement rate of {avg_er:.2f}% exceeds the typical benchmark, indicating good audience connection."
        })
    if follower_growth is not None and follower_growth > 0:
        strengths.append({
            "title": "Positive Audience Growth",
            "description": f"Net follower growth of +{follower_growth:,.0f} demonstrates expanding reach and audience interest."
        })
    if comparison:
        improving = [m.replace("total_", "").title() for m, d in comparison.items()
                    if isinstance(d, dict) and d.get("direction") == "up"]
        if improving:
            strengths.append({
                "title": "Improving Metrics",
                "description": f"{', '.join(improving[:3])} improved compared to the previous period."
            })
    
    insights["strengths"] = strengths if strengths else [{"title": "Data Being Analyzed", "description": "More data points will reveal strengths over time."}]
    
    # Weaknesses
    weaknesses = []
    if avg_er is not None and avg_er < 2:
        weaknesses.append({
            "title": "Low Engagement Rate",
            "description": f"An engagement rate of {avg_er:.2f}% is below industry averages, suggesting content may not be resonating with the target audience."
        })
    if follower_growth is not None and follower_growth < 0:
        weaknesses.append({
            "title": "Declining Audience",
            "description": f"A net follower change of {follower_growth:,.0f} indicates audience retention issues."
        })
    
    insights["weaknesses"] = weaknesses if weaknesses else [{"title": "No Major Weaknesses Detected", "description": "Current metrics are within acceptable ranges."}]
    
    # Strategy insights
    if format_perf is not None and hasattr(format_perf, 'empty') and not format_perf.empty:
        insights["content_strategy"] = f"Your content mix includes {len(format_perf)} formats. Analyze which formats drive the highest engagement rate and reach to optimize your content calendar."
    else:
        insights["content_strategy"] = "Add post type data to your dataset for content format analysis."
    
    insights["engagement_strategy"] = f"Focus on creating content that drives meaningful interactions. Your total engagements of {total_eng:,.0f} could be improved by incorporating calls-to-action and interactive elements." if total_eng else "Upload engagement data for strategy recommendations."
    
    insights["reach_optimization"] = f"Your total reach of {total_reach:,.0f} across {total_posts} posts suggests an average reach of {total_reach/max(total_posts,1):,.0f} per post. Experiment with posting times and hashtag strategies to improve discoverability." if total_reach else "Upload reach data for optimization insights."
    
    if posting_freq and posting_freq.get("posts_per_week"):
        insights["posting_consistency"] = f"You are posting approximately {posting_freq['posts_per_week']:.1f} times per week over {posting_freq.get('total_days', 'N/A')} days. Consistency is key for algorithmic favor."
    else:
        insights["posting_consistency"] = "Add date information to analyze posting consistency."
    
    return insights


def _generate_rule_based_from_summary(metrics_summary: str, platform: str) -> dict:
    """Fallback rule-based generation from metrics summary string."""
    return {
        "source": "rule_based",
        "note": "AI API call failed. These are rule-based insights.",
        "executive_summary": "Analysis could not be completed with AI. Please check your API key configuration.",
        "primary_takeaway": "Configure a valid API key for AI-powered insights.",
        "recommendations": [{
            "title": "Configure AI Integration",
            "description": "Add your Groq or OpenAI API key to the .env file for AI-powered performance analysis.",
            "priority": "high"
        }],
        "strengths": [],
        "weaknesses": [],
        "content_strategy": "AI analysis unavailable.",
        "engagement_strategy": "AI analysis unavailable.",
        "reach_optimization": "AI analysis unavailable.",
        "posting_consistency": "AI analysis unavailable.",
    }


def is_ai_configured() -> bool:
    """Check if AI API is properly configured."""
    client, _, _ = _get_ai_client()
    return client is not None
