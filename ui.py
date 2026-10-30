import time
import numpy as np, pandas as pd, plotly.express as px, streamlit as st
from config import P
from utils.db import run, load_queries
from utils.style import kpi

TRUNC = {"Daily": "strftime('%Y-%m-%d',order_date)", "Weekly": "strftime('%Y-W%W',order_date)",
         "Monthly": "strftime('%Y-%m',order_date)",
         "Quarterly": "strftime('%Y',order_date)||'-Q'||((CAST(strftime('%m',order_date) AS INT)+2)/3)"}
KPI = ("SELECT SUM(sales) rev, COUNT(DISTINCT order_id) orders, SUM(quantity) units, "
       "COUNT(DISTINCT customer_id) cust, SUM(profit) profit FROM f")

def q(c, sql, where=None, params=None):
    return run(c["conn"], sql, where or c["where"], c["params"] if params is None else params)
def sty(fig, h=330):
    fig.update_layout(height=h, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="#fff", font=dict(color=P["text"]), colorway=[P["accent"], P["steel"]])
    fig.update_xaxes(gridcolor=P["grid"]); fig.update_yaxes(gridcolor=P["grid"]); return fig
def show(fig): st.plotly_chart(sty(fig), width="stretch")
def money(x): return "N/A" if x is None or pd.isna(x) else f"${x:,.0f}"
def num(x): return "N/A" if x is None or pd.isna(x) else f"{x:,.0f}"
def pct(a, b): return None if a is None or b is None or pd.isna(a) or pd.isna(b) or not b else (a - b) / b * 100
def export(df, name): st.download_button("Export CSV", df.to_csv(index=False), name, "text/csv", key=name)
def header(n, title, desc, c):
    st.markdown(f"<div class='eyebrow'>{n:02d} / {title.upper()}</div>", unsafe_allow_html=True)
    st.title(title); st.caption(f"{desc} · {c['start']} → {c['end']} · {c['source']}"); st.divider()
def barh(df, x, y, **k):
    return px.bar(df.sort_values(x), x=x, y=y, orientation="h", **k)

def overview(c):
    header(1, "Executive Overview", "Revenue, volume and customer reach for the selected scope.", c)
    k = q(c, KPI).iloc[0]
    if not k.orders: st.info("No orders match the current filters."); return
    p = q(c, KPI, *c["prev"]).iloc[0] if c["prev"] else None
    def vals(r):
        d = {"Total Revenue": r.rev, "Orders": r.orders, "Units Sold": r.units,
             "Avg Order Value": r.rev / r.orders if r.orders else None, "Customers": r.cust}
        if c["has_profit"]: d["Profit"] = r.profit
        return d
    cur, prev = vals(k), (vals(p) if p is not None else {})
    fmt = {"Total Revenue": money, "Avg Order Value": money, "Profit": money}
    tip = {"Total Revenue": "SUM(sales)", "Orders": "COUNT(DISTINCT order_id)", "Units Sold": "SUM(quantity)",
           "Avg Order Value": "Revenue / distinct orders", "Customers": "COUNT(DISTINCT customer_id)", "Profit": "SUM(profit)"}
    for col, l in zip(st.columns(len(cur)), cur):
        col.markdown(kpi(l, fmt.get(l, num)(cur[l]), pct(cur[l], prev.get(l)), tip[l]), unsafe_allow_html=True)
    L, R = st.columns([3, 2])
    with L:
        f = st.selectbox("Aggregation", list(TRUNC), 2, key="ov_f")
        t = q(c, f"SELECT {TRUNC[f]} period, SUM(sales) revenue FROM f GROUP BY 1 ORDER BY 1")
        show(px.line(t, x="period", y="revenue", markers=len(t) < 40).update_traces(line_color=P["accent"]))
    with R:
        st.markdown("**Revenue by category**")
        cat = q(c, "SELECT category, SUM(sales) revenue FROM f GROUP BY 1")
        show(barh(cat, "revenue", "category"))
    a, b, d = st.columns(3)
    with a:
        st.markdown("**Top 5 products**"); show(barh(q(c, "SELECT product, SUM(sales) revenue FROM f GROUP BY 1 ORDER BY 2 DESC LIMIT 5"), "revenue", "product"))
    with b:
        st.markdown("**Revenue by region**"); show(barh(q(c, "SELECT region, SUM(sales) revenue FROM f GROUP BY 1"), "revenue", "region"))
    with d:
        st.markdown("**Segment contribution**"); show(px.pie(q(c, "SELECT segment, SUM(sales) revenue FROM f GROUP BY 1"), names="segment", values="revenue", hole=.5, color_discrete_sequence=[P["accent"], P["steel"], "#A9B8B0"]))
    st.markdown("**Recent order activity**")
    st.dataframe(q(c, "SELECT order_id, order_date, customer_id, product, quantity, ROUND(sales,2) sales FROM f ORDER BY order_date DESC, order_id DESC LIMIT 10"), hide_index=True, width="stretch")
    top = cat.sort_values("revenue").iloc[-1]; reg = q(c, "SELECT region, SUM(sales) r FROM f GROUP BY 1 ORDER BY 2 DESC").iloc[0]
    dlt = pct(cur["Total Revenue"], prev.get("Total Revenue"))
    cmp_ = (f"Revenue is {abs(dlt):.1f}% {'above' if dlt >= 0 else 'below'} the previous equivalent period." if dlt is not None
            else "No equivalent prior period exists in the data, so no comparison is shown.")
    st.info(f"**Summary:** {money(k.rev)} across {int(k.orders):,} orders. {top.category} is the largest category "
            f"({top.revenue / cat.revenue.sum():.0%} of revenue); {reg.region} leads regions. {cmp_}")

def revenue(c):
    header(2, "Revenue Analysis", "Trends, growth and mix over time.", c)
    f = st.selectbox("Aggregation", list(TRUNC), 2, key="rv_f")
    t = q(c, f"SELECT {TRUNC[f]} period, SUM(sales) revenue, COUNT(DISTINCT order_id) orders FROM f GROUP BY 1 ORDER BY 1")
    if t.empty: st.info("No data for these filters."); return
    t["growth_pct"] = t.revenue.pct_change().replace([np.inf, -np.inf], np.nan) * 100
    t["aov"] = t.revenue / t.orders.replace(0, np.nan)
    a, b = st.columns(2)
    with a: st.markdown("**Revenue growth % (period over period)**"); show(px.bar(t, x="period", y="growth_pct"))
    with b: st.markdown("**Order volume**"); show(px.line(t, x="period", y="orders"))
    a, b = st.columns(2)
    with a: st.markdown("**Average order value**"); show(px.line(t, x="period", y="aov"))
    with b:
        st.markdown("**Revenue by subcategory**")
        show(barh(q(c, "SELECT category||' / '||subcategory sub, SUM(sales) revenue FROM f GROUP BY 1"), "revenue", "sub"))
    st.dataframe(t.round(2), hide_index=True, width="stretch"); export(t, "revenue_trend.csv")

def products(c):
    header(3, "Product Intelligence", "Revenue, volume and profitability by product.", c)
    t = q(c, "SELECT product, category, SUM(quantity) units, SUM(sales) revenue, SUM(profit) profit FROM f GROUP BY 1,2")
    if t.empty: st.info("No data for these filters."); return
    t["margin_pct"] = 100 * t.profit / t.revenue.replace(0, np.nan)
    opts = ["Revenue", "Units"] + (["Profit"] if c["has_profit"] else [])
    m = st.selectbox("Rank by", opts); n = st.slider("Top N", 5, 25, 10)
    col = {"Revenue": "revenue", "Units": "units", "Profit": "profit"}[m]
    a, b = st.columns(2)
    with a: st.markdown(f"**Top {n} by {m.lower()}**"); show(barh(t.nlargest(n, col), col, "product"))
    with b: st.markdown(f"**Bottom {n} by {m.lower()}**"); show(barh(t.nsmallest(n, col), col, "product"))
    st.caption(f"Revenue concentration: top {n} products = {t.nlargest(n, 'revenue').revenue.sum() / t.revenue.sum():.0%} of revenue. "
               "Low rank means low sales, not necessarily unprofitable.")
    s = st.text_input("Search products"); v = t[t["product"].str.contains(s, case=False, na=False)] if s else t
    st.dataframe(v.sort_values("revenue", ascending=False).round(2), hide_index=True, width="stretch"); export(v, "products.csv")
    pr = st.selectbox("Product trend", sorted(t["product"]))
    tr = q(c, "SELECT strftime('%Y-%m',order_date) month, SUM(sales) revenue FROM f WHERE product=? GROUP BY 1 ORDER BY 1", params=c["params"] + [pr])
    show(px.line(tr, x="month", y="revenue"))

def customers(c):
    header(4, "Customer Intelligence", "Value, frequency and RFM segments.", c)
    cu = q(c, "SELECT customer_id, COUNT(DISTINCT order_id) orders, SUM(sales) revenue, MAX(order_date) last_order FROM f GROUP BY 1")
    if cu.empty: st.info("No data for these filters."); return
    for col, (l, v, tp) in zip(st.columns(3), [("Customers", num(len(cu)), "Distinct customer_id"),
            ("Avg revenue / customer", money(cu.revenue.mean()), "Revenue / customers"),
            ("Repeat purchase rate", f"{(cu.orders > 1).mean():.0%}", "Customers with >1 order in window; not retention")]):
        col.markdown(kpi(l, v, None, tp).replace("N/A vs prior period", ""), unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        st.markdown("**Purchase frequency**"); fq = cu.orders.value_counts().sort_index().reset_index(); fq.columns = ["orders", "customers"]
        show(px.bar(fq, x="orders", y="customers"))
    with b:
        st.markdown("**AOV by segment**")
        show(px.bar(q(c, "SELECT segment, SUM(sales)*1.0/COUNT(DISTINCT order_id) aov FROM f GROUP BY 1"), x="segment", y="aov"))
    if len(cu) >= 4:
        asof = pd.to_datetime(c["end"]) + pd.Timedelta(days=1)
        cu["recency_days"] = (asof - pd.to_datetime(cu.last_order)).dt.days
        sc = lambda s, lab: pd.qcut(s.rank(method="first"), 4, labels=lab).astype(int)
        cu["R"], cu["F"], cu["M"] = sc(cu.recency_days, [4, 3, 2, 1]), sc(cu.orders, [1, 2, 3, 4]), sc(cu.revenue, [1, 2, 3, 4])
        cu["rfm_segment"] = np.select([(cu.R >= 3) & (cu.F >= 3), (cu.R <= 2) & (cu.F >= 3), cu.R >= 3], ["Champions", "At risk", "New / recent"], "Hibernating")
        st.markdown(f"**RFM segments** · analysis date {asof.date()} · quartile scores (4 = best); Champions R≥3 & F≥3; At risk R≤2 & F≥3; New/recent R≥3 & F≤2; else Hibernating.")
        show(px.bar(cu.rfm_segment.value_counts().reset_index(), x="rfm_segment", y="count"))
    s = st.text_input("Search customer ID"); v = cu[cu.customer_id.str.contains(s, case=False)] if s else cu
    st.dataframe(v.sort_values("revenue", ascending=False).round(2), hide_index=True, width="stretch"); export(v, "customers.csv")
    st.caption("Customers are identified by ID only; names are not in the schema.")

def regions(c):
    header(5, "Regional Performance", "Regions against the company-wide average.", c)
    t = q(c, "SELECT region, SUM(sales) revenue, COUNT(DISTINCT order_id) orders FROM f GROUP BY 1")
    if t.empty: st.info("No data for these filters."); return
    t["aov"] = t.revenue / t.orders; t["share_pct"] = 100 * t.revenue / t.revenue.sum()
    co = t.revenue.sum() / t.orders.sum(); t["aov_vs_company_pct"] = 100 * (t.aov - co) / co
    t["flag"] = np.where(t.aov_vs_company_pct < -5, "AOV >5% below company", "Within range")
    a, b = st.columns(2)
    with a: st.markdown("**Revenue by region**"); show(barh(t, "revenue", "region"))
    with b:
        st.markdown("**Category mix (% of region revenue)**")
        show(px.bar(q(c, "SELECT region, category, SUM(sales) revenue FROM f GROUP BY 1,2"), x="region", y="revenue", color="category", color_discrete_sequence=[P["accent"], P["steel"], "#A9B8B0"]).update_layout(barmode="relative", barnorm="percent"))
    st.dataframe(t.sort_values("revenue", ascending=False).round(2), hide_index=True, width="stretch"); export(t, "regions.csv")
    st.caption(f"Rule: a region is flagged when its AOV is more than 5% below the company AOV ({money(co)}).")

def explorer(c):
    header(6, "SQL Explorer", "Predefined, read-only queries executed against SQLite.", c)
    Q = load_queries(); g = st.selectbox("Category", list(dict.fromkeys(x["group"] for x in Q)))
    x = st.selectbox("Query", [y for y in Q if y["group"] == g], format_func=lambda y: y["name"])
    st.markdown(f"**Business question:** {x['question']}  \n**Technique:** `{x['technique']}`  \n**Reading:** {x['reading']}")
    st.code(x["sql"], "sql")
    st.caption("`f` = sales filtered by the sidebar (date range, category, region) via bound parameters. Only whitelisted queries run; the connection is read-only.")
    if st.button("Execute query"):
        t0 = time.perf_counter(); df = q(c, x["sql"]); ms = (time.perf_counter() - t0) * 1000
        st.success(f"{len(df):,} rows · {ms:.1f} ms"); st.dataframe(df, hide_index=True, width="stretch"); export(df, "query_result.csv")

def quality(c):
    header(7, "Data Quality", "Checks run on the full table, ignoring sidebar filters.", c)
    allw = ("1=1", [])
    checks = [("Total rows", "SELECT COUNT(*) n FROM f", None, "Rows loaded.", "None"),
      ("Duplicate line groups", "SELECT COUNT(*) n FROM (SELECT 1 FROM f GROUP BY order_id,product,order_date,customer_id,quantity,sales HAVING COUNT(*)>1)", "Medium", "Identical lines; may be legitimate repeats.", "Confirm with source"),
      ("Missing key fields", "SELECT COUNT(*) n FROM f WHERE order_id IS NULL OR customer_id IS NULL OR product IS NULL OR category IS NULL OR region IS NULL OR sales IS NULL", "High", "Nulls in key columns.", "Fix upstream"),
      ("Invalid quantity", "SELECT COUNT(*) n FROM f WHERE quantity IS NULL OR quantity<=0", "Medium", "Quantity missing or ≤ 0.", "Check for returns"),
      ("Invalid date", "SELECT COUNT(*) n FROM f WHERE order_date IS NULL", "High", "Unparseable dates; excluded from date-filtered views.", "Repair dates"),
      ("Zero/negative sales", "SELECT COUNT(*) n FROM f WHERE sales<=0", "Low", "May be returns or credits; kept in totals.", "Review, do not auto-delete"),
      ("Category spelling variants", "SELECT COUNT(DISTINCT category)-COUNT(DISTINCT LOWER(TRIM(category))) n FROM f", "Medium", "Same category differing by case/whitespace.", "Standardise labels")]
    rows = []
    for name, sql, sev, d, act in checks:
        n = int(run(c["conn"], sql, *allw).n[0]); rows.append((name, n, "—" if name == "Total rows" or n == 0 else sev, d, act))
    df = pd.DataFrame(rows, columns=["check", "records_affected", "severity", "description", "recommended_action"])
    st.dataframe(df, hide_index=True, width="stretch"); export(df, "data_quality.csv")
    st.caption("Results are detected issues, not confirmed errors. Records are never removed automatically.")

def methodology(c):
    header(8, "Methodology", "Definitions, schema, limitations and data-driven insights.", c)
    st.markdown(f"**Data source:** {c['source']}. The bundled demo set is synthetic (seeded random generation), so findings below describe it, not a real business.")
    st.code("sales(order_id, order_date, customer_id, segment, region, category, subcategory, product, quantity, sales, profit)", "sql")
    st.markdown("**KPIs:** Revenue = SUM(sales); Orders = distinct order_id; AOV = revenue ÷ orders; Repeat rate = customers with >1 order in window ÷ customers (not retention). Prior period = equal-length window immediately before the selection; shown only if fully inside the data.")
    st.markdown("**Limitations:** single flat table (no refunds/discount fields); filters apply to every page except Data Quality.")
    st.subheader("Insights (computed from current filters)")
    cat = q(c, "SELECT category, SUM(sales) r FROM f GROUP BY 1 ORDER BY 2 DESC"); cu = q(c, "SELECT COUNT(DISTINCT order_id) o FROM f GROUP BY customer_id")
    rg = q(c, "SELECT region, SUM(sales)*1.0/COUNT(DISTINCT order_id) aov FROM f GROUP BY 1 ORDER BY 2")
    if cat.empty: st.info("No data for these filters."); return
    s = cat.r.iloc[0] / cat.r.sum()
    st.markdown(f"**1. Category concentration.** Observation: {cat.category.iloc[0]} leads. Evidence: {s:.0%} of revenue. Interpretation: {'revenue depends heavily on one category' if s > .4 else 'revenue is spread across categories'}. Action: {'monitor supply and pricing risk there' if s > .4 else 'review lower categories for growth'}.")
    st.markdown(f"**2. Repeat purchasing.** Observation: {(cu.o > 1).mean():.0%} of customers ordered more than once. Evidence: customer order counts in window. Interpretation: window-limited repeat rate, not retention. Action: compare against a longer window before setting targets.")
    st.markdown(f"**3. Regional AOV.** Observation: {rg.region.iloc[0]} has the lowest AOV (${rg.aov.iloc[0]:,.0f}) vs {rg.region.iloc[-1]} (${rg.aov.iloc[-1]:,.0f}). Evidence: SUM(sales) ÷ distinct orders. Interpretation: descriptive gap only; no significance test was run. Action: check mix and order counts before intervening.")

PAGES = {"Overview": overview, "Revenue Analysis": revenue, "Product Intelligence": products,
         "Customer Intelligence": customers, "Regional Performance": regions, "SQL Explorer": explorer,
         "Data Quality": quality, "Methodology": methodology}
