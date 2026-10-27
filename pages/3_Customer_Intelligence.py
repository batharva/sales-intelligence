"""
Page 3: Customer Intelligence
Customer segmentation, RFM analysis, and purchase behavior.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import COLORS
from utils.styling import render_section_header, render_empty_state
from utils.database import execute_query_df
from utils.metrics import format_currency, format_number

st.markdown("<div style='margin-top:-2rem;'></div>", unsafe_allow_html=True)
render_section_header("Customer Intelligence")

from utils.data_loader import get_filtered_data
from utils.database import is_database_ready

db_ready = is_database_ready()
df = get_filtered_data()

if df.empty:
    render_empty_state()
    st.stop()

# ── Customer KPIs ──
unique_customers = df["customer_id"].nunique()
total_revenue = df["sales"].sum()
avg_revenue_per_customer = total_revenue / unique_customers if unique_customers > 0 else 0

# Repeat purchase rate
customer_orders = df.groupby("customer_id")["order_id"].nunique()
repeat_customers = (customer_orders > 1).sum()
repeat_rate = (repeat_customers / len(customer_orders) * 100) if len(customer_orders) > 0 else 0

kpi_cols = st.columns(4)
with kpi_cols[0]:
    st.markdown(
        f'<div class="kpi-container">'
        f'<div class="kpi-label">Unique Customers</div>'
        f'<div class="kpi-value">{format_number(unique_customers)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
with kpi_cols[1]:
    st.markdown(
        f'<div class="kpi-container">'
        f'<div class="kpi-label">Avg Revenue Per Customer</div>'
        f'<div class="kpi-value">{format_currency(avg_revenue_per_customer)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
with kpi_cols[2]:
    st.markdown(
        f'<div class="kpi-container">'
        f'<div class="kpi-label">Repeat Purchase Rate</div>'
        f'<div class="kpi-value">{repeat_rate:.1f}%</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
with kpi_cols[3]:
    st.markdown(
        f'<div class="kpi-container">'
        f'<div class="kpi-label">Avg Orders per Customer</div>'
        f'<div class="kpi-value">{customer_orders.mean():.2f}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Charts ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    st.markdown("<h3>Avg Order Value by Segment</h3>", unsafe_allow_html=True)
    segment_aov = df.groupby("segment").agg(
        avg_order_value=("sales", "mean"),
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique"),
    ).reset_index().sort_values("avg_order_value", ascending=True)

    fig = px.bar(
        segment_aov, x="avg_order_value", y="segment",
        orientation="h",
        text=None,
    )
    fig.update_traces(
        marker_color=COLORS["accent_primary"],
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>AOV: $%{x:,.2f}<br>Orders: %{customdata[0]}<extra></extra>",
        customdata=segment_aov[["orders"]],
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title="Average Order Value ($)",
        yaxis_title=None,
        height=280,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=10, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="cust_segment_aov")

with c2:
    st.markdown("<h3>One-Time vs Repeat Customers</h3>", unsafe_allow_html=True)
    customer_orders_df = pd.DataFrame({
        "type": ["One-Time", "Repeat"],
        "count": [
            (customer_orders == 1).sum(),
            (customer_orders > 1).sum(),
        ],
    })

    fig = px.pie(
        customer_orders_df, values="count", names="type",
        color_discrete_sequence=[COLORS["accent_secondary"], COLORS["accent_primary"]],
    )
    fig.update_traces(
        textinfo="label+percent",
        textposition="outside",
        marker=dict(line=dict(color=COLORS["surface"], width=2)),
        hovertemplate="<b>%{label}</b><br>%{value} customers (%{percent})<extra></extra>",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        height=280,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=11, color=COLORS["text_secondary"]),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="cust_repeat")

# ── RFM Segmentation ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
st.markdown("<h3>RFM Customer Segmentation</h3>", unsafe_allow_html=True)
st.markdown(
    '<p style="font-size:0.75rem;color:#6B706D;">'
    "RFM scores calculated using: Recency (days since last purchase), "
    "Frequency (distinct orders), Monetary (total spend). "
    "Scored via quartile ranking (1=lowest, 4=highest)."
    "</p>",
    unsafe_allow_html=True,
)

# Calculate RFM from filtered data
date_max = pd.to_datetime(df["order_date"]).max()
cutoff_date = date_max + pd.Timedelta(days=1)
rfm = df.groupby("customer_id").agg(
    recency=("order_date", lambda x: (cutoff_date - pd.to_datetime(x).max()).days),
    frequency=("order_id", "nunique"),
    monetary=("sales", "sum"),
).reset_index()

# Quartile scores
rfm["R_Score"] = pd.qcut(rfm["recency"], 4, labels=[4, 3, 2, 1], duplicates="drop").astype(int)
rfm["F_Score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4], duplicates="drop").astype(int)
rfm["M_Score"] = pd.qcut(rfm["monetary"].rank(method="first"), 4, labels=[1, 2, 3, 4], duplicates="drop").astype(int)

# Segment assignment
def assign_rfm_segment(row):
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
    if r >= 3 and f >= 3 and m >= 3:
        return "Champions"
    elif r >= 3 and f >= 1 and m >= 1:
        return "Loyal Customers"
    elif r >= 3 and f <= 2 and m <= 2:
        return "New Customers"
    elif r <= 2 and f >= 3 and m >= 3:
        return "At Risk"
    elif r <= 2 and f <= 2 and m >= 2:
        return "Needs Attention"
    elif r <= 2 and f <= 2 and m <= 2:
        return "Lost"
    else:
        return "Other"

rfm["Segment"] = rfm.apply(assign_rfm_segment, axis=1)

# Segment summary
seg_summary = rfm.groupby("Segment").agg(
    count=("customer_id", "count"),
    avg_recency=("recency", "mean"),
    avg_frequency=("frequency", "mean"),
    avg_monetary=("monetary", "mean"),
).reset_index().sort_values("avg_monetary", ascending=False)

c3, c4 = st.columns([1, 1])

with c3:
    fig = px.bar(
        seg_summary.sort_values("count", ascending=True),
        x="count", y="Segment",
        orientation="h",
        color="Segment",
        color_discrete_sequence=COLORS["chart_colors"] + ["#8B6F5E"],
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Customers: %{x}<extra></extra>",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title="Customers",
        yaxis_title=None,
        height=300,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=10, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="cust_rfm_dist")

with c4:
    st.markdown("<h4>RFM Segment Summary</h4>", unsafe_allow_html=True)
    display_seg = seg_summary.copy()
    display_seg["avg_monetary"] = display_seg["avg_monetary"].apply(lambda x: f"${x:,.0f}")
    display_seg["avg_recency"] = display_seg["avg_recency"].apply(lambda x: f"{x:.0f}d")
    display_seg["avg_frequency"] = display_seg["avg_frequency"].apply(lambda x: f"{x:.1f}")
    display_seg.columns = ["Segment", "Customers", "Avg Recency", "Avg Freq", "Avg Spend"]
    st.dataframe(display_seg, use_container_width=True, hide_index=True)

# ── Purchase Frequency Distribution ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
c5, c6 = st.columns(2)

with c5:
    st.markdown("<h3>Purchase Frequency Distribution</h3>", unsafe_allow_html=True)
    freq_dist = customer_orders.value_counts().reset_index()
    freq_dist.columns = ["Orders", "Customers"]
    freq_dist = freq_dist.sort_values("Orders")

    fig = px.bar(
        freq_dist[freq_dist["Orders"] <= 20],
        x="Orders", y="Customers",
    )
    fig.update_traces(
        marker_color=COLORS["accent_primary"],
        marker_line_width=0,
        hovertemplate="%{x} orders: %{y} customers<extra></extra>",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title="Number of Orders",
        yaxis_title="Customers",
        height=280,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=10, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"], dtick=1),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="cust_freq_dist")

with c6:
    st.markdown("<h3>Top 10 Customers by Revenue</h3>", unsafe_allow_html=True)
    top_cust = df.groupby(["customer_id", "customer_name", "segment", "region"]).agg(
        total_revenue=("sales", "sum"),
        order_count=("order_id", "nunique"),
        avg_value=("sales", "mean"),
    ).reset_index().sort_values("total_revenue", ascending=False).head(10)

    fig = px.bar(
        top_cust.iloc[::-1],
        x="total_revenue", y="customer_name",
        orientation="h",
        color="segment",
        color_discrete_sequence=COLORS["chart_colors"],
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<br>Orders: %{customdata[0]}<extra></extra>",
        customdata=top_cust[["order_count"]],
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title="Revenue ($)",
        yaxis_title=None,
        height=280,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=10, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        legend=dict(orientation="h", y=1.05, font=dict(size=9)),
    )
    st.plotly_chart(fig, use_container_width=True, key="cust_top10")

# ── Full Customer Table ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
st.markdown("<h3>Customer Data</h3>", unsafe_allow_html=True)

customer_table = df.groupby(["customer_id", "customer_name", "segment", "region"]).agg(
    orders=("order_id", "nunique"),
    total_sales=("sales", "sum"),
    avg_order_value=("sales", "mean"),
    total_profit=("profit", "sum"),
).reset_index().sort_values("total_sales", ascending=False)

customer_table["total_sales"] = customer_table["total_sales"].apply(lambda x: f"${x:,.2f}")
customer_table["avg_order_value"] = customer_table["avg_order_value"].apply(lambda x: f"${x:,.2f}")
customer_table["total_profit"] = customer_table["total_profit"].apply(lambda x: f"${x:,.2f}")

st.dataframe(customer_table, use_container_width=True, hide_index=True)

csv = customer_table.to_csv(index=False)
st.download_button(
    label="Download Customer Data (CSV)",
    data=csv,
    file_name="customer_data.csv",
    mime="text/csv",
)