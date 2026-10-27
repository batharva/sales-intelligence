"""
Data loader — handles dataset loading, validation, and database seeding.
Also provides filtered data access for dashboard pages.
"""

import pathlib
import sys
import pandas as pd
import streamlit as st

from config import DB_PATH, DATA_DIR
from utils.database import is_database_ready, execute_query_df


def ensure_database() -> bool:
    """Ensure the database exists and is populated."""
    if is_database_ready():
        return True

    try:
        db_dir = DB_PATH.parent
        db_dir.mkdir(parents=True, exist_ok=True)

        sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
        from database.seed_database import seed_database
        success = seed_database(str(DB_PATH))
        return bool(success and is_database_ready())
    except Exception as e:
        st.error(f"Failed to seed database: {str(e)}")
        return False


def get_dataset_stats() -> dict:
    """Get basic statistics about the loaded dataset."""
    stats = {
        "status": "Not loaded",
        "orders": 0, "customers": 0, "products": 0,
        "date_range": None,
    }

    if not is_database_ready():
        return stats

    try:
        from utils.database import execute_query

        rows, _, _, _ = execute_query("SELECT COUNT(*) as cnt FROM orders")
        if rows:
            stats["orders"] = rows[0]["cnt"]

        rows, _, _, _ = execute_query("SELECT COUNT(DISTINCT customer_id) as cnt FROM orders")
        if rows:
            stats["customers"] = rows[0]["cnt"]

        rows, _, _, _ = execute_query("SELECT COUNT(DISTINCT product_id) as cnt FROM orders")
        if rows:
            stats["products"] = rows[0]["cnt"]

        rows, _, _, _ = execute_query(
            "SELECT MIN(order_date) as min_date, MAX(order_date) as max_date FROM orders"
        )
        if rows:
            stats["date_range"] = (rows[0]["min_date"], rows[0]["max_date"])

        stats["status"] = "Loaded"
    except Exception:
        stats["status"] = "Error"

    return stats


@st.cache_data(ttl=60)
def get_filter_options() -> dict:
    """Get available filter options from the database."""
    options = {"categories": [], "regions": [], "date_min": None, "date_max": None}

    try:
        df_cat = execute_query_df("SELECT DISTINCT category FROM products ORDER BY category")
        if not df_cat.empty:
            options["categories"] = df_cat["category"].tolist()

        df_reg = execute_query_df("SELECT DISTINCT region FROM customers ORDER BY region")
        if not df_reg.empty:
            options["regions"] = df_reg["region"].tolist()

        df_dates = execute_query_df(
            "SELECT MIN(order_date) as min_d, MAX(order_date) as max_d FROM orders"
        )
        if not df_dates.empty:
            options["date_min"] = df_dates["min_d"].iloc[0]
            options["date_max"] = df_dates["max_d"].iloc[0]
    except Exception:
        pass

    return options


def get_filtered_data(filter_options: dict = None) -> pd.DataFrame:
    """Get orders data filtered by current sidebar selections."""
    if not is_database_ready():
        return pd.DataFrame()

    if filter_options is None:
        filter_options = st.session_state.get("_filter_options", get_filter_options())

    conditions = []
    params = []

    if st.session_state.get("date_range"):
        dr = st.session_state.date_range
        if isinstance(dr, tuple) and len(dr) == 2:
            conditions.append("o.order_date >= ? AND o.order_date <= ?")
            params.extend([
                pd.Timestamp(dr[0]).strftime("%Y-%m-%d"),
                pd.Timestamp(dr[1]).strftime("%Y-%m-%d")
            ])

    cats = st.session_state.get("selected_categories", [])
    if cats and len(cats) < len(filter_options.get("categories", [])):
        placeholders = ",".join(["?" for _ in cats])
        conditions.append(f"p.category IN ({placeholders})")
        params.extend(cats)

    regs = st.session_state.get("selected_regions", [])
    if regs and len(regs) < len(filter_options.get("regions", [])):
        placeholders = ",".join(["?" for _ in regs])
        conditions.append(f"c.region IN ({placeholders})")
        params.extend(regs)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    sql = f"""
        SELECT o.*, p.category, p.subcategory, p.product_name,
               c.region, c.segment, c.customer_name
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE {where_clause}
    """

    try:
        return execute_query_df(sql, params=tuple(params))
    except Exception as e:
        st.error(f"Query error: {str(e)}")
        return pd.DataFrame()


def get_previous_period_data(filter_options: dict = None) -> pd.DataFrame:
    """Get data from the period prior to the current date range for comparison."""
    if not is_database_ready() or not st.session_state.get("date_range"):
        return pd.DataFrame()

    dr = st.session_state.date_range
    if not isinstance(dr, tuple) or len(dr) != 2:
        return pd.DataFrame()

    start = pd.to_datetime(dr[0])
    end = pd.to_datetime(dr[1])
    period_days = (end - start).days
    prev_end = start - pd.Timedelta(days=1)
    prev_start = prev_end - pd.Timedelta(days=period_days)

    if filter_options is None:
        filter_options = st.session_state.get("_filter_options", get_filter_options())

    conditions = []
    params = []

    conditions.append("o.order_date >= ? AND o.order_date <= ?")
    params.extend([prev_start.strftime("%Y-%m-%d"), prev_end.strftime("%Y-%m-%d")])

    cats = st.session_state.get("selected_categories", [])
    if cats and len(cats) < len(filter_options.get("categories", [])):
        placeholders = ",".join(["?" for _ in cats])
        conditions.append(f"p.category IN ({placeholders})")
        params.extend(cats)

    regs = st.session_state.get("selected_regions", [])
    if regs and len(regs) < len(filter_options.get("regions", [])):
        placeholders = ",".join(["?" for _ in regs])
        conditions.append(f"c.region IN ({placeholders})")
        params.extend(regs)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    sql = f"""
        SELECT o.sales, o.quantity, o.profit, o.order_id, o.customer_id,
               p.category, c.region
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE {where_clause}
    """

    try:
        return execute_query_df(sql, params=tuple(params))
    except Exception:
        return pd.DataFrame()