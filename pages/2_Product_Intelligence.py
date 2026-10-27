"""
Page 2: Product Intelligence
Product performance analysis, rankings, and profitability.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import COLORS
from utils.styling import render_section_header, render_empty_state
from utils.metrics import format_currency

st.markdown("<div style='margin-top:-2rem;'></div>", unsafe_allow_html=True)
render_section_header("Product Intelligence")

from utils.data_loader import get_filtered_data
from utils.database import is_database_ready

db_ready = is_database_ready()
df = get_filtered_data()

if df.empty:
    render_empty_state()
    st.stop()

# ── Controls ──
col1, col2, col3 = st.columns(3)
with col1:
    cat_filter = st.selectbox("Category", ["All"] + sorted(df["category"].unique().tolist()), key="prod_cat")
with col2:
    rank_metric = st.selectbox("Ranking Metric", ["Revenue", "Quantity Sold", "Profit"], key="prod_metric")
with col3:
    top_n = st.selectbox("Top N", [10, 20, 50, 100], index=0, key="prod_n")

plot_df = df.copy()
if cat_filter != "All":
    plot_df = plot_df[plot_df["category"] == cat_filter]

if plot_df.empty:
    render_empty_state()
    st.stop()

# ── Ranking ──
metric_map = {"Revenue": "sales", "Quantity Sold": "quantity", "Profit": "profit"}
sort_col = metric_map[rank_metric]

product_stats = plot_df.groupby(["product_id", "product_name", "category", "subcategory"]).agg(
    revenue=("sales", "sum"),
    quantity=("quantity", "sum"),
    profit=("profit", "sum"),
).reset_index()

product_stats["profit_margin"] = (product_stats["profit"] / product_stats["revenue"] * 100).round(2)
product_stats["profit_margin"] = product_stats["profit_margin"].fillna(0)

product_stats = product_stats.sort_values(sort_col, ascending=False)

top_products = product_stats.head(top_n)
bottom_products = product_stats[product_stats["revenue"] > 0].sort_values("revenue").head(10)

# ── Charts ──
c1, c2 = st.columns(2)

with c1:
    st.markdown(f"<h3>Top {top_n} Products by {rank_metric}</h3>", unsafe_allow_html=True)
    plot_data = top_products.head(10).iloc[::-1]
    fig = px.bar(
        plot_data, x=sort_col, y="product_name",
        orientation="h",
        color="category",
        color_discrete_sequence=COLORS["chart_colors"],
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>" + rank_metric + ": %{x:,.0f}<br>Category: %{customdata[0]}<extra></extra>",
        customdata=plot_data[["category"]],
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title=rank_metric,
        yaxis_title=None,
        height=350,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=10, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        legend=dict(orientation="h", y=1.05, font=dict(size=9)),
    )
    st.plotly_chart(fig, use_container_width=True, key="prod_top")

with c2:
    st.markdown("<h3>Bottom 10 Products by Revenue</h3>", unsafe_allow_html=True)
    plot_data = bottom_products.iloc[::-1]
    fig = px.bar(
        plot_data, x="revenue", y="product_name",
        orientation="h",
        color="category",
        color_discrete_sequence=COLORS["chart_colors"],
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>",
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
    st.plotly_chart(fig, use_container_width=True, key="prod_bottom")

# ── Category Performance ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    st.markdown("<h3>Category Performance</h3>", unsafe_allow_html=True)
    cat_perf = plot_df.groupby("category").agg(
        revenue=("sales", "sum"),
        quantity=("quantity", "sum"),
        profit=("profit", "sum"),
        products=("product_id", "nunique"),
    ).reset_index()
    cat_perf["margin"] = (cat_perf["profit"] / cat_perf["revenue"] * 100).round(2)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cat_perf["category"], y=cat_perf["revenue"],
        name="Revenue",
        marker_color=COLORS["accent_primary"],
        hovertemplate="%{x}<br>Revenue: $%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=cat_perf["category"], y=cat_perf["profit"],
        name="Profit",
        marker_color=COLORS["accent_secondary"],
        hovertemplate="%{x}<br>Profit: $%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        barmode="group",
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title=None,
        yaxis_title="$",
        height=300,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=10, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        legend=dict(orientation="h", y=1.05, font=dict(size=9)),
    )
    st.plotly_chart(fig, use_container_width=True, key="prod_cat_perf")

with c4:
    st.markdown("<h3>Revenue Concentration</h3>", unsafe_allow_html=True)
    # Revenue share of top N vs rest
    all_rev = product_stats["revenue"].sum()
    top_rev = top_products["revenue"].sum()
    other_rev = all_rev - top_rev

    conc_df = pd.DataFrame({
        "group": [f"Top {top_n} Products", "Other Products"],
        "revenue": [top_rev, other_rev],
    })

    fig = px.pie(
        conc_df, values="revenue", names="group",
        color_discrete_sequence=[COLORS["accent_primary"], COLORS["chart_grid"]],
    )
    fig.update_traces(
        textinfo="label+percent",
        textposition="outside",
        marker=dict(line=dict(color=COLORS["surface"], width=2)),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        height=300,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=11, color=COLORS["text_secondary"]),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="prod_concentration")

# ── Product Table ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
st.markdown("<h3>Product Search &amp; Data</h3>", unsafe_allow_html=True)

search = st.text_input("Search product name", "", placeholder="Type to filter products...", label_visibility="collapsed")

table_df = product_stats.copy()
if search:
    table_df = table_df[table_df["product_name"].str.lower().str.contains(search.lower(), na=False)]

display_cols = ["product_name", "category", "subcategory", "revenue", "quantity", "profit", "profit_margin"]
display_names = ["Product", "Category", "Subcategory", "Revenue", "Qty Sold", "Profit", "Margin %"]
display_df = table_df[display_cols].copy()
display_df.columns = display_names
display_df["Revenue"] = display_df["Revenue"].apply(lambda x: f"${x:,.2f}")
display_df["Profit"] = display_df["Profit"].apply(lambda x: f"${x:,.2f}")
display_df["Margin %"] = display_df["Margin %"].apply(lambda x: f"{x:.1f}%")

st.dataframe(display_df, use_container_width=True, hide_index=True)

csv = table_df.to_csv(index=False)
st.download_button(
    label="Download Product Data (CSV)",
    data=csv,
    file_name="product_data.csv",
    mime="text/csv",
)