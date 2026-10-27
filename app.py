"""
Sales Intelligence | SQL Analytics
Industrial-minimal Streamlit dashboard for retail sales analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import APP_NAME, APP_SUBTITLE, APP_VERSION, APP_YEAR, COLORS, PAGES
from utils.styling import apply_css, render_section_header
from utils.database import is_database_ready
from utils.metrics import get_kpis, get_kpi_deltas, render_kpi_row, format_number, generate_executive_summary
from utils.data_loader import ensure_database, get_dataset_stats, get_filter_options, get_filtered_data, get_previous_period_data

# ── Page configuration ──────────────────────────────────────────────────────────

st.set_page_config(
    page_title=f"{APP_NAME} | {APP_SUBTITLE}",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_css()

# ── Initialize session state ────────────────────────────────────────────────────

if "current_page" not in st.session_state:
    st.session_state.current_page = "Overview"
if "date_range" not in st.session_state:
    st.session_state.date_range = None
if "selected_categories" not in st.session_state:
    st.session_state.selected_categories = []
if "selected_regions" not in st.session_state:
    st.session_state.selected_regions = []

# ── Database initialization ──────────────────────────────────────────────────────

db_ready = ensure_database()
filter_options = get_filter_options() if db_ready else {}
if db_ready:
    st.session_state["_filter_options"] = filter_options

# ── Sidebar ──────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        f'<div class="sidebar-logo">SI / {APP_NAME.upper()}</div>'
        f'<div class="sidebar-subtitle">{APP_SUBTITLE}</div>'
        f'<hr class="sidebar-divider" />',
        unsafe_allow_html=True,
    )

    nav_selection = st.radio(
        "Navigation", PAGES,
        index=PAGES.index(st.session_state.current_page),
        label_visibility="collapsed",
        key="nav_radio",
    )
    st.session_state.current_page = nav_selection

    st.markdown('<hr class="sidebar-divider" />', unsafe_allow_html=True)

    if db_ready:
        st.markdown(
            '<div style="font-size:0.7rem;font-weight:600;color:#637D8A;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.4rem;">Filters</div>',
            unsafe_allow_html=True,
        )

        date_min = filter_options.get("date_min")
        date_max = filter_options.get("date_max")
        if date_min and date_max:
            date_min_dt = pd.to_datetime(date_min)
            date_max_dt = pd.to_datetime(date_max)
            date_range = st.date_input(
                "Date Range",
                value=(date_min_dt, date_max_dt),
                min_value=date_min_dt,
                max_value=date_max_dt,
                label_visibility="collapsed",
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                st.session_state.date_range = date_range
            else:
                st.session_state.date_range = (date_min_dt, date_max_dt)

        categories = filter_options.get("categories", [])
        if categories:
            selected_cats = st.multiselect(
                "Category",
                options=categories,
                default=st.session_state.selected_categories if st.session_state.selected_categories else categories,
                label_visibility="collapsed",
                placeholder="All Categories",
            )
            st.session_state.selected_categories = selected_cats

        regions = filter_options.get("regions", [])
        if regions:
            selected_regions = st.multiselect(
                "Region",
                options=regions,
                default=st.session_state.selected_regions if st.session_state.selected_regions else regions,
                label_visibility="collapsed",
                placeholder="All Regions",
            )
            st.session_state.selected_regions = selected_regions

        st.markdown('<hr class="sidebar-divider" />', unsafe_allow_html=True)

    stats = get_dataset_stats()
    status_color = "active" if stats["status"] == "Loaded" else "inactive"
    st.markdown(
        f'<div style="font-size:0.75rem;color:#6B706D;margin-bottom:0.3rem;">'
        f'<span class="status-indicator status-{status_color}"></span>'
        f'Dataset: {stats["status"]}'
        f'</div>',
        unsafe_allow_html=True,
    )
    if stats["orders"] > 0:
        st.markdown(
            f'<div style="font-size:0.65rem;color:#6B706D;">'
            f'Rows: {format_number(stats["orders"])} &middot; '
            f'Customers: {format_number(stats["customers"])} &middot; '
            f'Products: {format_number(stats["products"])}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sidebar-divider" />', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sidebar-footer">'
        f'{APP_NAME} v{APP_VERSION}<br>'
        f'{APP_YEAR} &middot; Python &middot; Streamlit &middot; SQLite<br>'
        f'Built with Plotly &amp; Pandas'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Page dispatch ───────────────────────────────────────────────────────────────

page = st.session_state.current_page

if not db_ready:
    st.markdown(
        '<div style="text-align:center;padding:4rem 2rem;">'
        f'<h2 style="color:#191B1A;">{APP_NAME}</h2>'
        f'<p style="color:#6B706D;">{APP_SUBTITLE}</p>'
        '<hr style="border-color:#D9DDD7;width:60px;margin:1.5rem auto;" />'
        '<p>Generating the analytical database. This may take a moment...</p>'
        '<p style="font-size:0.8rem;color:#6B706D;">Refresh the page once the generation completes.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── OVERVIEW PAGE ───────────────────────────────────────────────────────────────

if page == "Overview":
    render_section_header("Overview")

    df = get_filtered_data(filter_options)
    df_prev = get_previous_period_data(filter_options)

    if df.empty:
        from utils.styling import render_empty_state
        render_empty_state("No data matches the current filter selections.")
        st.stop()

    kpis = get_kpis(df)
    kpis_prev = get_kpis(df_prev) if not df_prev.empty else {}
    deltas = get_kpi_deltas(kpis, kpis_prev) if kpis_prev else {}

    kpi_cols = st.columns(6)
    render_kpi_row(kpis, deltas, kpi_cols)

    st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3>Revenue Trend</h3>", unsafe_allow_html=True)
        agg_option = st.selectbox(
            "Aggregation", ["Daily", "Weekly", "Monthly", "Quarterly"],
            key="overview_agg", label_visibility="collapsed",
        )

        df_trend = df.copy()
        df_trend["date"] = pd.to_datetime(df_trend["order_date"])
        if agg_option == "Daily":
            df_trend["period"] = df_trend["date"].dt.strftime("%Y-%m-%d")
        elif agg_option == "Weekly":
            df_trend["period"] = df_trend["date"].dt.strftime("%Y-W%W")
        elif agg_option == "Monthly":
            df_trend["period"] = df_trend["date"].dt.strftime("%Y-%m")
        else:
            df_trend["period"] = df_trend["date"].dt.to_period("Q").astype(str)

        trend_data = df_trend.groupby("period")["sales"].sum().reset_index().sort_values("period")

        fig = px.line(
            trend_data, x="period", y="sales",
            line_shape="spline",
        )
        fig.update_traces(
            line=dict(color=COLORS["accent_primary"], width=2),
            fill="tozeroy",
            fillcolor=f"rgba(40, 92, 72, 0.08)",
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=30),
            xaxis_title=None, yaxis_title="Revenue ($)",
            showlegend=False, height=300,
            plot_bgcolor=COLORS["surface"], paper_bgcolor=COLORS["surface"],
            font=dict(family="Inter, sans-serif", size=11, color=COLORS["text_secondary"]),
            hovermode="x unified",
            xaxis=dict(gridcolor=COLORS["chart_grid"], linecolor=COLORS["border"]),
            yaxis=dict(gridcolor=COLORS["chart_grid"], linecolor=COLORS["border"]),
        )
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True, key="overview_trend")

    with col2:
        st.markdown("<h3>Revenue by Category</h3>", unsafe_allow_html=True)
        cat_rev = df.groupby("category")["sales"].sum().reset_index().sort_values("sales")

        fig = px.bar(cat_rev, x="sales", y="category", orientation="h")
        fig.update_traces(
            marker_color=COLORS["chart_colors"][0], marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>",
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=30),
            xaxis_title="Revenue ($)", yaxis_title=None,
            showlegend=False, height=300,
            plot_bgcolor=COLORS["surface"], paper_bgcolor=COLORS["surface"],
            font=dict(family="Inter, sans-serif", size=11, color=COLORS["text_secondary"]),
            hovermode="y unified",
            xaxis=dict(gridcolor=COLORS["chart_grid"], linecolor=COLORS["border"]),
            yaxis=dict(gridcolor=COLORS["chart_grid"], linecolor=COLORS["border"]),
            yaxis_autorange="reversed",
        )
        st.plotly_chart(fig, use_container_width=True, key="overview_cat")

    st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("<h3>Top 5 Products by Revenue</h3>", unsafe_allow_html=True)
        top_products = (
            df.groupby("product_name")["sales"].sum().reset_index()
            .sort_values("sales", ascending=False).head(5)
        )
        fig = px.bar(
            top_products, x="sales", y="product_name", orientation="h",
        )
        fig.update_traces(
            marker_color=COLORS["accent_secondary"], marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>",
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=30),
            xaxis_title="Revenue ($)", yaxis_title=None,
            showlegend=False, height=220,
            plot_bgcolor=COLORS["surface"], paper_bgcolor=COLORS["surface"],
            font=dict(family="Inter, sans-serif", size=10, color=COLORS["text_secondary"]),
            xaxis=dict(gridcolor=COLORS["chart_grid"]),
            yaxis=dict(gridcolor=COLORS["chart_grid"]),
            yaxis_autorange="reversed",
        )
        st.plotly_chart(fig, use_container_width=True, key="overview_top5")

    with col4:
        st.markdown("<h3>Revenue by Region</h3>", unsafe_allow_html=True)
        reg_rev = df.groupby("region")["sales"].sum().reset_index().sort_values("sales")
        fig = px.bar(reg_rev, x="sales", y="region", orientation="h")
        fig.update_traces(
            marker_color=COLORS["chart_colors"][1], marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>",
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=30),
            xaxis_title="Revenue ($)", yaxis_title=None,
            showlegend=False, height=220,
            plot_bgcolor=COLORS["surface"], paper_bgcolor=COLORS["surface"],
            font=dict(family="Inter, sans-serif", size=10, color=COLORS["text_secondary"]),
            xaxis=dict(gridcolor=COLORS["chart_grid"]),
            yaxis=dict(gridcolor=COLORS["chart_grid"]),
            yaxis_autorange="reversed",
        )
        st.plotly_chart(fig, use_container_width=True, key="overview_region")

    st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
    st.markdown("<h3>Executive Summary</h3>", unsafe_allow_html=True)
    summary = generate_executive_summary(kpis, deltas)
    st.markdown(
        f'<div style="background-color:#FFFFFF;border:1px solid #D9DDD7;padding:1rem 1.25rem;font-size:0.9rem;line-height:1.7;color:#191B1A;">{summary}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div style="margin-top:1.25rem;"></div>', unsafe_allow_html=True)
    with st.expander("Recent Order Activity"):
        recent = df.sort_values("order_date", ascending=False).head(20)[
            ["order_date", "order_id", "customer_name", "product_name", "category", "sales", "quantity", "region"]
        ]
        st.dataframe(recent, use_container_width=True, hide_index=True)
        csv = recent.to_csv(index=False)
        st.download_button(label="Download CSV", data=csv, file_name="recent_orders.csv", mime="text/csv")

elif page == "Revenue Analysis":
    exec(open("pages/1_Revenue_Analysis.py", encoding="utf-8").read())
elif page == "Product Intelligence":
    exec(open("pages/2_Product_Intelligence.py", encoding="utf-8").read())
elif page == "Customer Intelligence":
    exec(open("pages/3_Customer_Intelligence.py", encoding="utf-8").read())
elif page == "Regional Performance":
    exec(open("pages/4_Regional_Performance.py", encoding="utf-8").read())
elif page == "SQL Explorer":
    exec(open("pages/5_SQL_Explorer.py", encoding="utf-8").read())
elif page == "Data Quality":
    exec(open("pages/6_Data_Quality.py", encoding="utf-8").read())
elif page == "Methodology":
    exec(open("pages/7_Methodology.py", encoding="utf-8").read())