import pandas as pd, streamlit as st
from utils.db import normalise, demo_data, get_conn, filter_sql
from utils.style import CSS
import ui as views

st.set_page_config(page_title="Sales Intelligence | SQL Analytics", page_icon="▪", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
sb = st.sidebar
sb.markdown("**SI / SALES INTELLIGENCE**")
sb.markdown("<span class='muted'>SQL ANALYTICS SYSTEM</span>", unsafe_allow_html=True)
page = sb.radio("Navigate", list(views.PAGES), label_visibility="collapsed")
sb.divider()

df, source, key = None, "Synthetic demo data", "demo"
up = sb.file_uploader("Upload sales CSV (optional)", type="csv")
if up:
    try: df, source, key = normalise(pd.read_csv(up)), f"Upload: {up.name}", f"{up.name}-{up.size}"
    except Exception as e: sb.error(f"Upload rejected: {e}")
if df is None: df = demo_data()
if df["order_date"].isna().all(): st.error("No valid dates found in the dataset."); st.stop()

lo, hi = df["order_date"].min().date(), df["order_date"].max().date()
rng = sb.date_input("Date range", (lo, hi), min_value=lo, max_value=hi)
cats = sb.multiselect("Category", sorted(df.category.dropna().unique()), sorted(df.category.dropna().unique()))
regs = sb.multiselect("Region", sorted(df.region.dropna().unique()), sorted(df.region.dropna().unique()))
sb.caption(f"● {len(df):,} rows loaded · {source}")
sb.markdown("<span class='muted'>Python · Streamlit · SQLite · Plotly</span>", unsafe_allow_html=True)
if len(rng) != 2: st.info("Select both a start and end date."); st.stop()
if not cats or not regs: st.warning("Select at least one category and one region."); st.stop()

start, end = rng
where, params = filter_sql(start.isoformat(), end.isoformat(), cats, regs)
span = (end - start).days + 1
pstart, pend = start - pd.Timedelta(days=span), start - pd.Timedelta(days=1)
prev = None
if pstart >= lo:
    prev = filter_sql(pstart.isoformat(), pend.isoformat(), cats, regs)
ctx = dict(conn=get_conn(key, df), where=where, params=params, prev=prev, start=start, end=end,
           source=source, has_profit=bool(df.profit.notna().any()))
views.PAGES[page](ctx)
