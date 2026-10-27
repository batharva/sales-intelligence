"""
Page 4: Regional Performance
Geographic revenue distribution and regional comparisons.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import COLORS
from utils.styling import render_section_header, render_empty_state
from utils.metrics import format_currency, format_number

st.markdown("<div style='margin-top:-2rem;'></div>", unsafe_allow_html=True)
render_section_header("Regional Performance")

from utils.data_loader import get_filtered_data
from utils.database import is_database_ready

db_ready = is_database_ready()
df = get_filtered_data()

if df.empty:
    render_empty_state()
    st.stop()

# ── Regional Summary ──
regional = df.groupby("region").agg(
    revenue=("sales", "sum"),
    orders=("order_id", "nunique"),
    units=("quantity", "sum"),
    customers=("customer_id", "nunique"),
    profit=("profit", "sum"),
).reset_index()

regional["avg_order_value"] = regional["revenue"] / regional["orders"]
regional["profit_margin"] = (regional["profit"] / regional["revenue"] * 100).round(2)
regional["revenue_share"] = (regional["revenue"] / regional["revenue"].sum() * 100).round(2)

# Company-wide averages
company_avg_aov = regional["revenue"].sum() / regional["orders"].sum() if regional["orders"].sum() > 0 else 0
company_avg_margin = regional["profit"].sum() / regional["revenue"].sum() * 100 if regional["revenue"].sum() > 0 else 0

regional = regional.sort_values("revenue", ascending=False)

# ── KPI Row ──
kpi_cols = st.columns(4)
with kpi_cols[0]:
    st.markdown(
        f'<div class="kpi-container">'
        f'<div class="kpi-label">Regions</div>'
        f'<div class="kpi-value">{len(regional)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
with kpi_cols[1]:
    st.markdown(
        f'<div class="kpi-container">'
        f'<div class="kpi-label">Top Region</div>'
        f'<div class="kpi-value">{regional.iloc[0]["region"]}</div>'
        f'<div class="kpi-delta positive">{format_currency(regional.iloc[0]["revenue"])}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
with kpi_cols[2]:
    st.markdown(
        f'<div class="kpi-container">'
        f'<div class="kpi-label">Company Avg AOV</div>'
        f'<div class="kpi-value">{format_currency(company_avg_aov)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
with kpi_cols[3]:
    st.markdown(
        f'<div class="kpi-container">'
        f'<div class="kpi-label">Company Avg Margin</div>'
        f'<div class="kpi-value">{company_avg_margin:.1f}%</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Charts ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    st.markdown("<h3>Revenue by Region</h3>", unsafe_allow_html=True)
    plot_data = regional.sort_values("revenue", ascending=True)
    fig = px.bar(
        plot_data, x="revenue", y="region",
        orientation="h",
        text=None,
    )
    fig.update_traces(
        marker_color=[COLORS["accent_primary"]] * len(plot_data),
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<br>Share: %{customdata[0]:.1f}%<extra></extra>",
        customdata=plot_data[["revenue_share"]],
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title="Revenue ($)",
        yaxis_title=None,
        height=300,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=11, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"], linecolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="reg_revenue")

with c2:
    st.markdown("<h3>Orders &amp; Customers by Region</h3>", unsafe_allow_html=True)
    plot_data = regional.sort_values("orders", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=plot_data["region"], x=plot_data["orders"],
        name="Orders",
        orientation="h",
        marker_color=COLORS["accent_primary"],
        hovertemplate="<b>%{y}</b><br>Orders: %{x}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=plot_data["region"], x=plot_data["customers"],
        name="Customers",
        orientation="h",
        marker_color=COLORS["accent_secondary"],
        hovertemplate="<b>%{y}</b><br>Customers: %{x}<extra></extra>",
    ))
    fig.update_layout(
        barmode="group",
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title=None,
        yaxis_title=None,
        height=300,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=11, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        legend=dict(orientation="h", y=1.1, font=dict(size=9)),
    )
    st.plotly_chart(fig, use_container_width=True, key="reg_orders")

# ── Comparison Charts ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    st.markdown("<h3>AOV vs Company Average</h3>", unsafe_allow_html=True)
    aov_compare = regional[["region", "avg_order_value"]].copy()
    aov_compare["company_avg"] = company_avg_aov
    aov_compare = aov_compare.sort_values("avg_order_value", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=aov_compare["region"], x=aov_compare["avg_order_value"],
        name="Region AOV",
        orientation="h",
        marker_color=COLORS["accent_primary"],
        hovertemplate="<b>%{y}</b><br>AOV: $%{x:,.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        y=aov_compare["region"],
        x=[company_avg_aov] * len(aov_compare),
        mode="lines",
        name="Company Avg",
        line=dict(color=COLORS["negative"], width=2, dash="dash"),
        hovertemplate="Company Avg: $%{x:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title="AOV ($)",
        yaxis_title=None,
        height=300,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=11, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        legend=dict(orientation="h", y=1.1, font=dict(size=9)),
    )
    st.plotly_chart(fig, use_container_width=True, key="reg_aov_compare")

with c4:
    st.markdown("<h3>Profit Margin vs Company Average</h3>", unsafe_allow_html=True)
    margin_compare = regional[["region", "profit_margin"]].copy()
    margin_compare = margin_compare.sort_values("profit_margin", ascending=True)

    colors = [COLORS["positive"] if m >= company_avg_margin else COLORS["negative"] for m in margin_compare["profit_margin"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=margin_compare["region"], x=margin_compare["profit_margin"],
        orientation="h",
        marker_color=colors,
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Margin: %{x:.1f}%<extra></extra>",
    ))
    fig.add_vline(x=company_avg_margin, line=dict(color=COLORS["border"], width=2, dash="dash"))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title="Profit Margin (%)",
        yaxis_title=None,
        height=300,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=11, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="reg_margin_compare")

# ── Regional Category Mix ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
st.markdown("<h3>Regional Category Mix</h3>", unsafe_allow_html=True)

region_cat = df.groupby(["region", "category"])["sales"].sum().reset_index()
region_cat["share"] = region_cat.groupby("region")["sales"].transform(lambda x: x / x.sum() * 100)

fig = px.bar(
    region_cat,
    x="region", y="sales",
    color="category",
    color_discrete_sequence=COLORS["chart_colors"],
)
fig.update_traces(
    marker_line_width=0,
    hovertemplate="<b>%{x}</b><br>%{legend}: $%{y:,.0f}<extra></extra>",
)
fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=30),
    xaxis_title=None,
    yaxis_title="Revenue ($)",
    height=300,
    plot_bgcolor=COLORS["surface"],
    paper_bgcolor=COLORS["surface"],
    font=dict(family="Inter, sans-serif", size=11, color=COLORS["text_secondary"]),
    xaxis=dict(gridcolor=COLORS["chart_grid"]),
    yaxis=dict(gridcolor=COLORS["chart_grid"]),
    legend=dict(orientation="h", y=1.1, font=dict(size=9)),
)
st.plotly_chart(fig, use_container_width=True, key="reg_cat_mix")

# ── Comparison Table ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
st.markdown("<h3>Regional Comparison Table</h3>", unsafe_allow_html=True)

comparison = regional[["region", "revenue", "orders", "customers", "avg_order_value", "profit", "profit_margin", "revenue_share"]].copy()
comparison["revenue"] = comparison["revenue"].apply(lambda x: f"${x:,.0f}")
comparison["profit"] = comparison["profit"].apply(lambda x: f"${x:,.0f}")
comparison["avg_order_value"] = comparison["avg_order_value"].apply(lambda x: f"${x:,.2f}")
comparison["profit_margin"] = comparison["profit_margin"].apply(lambda x: f"{x:.1f}%")
comparison["revenue_share"] = comparison["revenue_share"].apply(lambda x: f"{x:.1f}%")

comparison.columns = ["Region", "Revenue", "Orders", "Customers", "AOV", "Profit", "Margin", "Rev Share"]

st.dataframe(comparison, use_container_width=True, hide_index=True)
csv = comparison.to_csv(index=False)
st.download_button(
    label="Download Regional Data (CSV)",
    data=csv,
    file_name="regional_performance.csv",
    mime="text/csv",
)