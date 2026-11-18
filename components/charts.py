"""
SocialPulse AI - Chart Components
Interactive Plotly charts for performance visualization.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.constants import (
    PRIMARY, PRIMARY_LIGHT, SECONDARY, SUCCESS, DANGER,
    CHART_COLORS, TEXT_PRIMARY, TEXT_MUTED, BACKGROUND
)


def _base_layout():
    """Return base layout dict for consistent chart styling."""
    return dict(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT_PRIMARY, size=12),
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=11)),
        hovermode="x unified",
        xaxis=dict(showgrid=False, showline=True, linecolor="#E8E8F0"),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F5", showline=False),
    )


def render_performance_trend(trend_df: pd.DataFrame, view: str = "Daily"):
    """Line/area chart for Reach, Impressions, Engagements."""
    if trend_df is None or trend_df.empty:
        st.info("No trend data available.")
        return

    fig = go.Figure()
    date_col = "Date"

    colors = {"Reach": PRIMARY, "Impressions": SECONDARY, "Engagements": SUCCESS}

    for col_name in ["Reach", "Impressions", "Engagements"]:
        if col_name not in trend_df.columns:
            continue
        y_data = trend_df[col_name].cumsum() if view == "Cumulative" else trend_df[col_name]

        fig.add_trace(go.Scatter(
            x=trend_df[date_col], y=y_data,
            name=col_name, mode="lines",
            line=dict(color=colors.get(col_name, PRIMARY), width=2.5),
            fill="tozeroy" if col_name == "Reach" else None,
            fillcolor=f"rgba(70,72,212,0.08)" if col_name == "Reach" else None,
            hovertemplate=f"<b>{col_name}</b>: %{{y:,.0f}}<extra></extra>",
        ))

    layout = _base_layout()
    layout["height"] = 320
    layout["yaxis"]["title"] = None
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_engagement_donut(distribution: dict):
    """Donut chart of engagement type distribution."""
    if not distribution:
        st.info("No engagement data available.")
        return

    labels = list(distribution.keys())
    values = list(distribution.values())
    colors_list = [PRIMARY, SECONDARY, SUCCESS, "#F59E0B"][:len(labels)]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values,
        hole=0.55, marker=dict(colors=colors_list),
        textinfo="label+percent", textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>Count: %{value:,.0f}<br>Share: %{percent}<extra></extra>",
    )])
    layout = _base_layout()
    layout["height"] = 300
    layout["showlegend"] = False
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_format_bar_chart(format_df: pd.DataFrame, metric_col: str = "eng_rate_by_reach"):
    """Horizontal bar chart of format performance."""
    if format_df is None or format_df.empty or metric_col not in format_df.columns:
        st.info("No format performance data.")
        return

    fig = go.Figure(go.Bar(
        y=format_df.index.tolist(),
        x=format_df[metric_col].tolist(),
        orientation="h",
        marker_color=PRIMARY,
        text=[f"{v:.2f}%" for v in format_df[metric_col]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Eng Rate: %{x:.2f}%<extra></extra>",
    ))
    layout = _base_layout()
    layout["height"] = max(200, len(format_df) * 50)
    layout["yaxis"]["autorange"] = "reversed"
    layout["xaxis"]["title"] = "Engagement Rate (%)"
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_follower_growth_chart(df: pd.DataFrame, mapped_columns: dict):
    """Line chart of follower growth over time."""
    from utils.constants import STD_DATE, STD_FOLLOWERS
    date_col = mapped_columns.get(STD_DATE)
    fol_col = mapped_columns.get(STD_FOLLOWERS)
    if not date_col or not fol_col or date_col not in df.columns or fol_col not in df.columns:
        st.info("Follower data not available.")
        return

    fol_df = df[[date_col, fol_col]].dropna().sort_values(date_col)
    if fol_df.empty:
        st.info("No follower data points.")
        return

    fig = go.Figure(go.Scatter(
        x=fol_df[date_col], y=fol_df[fol_col],
        mode="lines+markers", line=dict(color=SUCCESS, width=2.5),
        marker=dict(size=5, color=SUCCESS),
        fill="tozeroy", fillcolor="rgba(0,136,93,0.08)",
        hovertemplate="<b>%{x|%b %d}</b><br>Followers: %{y:,.0f}<extra></extra>",
    ))
    layout = _base_layout()
    layout["height"] = 280
    layout["yaxis"]["title"] = "Followers"
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_comparison_chart(comparison: dict):
    """Grouped bar chart current vs previous period."""
    metrics = []
    current_vals = []
    previous_vals = []

    label_map = {
        "total_reach": "Reach", "total_impressions": "Impressions",
        "total_engagements": "Engagements", "total_likes": "Likes",
        "total_comments": "Comments", "total_shares": "Shares",
    }

    for key, label in label_map.items():
        data = comparison.get(key, {})
        if isinstance(data, dict) and data.get("available"):
            metrics.append(label)
            current_vals.append(data.get("current_value", 0))
            previous_vals.append(data.get("previous_value", 0))

    if not metrics:
        st.info("No comparable metrics available.")
        return

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Previous", x=metrics, y=previous_vals,
                         marker_color="#C4C4E8", text=[f"{v:,.0f}" for v in previous_vals],
                         textposition="outside"))
    fig.add_trace(go.Bar(name="Current", x=metrics, y=current_vals,
                         marker_color=PRIMARY, text=[f"{v:,.0f}" for v in current_vals],
                         textposition="outside"))
    layout = _base_layout()
    layout["barmode"] = "group"
    layout["height"] = 350
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_metric_over_time(df, mapped_columns, metric_std, label, color=PRIMARY):
    """Generic line chart for a single metric over time."""
    from utils.constants import STD_DATE
    date_col = mapped_columns.get(STD_DATE)
    metric_col = mapped_columns.get(metric_std)
    if not date_col or not metric_col or date_col not in df.columns or metric_col not in df.columns:
        return

    daily = df.groupby(pd.to_datetime(df[date_col]).dt.date)[metric_col].sum().reset_index()
    daily.columns = ["Date", label]

    fig = go.Figure(go.Scatter(
        x=daily["Date"], y=daily[label], mode="lines",
        line=dict(color=color, width=2.5),
        fill="tozeroy", fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.08)",
        hovertemplate=f"<b>%{{x|%b %d}}</b><br>{label}: %{{y:,.0f}}<extra></extra>",
    ))
    layout = _base_layout()
    layout["height"] = 250
    layout["yaxis"]["title"] = label
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
