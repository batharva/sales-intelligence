"""
Page 1: Revenue Analysis
Interactive revenue analysis workspace with trends, growth, and breakdowns.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import COLORS
from utils.styling import render_section_header, render_empty_state
from utils.database import execute_query_df, is_database_ready
from utils.metrics import format_currency

st.markdown("<div style='margin-top:-2rem;'></div>", unsafe_allow_html=True)
render_section_header("Revenue Analysis")

from utils.data_loader import get_filtered_data
from utils.database import is_database_ready

db_ready = is_database_ready()
df = get_filtered_data()

if df.empty:
    render_empty_state("No data matches the current filter selections.")
    st.stop()

# ── Controls ──
col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns(4)
with col_ctrl1:
    agg = st.selectbox("Date Aggregation", ["Monthly", "Weekly", "Daily", "Quarterly"], key="rev_agg")
with col_ctrl2:
    compare = st.selectbox("Comparison", ["None", "Previous Period", "Year-over-Year"], key="rev_compare")
with col_ctrl3:
    cat_filter = st.selectbox("Category", ["All"] + sorted(df["category"].unique().tolist()), key="rev_cat")
with col_ctrl4:
    reg_filter = st.selectbox("Region", ["All"] + sorted(df["region"].unique().tolist()), key="rev_reg")

# Apply inline filters
plot_df = df.copy()
if cat_filter != "All":
    plot_df = plot_df[plot_df["category"] == cat_filter]
if reg_filter != "All":
    plot_df = plot_df[plot_df["region"] == reg_filter]

if plot_df.empty:
    render_empty_state()
    st.stop()

# ── Revenue Trend ──
st.markdown("<h3>Revenue Trend</h3>", unsafe_allow_html=True)

date_col = pd.to_datetime(plot_df["order_date"])
plot_df["date"] = date_col

if agg == "Daily":
    plot_df["period"] = plot_df["date"].dt.strftime("%Y-%m-%d")
elif agg == "Weekly":
    plot_df["period"] = plot_df["date"].dt.strftime("%Y-W%W")
elif agg == "Monthly":
    plot_df["period"] = plot_df["date"].dt.strftime("%Y-%m")
else:
    plot_df["period"] = plot_df["date"].dt.to_period("Q").astype(str)

trend = plot_df.groupby("period").agg(
    revenue=("sales", "sum"),
    orders=("order_id", "nunique"),
    units=("quantity", "sum"),
    avg_value=("sales", "mean"),
).reset_index()
trend = trend.sort_values("period")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=trend["period"], y=trend["revenue"],
    mode="lines+markers",
    name="Revenue",
    line=dict(color=COLORS["accent_primary"], width=2.5),
    marker=dict(size=4, color=COLORS["accent_primary"]),
    hovertemplate="%{x}<br>Revenue: $%{y:,.0f}<extra></extra>",
))

if compare == "Previous Period":
    # Simple simulated comparison using shifted data
    trend["prev_revenue"] = trend["revenue"].shift(len(trend) // 4)
    fig.add_trace(go.Scatter(
        x=trend["period"], y=trend["prev_revenue"],
        mode="lines",
        name="Previous Period",
        line=dict(color=COLORS["chart_grid"], width=1.5, dash="dot"),
        hovertemplate="%{x}<br>Prev: $%{y:,.0f}<extra></extra>",
    ))

fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=40),
    xaxis_title=None,
    yaxis_title="Revenue ($)",
    height=350,
    plot_bgcolor=COLORS["surface"],
    paper_bgcolor=COLORS["surface"],
    font=dict(family="Inter, sans-serif", size=11, color=COLORS["text_secondary"]),
    hovermode="x unified",
    legend=dict(orientation="h", y=1.1, font=dict(size=10)),
    xaxis=dict(gridcolor=COLORS["chart_grid"], linecolor=COLORS["border"]),
    yaxis=dict(gridcolor=COLORS["chart_grid"], linecolor=COLORS["border"]),
)
fig.update_xaxes(tickangle=-45)
st.plotly_chart(fig, use_container_width=True, key="rev_trend")

# ── Two-column secondary charts ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    st.markdown("<h3>Monthly Revenue Breakdown</h3>", unsafe_allow_html=True)

    monthly = trend.copy()
    if agg != "Monthly":
        plot_df_m = plot_df.copy()
        plot_df_m["month"] = plot_df_m["date"].dt.strftime("%Y-%m")
        monthly = plot_df_m.groupby("month").agg(
            revenue=("sales", "sum"),
            orders=("order_id", "nunique"),
        ).reset_index().sort_values("month")

    fig = px.bar(
        monthly, x="period" if agg == "Monthly" else "month",
        y="revenue",
    )
    fig.update_traces(
        marker_color=COLORS["accent_primary"],
        marker_line_width=0,
        hovertemplate="%{x}<br>$%{y:,.0f}<extra></extra>",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=40),
        xaxis_title=None,
        yaxis_title="Revenue ($)",
        height=280,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=10, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
    )
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True, key="rev_monthly")

with c2:
    st.markdown("<h3>Revenue Growth %</h3>", unsafe_allow_html=True)
    monthly["growth"] = monthly["revenue"].pct_change() * 100
    monthly = monthly.dropna()

    colors = [COLORS["positive"] if v >= 0 else COLORS["negative"] for v in monthly["growth"]]
    fig = px.bar(
        monthly,
        x="period" if agg == "Monthly" else "month",
        y="growth",
    )
    fig.update_traces(
        marker_color=colors,
        marker_line_width=0,
        hovertemplate="%{x}<br>Growth: %{y:+.1f}%<extra></extra>",
    )
    fig.add_hline(y=0, line_color=COLORS["border"], line_width=1)
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=40),
        xaxis_title=None,
        yaxis_title="Growth (%)",
        height=280,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=10, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        showlegend=False,
    )
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True, key="rev_growth")

# ── Bottom charts ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    st.markdown("<h3>Revenue by Category &amp; Subcategory</h3>", unsafe_allow_html=True)
    cat_sub = plot_df.groupby(["category", "subcategory"])["sales"].sum().reset_index()
    cat_sub = cat_sub.sort_values("sales", ascending=True)

    fig = px.bar(
        cat_sub, x="sales", y="subcategory", color="category",
        orientation="h",
        color_discrete_sequence=COLORS["chart_colors"],
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title="Revenue ($)",
        yaxis_title=None,
        height=350,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=10, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        legend=dict(orientation="h", y=1.05, font=dict(size=9)),
    )
    st.plotly_chart(fig, use_container_width=True, key="rev_cat_sub")

with c4:
    st.markdown("<h3>Revenue Contribution by Category</h3>", unsafe_allow_html=True)
    cat_contrib = plot_df.groupby("category")["sales"].sum().reset_index()
    total = cat_contrib["sales"].sum()
    cat_contrib["share"] = cat_contrib["sales"] / total * 100

    fig = go.Figure(data=[go.Pie(
        labels=cat_contrib["category"],
        values=cat_contrib["sales"],
        textinfo="label+percent",
        textposition="outside",
        marker=dict(colors=COLORS["chart_colors"][:len(cat_contrib)], line=dict(color=COLORS["surface"], width=2)),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
    )])
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        height=350,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=11, color=COLORS["text_secondary"]),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="rev_contrib")

# ── Additional trends ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
c5, c6 = st.columns(2)

with c5:
    st.markdown("<h3>Average Order Value Trend</h3>", unsafe_allow_html=True)
    aov_data = trend[["period", "avg_value"]].dropna()
    fig = px.line(
        aov_data, x="period", y="avg_value",
        markers=True,
    )
    fig.update_traces(
        line=dict(color=COLORS["accent_secondary"], width=2),
        marker=dict(size=4, color=COLORS["accent_secondary"]),
        hovertemplate="%{x}<br>AOV: $%{y:,.2f}<extra></extra>",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=40),
        xaxis_title=None,
        yaxis_title="AOV ($)",
        height=280,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=10, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        showlegend=False,
    )
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True, key="rev_aov")

with c6:
    st.markdown("<h3>Order Volume Trend</h3>", unsafe_allow_html=True)
    fig = px.bar(
        trend, x="period", y="orders",
    )
    fig.update_traces(
        marker_color=COLORS["chart_colors"][2],
        marker_line_width=0,
        hovertemplate="%{x}<br>Orders: %{y}<extra></extra>",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=40),
        xaxis_title=None,
        yaxis_title="Orders",
        height=280,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=10, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        showlegend=False,
    )
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True, key="rev_orders")