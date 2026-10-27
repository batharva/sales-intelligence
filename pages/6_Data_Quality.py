"""
Page 6: Data Quality
Data integrity checks and validation results.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import COLORS
from utils.styling import render_section_header, render_empty_state
from utils.database import execute_query_df, is_database_ready
from utils.metrics import format_number

st.markdown("<div style='margin-top:-2rem;'></div>", unsafe_allow_html=True)
render_section_header("Data Quality")

st.markdown(
    '<p style="font-size:0.85rem;color:#6B706D;">'
    "Automated data quality checks to validate the integrity and reliability of the sales dataset. "
    "These checks are executed against the database in real time."
    "</p>",
    unsafe_allow_html=True,
)

if not is_database_ready():
    render_empty_state("Database not available.")
    st.stop()

# ── Run Data Quality Checks ──
@st.cache_data(ttl=60)
def run_quality_checks():
    """Execute data quality SQL checks."""
    results = []

    # 1. Total row count
    df = execute_query_df("SELECT COUNT(*) as cnt FROM orders")
    total_rows = df["cnt"].iloc[0] if not df.empty else 0
    results.append({
        "Check": "Total Row Count",
        "Records Affected": format_number(total_rows),
        "Severity": "Info",
        "Description": f"Total order line items: {format_number(total_rows)}",
        "Action": "Baseline metric. No action required.",
        "Status": "✅",
    })

    # 2. Duplicate transactions
    df = execute_query_df("""
        SELECT COUNT(*) as cnt FROM (
            SELECT order_id, product_id, COUNT(*) as cnt
            FROM orders
            GROUP BY order_id, product_id
            HAVING COUNT(*) > 1
        )
    """)
    dupes = df["cnt"].iloc[0] if not df.empty else 0
    results.append({
        "Check": "Duplicate Transactions",
        "Records Affected": format_number(dupes),
        "Severity": "High" if dupes > 0 else "Low",
        "Description": "Order line items with identical order/product combinations",
        "Action": "Investigate source system for duplicate entries." if dupes > 0 else "No duplicates detected.",
        "Status": "⚠️" if dupes > 0 else "✅",
    })

    # 3. Missing values
    checks = [
        ("Missing Customer IDs", "customer_id", "High"),
        ("Missing Order Dates", "order_date", "High"),
        ("Missing Product IDs", "product_id", "High"),
        ("Missing Ship Dates", "ship_date", "Low"),
        ("Missing Sales Values", "sales", "High"),
        ("Missing Quantities", "quantity", "High"),
    ]
    for check_name, column, severity in checks:
        df = execute_query_df(
            f"SELECT COUNT(*) as cnt FROM orders WHERE {column} IS NULL OR {column} = ''"
        )
        cnt = df["cnt"].iloc[0] if not df.empty else 0
        if cnt > 0:
            results.append({
                "Check": check_name,
                "Records Affected": format_number(cnt),
                "Severity": severity,
                "Description": f"Records with missing '{column}' values",
                "Action": f"Review and populate missing {column} values." if cnt > 0 else "N/A",
                "Status": "⚠️" if cnt > 0 and severity == "High" else "ℹ️" if cnt > 0 else "✅",
            })

    # 4. Invalid quantity
    df = execute_query_df("SELECT COUNT(*) as cnt FROM orders WHERE quantity <= 0")
    invalid_qty = df["cnt"].iloc[0] if not df.empty else 0
    results.append({
        "Check": "Invalid Quantities",
        "Records Affected": format_number(invalid_qty),
        "Severity": "Medium" if invalid_qty > 0 else "Low",
        "Description": "Orders with zero or negative quantities (may represent returns)",
        "Action": "Verify if these are legitimate returns/credits." if invalid_qty > 0 else "No issues detected.",
        "Status": "ℹ️" if invalid_qty > 0 else "✅",
    })

    # 5. Negative or zero sales
    df = execute_query_df("SELECT COUNT(*) as cnt FROM orders WHERE sales <= 0")
    neg_sales = df["cnt"].iloc[0] if not df.empty else 0
    results.append({
        "Check": "Negative/Zero Sales",
        "Records Affected": format_number(neg_sales),
        "Severity": "Medium" if neg_sales > 0 else "Low",
        "Description": "Orders with non-positive sales values (credits or errors)",
        "Action": "Confirm if credits/returns are accounted for correctly." if neg_sales > 0 else "No issues detected.",
        "Status": "ℹ️" if neg_sales > 0 else "✅",
    })

    # 6. Extreme discounts
    df = execute_query_df("SELECT COUNT(*) as cnt FROM orders WHERE discount > 0.5")
    extreme_disc = df["cnt"].iloc[0] if not df.empty else 0
    results.append({
        "Check": "Extreme Discounts (>50%)",
        "Records Affected": format_number(extreme_disc),
        "Severity": "Low" if extreme_disc > 0 else "Low",
        "Description": "Orders with discounts exceeding 50%",
        "Action": "Review pricing policy for high-discount items." if extreme_disc > 0 else "No extreme discounts detected.",
        "Status": "ℹ️" if extreme_disc > 0 else "✅",
    })

    # 7. Negative profit
    df = execute_query_df("SELECT COUNT(*) as cnt FROM orders WHERE profit < 0")
    neg_profit = df["cnt"].iloc[0] if not df.empty else 0
    results.append({
        "Check": "Negative Profit Orders",
        "Records Affected": format_number(neg_profit),
        "Severity": "Medium" if neg_profit > 0 else "Low",
        "Description": "Orders sold at a loss (negative profit margin)",
        "Action": "Review pricing and discounting strategy for loss-making items." if neg_profit > 0 else "No losses detected.",
        "Status": "ℹ️" if neg_profit > 0 else "✅",
    })

    # 8. Referential integrity
    checks_ri = [
        ("Orphan Orders (Customers)", "orders o LEFT JOIN customers c ON o.customer_id = c.customer_id WHERE c.customer_id IS NULL", "High"),
        ("Orphan Orders (Products)", "orders o LEFT JOIN products p ON o.product_id = p.product_id WHERE p.product_id IS NULL", "High"),
    ]
    for check_name, condition, severity in checks_ri:
        df = execute_query_df(f"SELECT COUNT(*) as cnt FROM {condition}")
        cnt = df["cnt"].iloc[0] if not df.empty else 0
        if cnt > 0:
            results.append({
                "Check": check_name,
                "Records Affected": format_number(cnt),
                "Severity": severity,
                "Description": f"Records violating referential integrity",
                "Action": "Fix missing foreign key references in the source data.",
                "Status": "⚠️",
            })

    # 9. Future dates
    df = execute_query_df("SELECT COUNT(*) as cnt FROM orders WHERE order_date > date('now')")
    future_dates = df["cnt"].iloc[0] if not df.empty else 0
    if future_dates > 0:
        results.append({
            "Check": "Future Order Dates",
            "Records Affected": format_number(future_dates),
            "Severity": "Medium",
            "Description": "Orders with dates in the future",
            "Action": "Verify date entry or timezone settings.",
            "Status": "⚠️",
        })

    # 10. Ship date before order date
    df = execute_query_df("SELECT COUNT(*) as cnt FROM orders WHERE ship_date < order_date")
    ship_before = df["cnt"].iloc[0] if not df.empty else 0
    if ship_before > 0:
        results.append({
            "Check": "Ship Date Before Order Date",
            "Records Affected": format_number(ship_before),
            "Severity": "Medium",
            "Description": "Orders where shipping precedes ordering",
            "Action": "Investigate data entry errors or timezone issues.",
            "Status": "⚠️",
        })

    # 11. Category inconsistencies
    df = execute_query_df("SELECT COUNT(*) as cnt FROM products WHERE category IS NULL OR category = ''")
    bad_cats = df["cnt"].iloc[0] if not df.empty else 0
    if bad_cats > 0:
        results.append({
            "Check": "Missing Product Categories",
            "Records Affected": format_number(bad_cats),
            "Severity": "Medium",
            "Description": "Products without a category assignment",
            "Action": "Assign categories to unclassified products.",
            "Status": "⚠️",
        })

    return pd.DataFrame(results), total_rows


df_quality, total_rows = run_quality_checks()

# ── Summary KPIs ──
issues_count = len(df_quality[df_quality["Status"].isin(["⚠️", "ℹ️"])])
high_severity = len(df_quality[df_quality["Severity"] == "High"])

kpi_cols = st.columns(4)
with kpi_cols[0]:
    st.markdown(
        f'<div class="kpi-container">'
        f'<div class="kpi-label">Total Records</div>'
        f'<div class="kpi-value">{format_number(total_rows)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
with kpi_cols[1]:
    st.markdown(
        f'<div class="kpi-container">'
        f'<div class="kpi-label">Checks Run</div>'
        f'<div class="kpi-value">{len(df_quality)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
with kpi_cols[2]:
    st.markdown(
        f'<div class="kpi-container">'
        f'<div class="kpi-label">Issues Found</div>'
        f'<div class="kpi-value">{issues_count}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
with kpi_cols[3]:
    st.markdown(
        f'<div class="kpi-container">'
        f'<div class="kpi-label">High Severity</div>'
        f'<div class="kpi-value">{high_severity}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Results Table ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
st.markdown("<h3>Quality Check Results</h3>", unsafe_allow_html=True)

# Color the severity column
def color_severity(val):
    if val == "High":
        return f'color: {COLORS["negative"]}; font-weight: 600;'
    elif val == "Medium":
        return f'color: #B8860B; font-weight: 500;'
    elif val == "Low":
        return f'color: {COLORS["text_secondary"]};'
    return ""

styled_df = df_quality.style.map(color_severity, subset=["Severity"])
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# ── Visual Summary ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    st.markdown("<h3>Severity Distribution</h3>", unsafe_allow_html=True)
    severity_dist = df_quality["Severity"].value_counts().reset_index()
    severity_dist.columns = ["Severity", "Count"]

    colors_map = {
        "High": COLORS["negative"],
        "Medium": "#B8860B",
        "Low": COLORS["text_secondary"],
        "Info": COLORS["accent_secondary"],
    }

    fig = px.bar(
        severity_dist, x="Severity", y="Count",
        color="Severity",
        color_discrete_map=colors_map,
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="%{x}: %{y} checks<extra></extra>",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title=None,
        yaxis_title="Number of Checks",
        height=250,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=11, color=COLORS["text_secondary"]),
        xaxis=dict(gridcolor=COLORS["chart_grid"]),
        yaxis=dict(gridcolor=COLORS["chart_grid"]),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="dq_severity")

with c2:
    st.markdown("<h3>Status Overview</h3>", unsafe_allow_html=True)
    status_dist = df_quality["Status"].value_counts().reset_index()
    status_dist.columns = ["Status", "Count"]

    fig = px.pie(
        status_dist, values="Count", names="Status",
        color_discrete_sequence=[COLORS["positive"], "#B8860B", COLORS["accent_secondary"]],
    )
    fig.update_traces(
        textinfo="label+percent",
        textposition="outside",
        marker=dict(line=dict(color=COLORS["surface"], width=2)),
        hovertemplate="<b>%{label}</b><br>%{value} checks (%{percent})<extra></extra>",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=30),
        height=250,
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor=COLORS["surface"],
        font=dict(family="Inter, sans-serif", size=11, color=COLORS["text_secondary"]),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="dq_status")

# ── Methodology ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
with st.expander("Data Quality Methodology"):
    st.markdown(
        """
        **How Data Quality Checks Work**

        Each check runs a specific SQL query against the database and reports:

        - **Records Affected**: Number of rows that fail the check
        - **Severity**: 
          - **High**: Issues that could invalidate analysis results
          - **Medium**: Issues that require attention but may not block analysis
          - **Low**: Minor issues or informational flags
        - **Description**: What the check validates
        - **Action**: Recommended next steps

        **Important Notes:**
        - Negative quantities and sales may represent legitimate returns/credits
        - Extreme discounts may indicate promotional pricing or data errors
        - Referential integrity checks ensure foreign key relationships are valid
        - No records are automatically deleted — all data is preserved for analysis
        """,
        unsafe_allow_html=True,
    )