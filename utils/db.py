import re, sqlite3
import numpy as np, pandas as pd, streamlit as st
from config import REQUIRED, ROOT

ALIAS = {"sub_category": "subcategory", "product_name": "product"}

def normalise(df):
    df = df.copy()
    df.columns = [c.strip().lower().replace("-", "_").replace(" ", "_") for c in df.columns]
    df = df.rename(columns=ALIAS)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing: raise ValueError(f"Missing required columns: {', '.join(missing)}")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    if "profit" not in df: df["profit"] = np.nan
    for c in ("quantity", "sales", "profit"): df[c] = pd.to_numeric(df[c], errors="coerce")
    return df[REQUIRED + ["profit"]]

@st.cache_data
def demo_data():
    """Synthetic data (seeded) so the app runs without a download. Clearly labelled in the UI."""
    r = np.random.default_rng(7)
    tree = {"Furniture": {"Chairs": [("Ergo Chair", 180), ("Task Chair", 95)], "Tables": [("Oak Table", 420), ("Side Table", 110)]},
            "Technology": {"Phones": [("Phone X", 520), ("Phone Lite", 240)], "Accessories": [("Keyboard", 70), ("Monitor", 260)]},
            "Office Supplies": {"Paper": [("Copy Paper", 35), ("Notebook", 12)], "Storage": [("File Box", 28), ("Shelf Unit", 85)]}}
    margin = {"Furniture": .08, "Technology": .17, "Office Supplies": .22}
    items = [(c, s, p, pr) for c, d in tree.items() for s, ps in d.items() for p, pr in ps]
    n = 350
    cid = [f"C{i:04d}" for i in range(n)]
    seg = r.choice(["Consumer", "Corporate", "Home Office"], n, p=[.5, .3, .2])
    reg = r.choice(["East", "West", "Central", "South"], n)
    w = r.gamma(1.2, size=n); w /= w.sum()
    days = pd.date_range("2023-01-01", "2025-12-31")
    rows = []
    for i in range(1800):
        ci = r.choice(n, p=w); d = days[r.integers(len(days))]
        for _ in range(r.integers(1, 4)):
            c, s, p, pr = items[r.integers(len(items))]
            q = int(r.integers(1, 6)); disc = r.choice([0, 0, .1, .2]); sales = round(pr * q * (1 - disc), 2)
            rows.append((f"O{i:05d}", d, cid[ci], seg[ci], reg[ci], c, s, p, q, sales,
                         round(sales * (margin[c] - disc * .5 + r.normal(0, .04)), 2)))
    return pd.DataFrame(rows, columns=REQUIRED + ["profit"])

@st.cache_resource
def get_conn(key, _df):
    con = sqlite3.connect(":memory:", check_same_thread=False)
    d = _df.copy(); d["order_date"] = d["order_date"].dt.strftime("%Y-%m-%d")
    d.to_sql("sales", con, index=False)
    con.execute("PRAGMA query_only=ON")
    return con

def filter_sql(start, end, cats, regs):
    ph = lambda xs: ",".join("?" * len(xs))
    return (f"order_date BETWEEN ? AND ? AND category IN ({ph(cats)}) AND region IN ({ph(regs)})",
            [start, end, *cats, *regs])

def run(con, sql, where, params):
    """All analytical SQL is read from our own whitelist; user values are only ever bound parameters."""
    s = sql.strip().rstrip(";")
    head = f"WITH f AS (SELECT * FROM sales WHERE {where})"
    full = f"{head}, {s[4:]}" if s.upper().startswith("WITH") else f"{head} {s}"
    return pd.read_sql_query(full, con, params=params)

@st.cache_data
def load_queries():
    out = []
    for blk in (ROOT / "sql" / "queries.sql").read_text().split("-- end"):
        meta, sql = {}, []
        for ln in blk.strip().splitlines():
            m = re.match(r"-- (\w+): (.*)", ln)
            if m: meta[m[1]] = m[2]
            else: sql.append(ln)
        if meta: meta["sql"] = "\n".join(sql).strip(); out.append(meta)
    return out
