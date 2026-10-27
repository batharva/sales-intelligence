"""
Metrics calculation and KPI formatting utilities.
"""

import pandas as pd
import streamlit as st

from config import COLORS


def format_currency(value: float) -> str:
    """Format a number as USD currency."""
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    elif abs(value) >= 1_000:
        return f"${value:,.0f}"
    else:
        return f"${value:,.2f}"


def format_number(value: float) -> str:
    """Format a number with commas."""
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:,.2f}M"
    elif abs(value) >= 1_000:
        return f"{value:,.0f}"
    else:
        return f"{value:,.2f}"


def format_percent(value: float) -> str:
    """Format a number as percentage."""
    return f"{value:+.1f}%" if value != 0 else "0.0%"


def calc_delta(current: float, previous: float) -> tuple:
    """
    Calculate the change between current and previous period.
    Returns (delta_value, delta_pct, is_positive, is_valid).
    """
    if previous is None or previous == 0:
        return (None, None, None, False)
    delta_val = current - previous
    delta_pct = (delta_val / abs(previous)) * 100 if previous != 0 else 0
    is_positive = delta_val >= 0
    return (delta_val, delta_pct, is_positive, True)


def get_kpis(df_orders: pd.DataFrame, df_prev: pd.DataFrame = None) -> dict:
    """
    Calculate KPI values from an orders DataFrame.
    Returns a dict with keys: revenue, orders, units, aov, customers, profit.
    """
    if df_orders.empty:
        return {
            "revenue": 0, "orders": 0, "units": 0, "aov": 0,
            "customers": 0, "profit": 0,
        }

    revenue = float(df_orders["sales"].sum())
    orders = int(df_orders["order_id"].nunique())
    units = int(df_orders["quantity"].sum())
    aov = revenue / orders if orders > 0 else 0
    customers = int(df_orders["customer_id"].nunique()) if "customer_id" in df_orders.columns else 0
    profit = float(df_orders["profit"].sum()) if "profit" in df_orders.columns else 0

    return {
        "revenue": revenue,
        "orders": orders,
        "units": units,
        "aov": aov,
        "customers": customers,
        "profit": profit,
    }


def get_kpi_deltas(current: dict, previous: dict) -> dict:
    """Compute deltas between current and previous period KPIs."""
    deltas = {}
    for key in current:
        delta_val, delta_pct, is_positive, is_valid = calc_delta(
            current[key], previous.get(key, 0)
        )
        deltas[key] = {
            "value": delta_val,
            "pct": delta_pct,
            "is_positive": is_positive,
            "is_valid": is_valid,
        }
    return deltas


def render_kpi_row(kpis: dict, deltas: dict = None, cols=None):
    """
    Render a row of KPI metric cards.
    If cols is provided (list of st.columns), use those.
    """
    from utils.styling import metric_card

    if deltas is None:
        deltas = {k: {"value": None, "pct": None, "is_positive": None, "is_valid": False} for k in kpis}

    kpi_config = [
        ("Total Revenue", "revenue", format_currency),
        ("Total Orders", "orders", format_number),
        ("Units Sold", "units", format_number),
        ("Avg Order Value", "aov", format_currency),
        ("Unique Customers", "customers", format_number),
        ("Total Profit", "profit", format_currency),
    ]

    if cols is None:
        cols = st.columns(len(kpi_config))

    for i, (label, key, fmt_fn) in enumerate(kpi_config):
        if key not in kpis:
            continue
        value = kpis[key]
        delta_info = deltas.get(key, {})
        delta_str = None
        delta_pos = None

        if delta_info.get("is_valid") and delta_info["pct"] is not None:
            delta_str = f"{delta_info['pct']:+.1f}% vs prev period"
            delta_pos = delta_info["is_positive"]

        tooltip = f"Current: {fmt_fn(value)}"
        if delta_str:
            tooltip += f" | Change: {delta_str}"

        with cols[i]:
            st.markdown(
                metric_card(label, fmt_fn(value), delta_str, delta_pos, tooltip),
                unsafe_allow_html=True,
            )


def generate_executive_summary(kpis: dict, deltas: dict = None) -> str:
    """
    Generate an automatic executive summary based on KPI values.
    """
    parts = []

    revenue = kpis.get("revenue", 0)
    orders = kpis.get("orders", 0)
    aov = kpis.get("aov", 0)
    customers = kpis.get("customers", 0)
    profit = kpis.get("profit", 0)

    # Revenue statement
    parts.append(f"Total revenue reached **{format_currency(revenue)}**")

    if deltas and deltas.get("revenue", {}).get("is_valid"):
        rev_pct = deltas["revenue"]["pct"]
        if rev_pct > 0:
            parts.append(f"growing **{rev_pct:+.1f}%** compared to the previous period")
        elif rev_pct < 0:
            parts.append(f"declining **{rev_pct:+.1f}%** compared to the previous period")
        else:
            parts.append("remaining flat compared to the previous period")

    parts.append(f"from **{format_number(orders)}** orders by **{format_number(customers)}** customers")

    # AOV
    parts.append(f"The average order value is **{format_currency(aov)}**")

    # Profit
    if profit != 0:
        margin = (profit / revenue * 100) if revenue > 0 else 0
        parts.append(f"with a total profit of **{format_currency(profit)}** ({margin:+.1f}% margin)")

    summary = ". ".join(parts) + "."
    return summary