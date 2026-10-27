"""
Page 7: Methodology and Business Insights
Documentation of analytical methodology and business findings.
"""

import streamlit as st
import pandas as pd

from config import COLORS, APP_NAME, APP_SUBTITLE, DATASET_NAME, DATASET_SOURCE, DATASET_ROWS
from utils.styling import render_section_header, render_empty_state
from utils.database import execute_query_df, is_database_ready
from utils.metrics import format_currency, format_number

st.markdown("<div style='margin-top:-2rem;'></div>", unsafe_allow_html=True)
render_section_header("Methodology")

# ── Dataset Info ──
st.markdown("<h3>Dataset</h3>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="background-color:#FFFFFF;border:1px solid #D9DDD7;padding:1rem 1.25rem;font-size:0.9rem;line-height:1.7;">
    <table style="width:100%;border-collapse:collapse;">
        <tr><td style="padding:0.35rem 0.5rem;font-weight:500;color:#191B1A;width:180px;">Dataset Name</td>
            <td style="padding:0.35rem 0.5rem;color:#6B706D;">{DATASET_NAME}</td></tr>
        <tr><td style="padding:0.35rem 0.5rem;font-weight:500;color:#191B1A;">Source</td>
            <td style="padding:0.35rem 0.5rem;color:#6B706D;">{DATASET_SOURCE}</td></tr>
        <tr><td style="padding:0.35rem 0.5rem;font-weight:500;color:#191B1A;">Approximate Rows</td>
            <td style="padding:0.35rem 0.5rem;color:#6B706D;">{format_number(DATASET_ROWS)} order line items</td></tr>
        <tr><td style="padding:0.35rem 0.5rem;font-weight:500;color:#191B1A;">Period</td>
            <td style="padding:0.35rem 0.5rem;color:#6B706D;">January 2020 — December 2024</td></tr>
        <tr><td style="padding:0.35rem 0.5rem;font-weight:500;color:#191B1A;">License</td>
            <td style="padding:0.35rem 0.5rem;color:#6B706D;">Open for demonstration and educational use</td></tr>
    </table>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Database Schema ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
st.markdown("<h3>Database Schema</h3>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="background-color:#FFFFFF;border:1px solid #D9DDD7;padding:1rem 1.25rem;font-family:'Cascadia Code','Consolas',monospace;font-size:0.8rem;line-height:1.7;">
    <strong style="color:#285C48;">customers</strong> (dimension)<br>
    &nbsp;&nbsp;customer_id (PK), customer_name, segment, country, region, state, city, postal_code<br><br>
    <strong style="color:#285C48;">products</strong> (dimension)<br>
    &nbsp;&nbsp;product_id (PK), product_name, category, subcategory<br><br>
    <strong style="color:#285C48;">orders</strong> (fact table)<br>
    &nbsp;&nbsp;order_id, order_date, ship_date, ship_mode, customer_id (FK), product_id (FK),<br>
    &nbsp;&nbsp;sales, quantity, discount, profit<br><br>
    <span style="color:#6B706D;">-- Star schema: orders as central fact table with customer and product dimensions</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── KPI Definitions ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
st.markdown("<h3>KPI Definitions</h3>", unsafe_allow_html=True)

kpi_defs = [
    ("Total Revenue", "SUM(sales) across all order line items. Sales is calculated as quantity × unit price × (1 - discount)."),
    ("Total Orders", "COUNT(DISTINCT order_id). Each order may contain multiple line items."),
    ("Units Sold", "SUM(quantity). Total number of individual items sold."),
    ("Average Order Value (AOV)", "SUM(sales) / COUNT(DISTINCT order_id). Average revenue per unique order."),
    ("Unique Customers", "COUNT(DISTINCT customer_id). Distinct customer accounts with at least one order."),
    ("Total Profit", "SUM(profit). Total profit across all orders. Profit is calculated as (sales - cost)."),
    ("Profit Margin", "(SUM(profit) / SUM(sales)) × 100. Percentage of revenue retained as profit."),
    ("Revenue Growth", "((current_period_revenue - previous_period_revenue) / previous_period_revenue) × 100."),
    ("Repeat Purchase Rate", "Customers with more than 1 order / total customers × 100."),
    ("Revenue per Customer", "SUM(sales) / COUNT(DISTINCT customer_id). Average revenue per customer."),
    ("RFM Score", "Customer segmentation using Recency (days since last purchase), Frequency (order count), Monetary (total spend). Quartile-based scoring (1-4)."),
]

kpi_df = pd.DataFrame(kpi_defs, columns=["KPI", "Definition"])
st.dataframe(kpi_df, use_container_width=True, hide_index=True)

# ── SQL Techniques ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
st.markdown("<h3>SQL Techniques Demonstrated</h3>", unsafe_allow_html=True)

techniques = [
    ("Basic Queries", "SELECT, WHERE, ORDER BY, LIMIT — foundational data retrieval"),
    ("Aggregations", "GROUP BY with SUM, COUNT, AVG, MIN, MAX — summarization"),
    ("Joins", "INNER JOIN connecting orders → customers and orders → products via foreign keys"),
    ("Date Functions", "STRFTIME, JULIANDAY, date arithmetic for period analysis"),
    ("Window Functions", "ROW_NUMBER, RANK, LAG, NTILE, SUM() OVER for rankings, growth, and running totals"),
    ("Common Table Expressions (CTEs)", "WITH clause for multi-step queries and readability"),
    ("Subqueries", "Nested SELECTs for comparative analysis"),
    ("Conditional Aggregation", "CASE expressions within aggregation functions"),
    ("Data Quality", "Validation queries, referential integrity checks"),
    ("RFM Analysis", "Quartile-based customer segmentation"),
]

tech_df = pd.DataFrame(techniques, columns=["Technique", "Application"])
st.dataframe(tech_df, use_container_width=True, hide_index=True)

# ── Assumptions & Limitations ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
st.markdown("<h3>Assumptions &amp; Limitations</h3>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="background-color:#FFFFFF;border:1px solid #D9DDD7;padding:1rem 1.25rem;font-size:0.9rem;line-height:1.7;">
    <ul>
        <li><strong>Synthetic data:</strong> The dataset is synthetically generated for demonstration. Patterns and relationships may not reflect real-world business dynamics.</li>
        <li><strong>Revenue definition:</strong> Revenue is calculated as sales amount before adjustments. Returns and credits are included as negative values.</li>
        <li><strong>No cost data:</strong> Profit margins are calculated from generated profit values, which may not reflect actual cost structures.</li>
        <li><strong>Time period:</strong> Analysis covers 2020-2024. Seasonal patterns may be influenced by the synthetic generation process.</li>
        <li><strong>Customer data:</strong> Customer names are randomly generated. No real personally identifiable information is used.</li>
        <li><strong>Geographic scope:</strong> Data is limited to US regions. International sales are not represented.</li>
        <li><strong>RFM interpretation:</strong> Segments are based on relative quartile rankings within the dataset and should be validated against business context.</li>
        <li><strong>No causal inference:</strong> Correlations observed in the data do not imply causation.</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Business Insights ──
if is_database_ready():
    st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
    st.markdown("<h3>Business Findings</h3>", unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:0.85rem;color:#6B706D;">Key observations from the data, structured as: '
        "<strong>Observation → Evidence → Interpretation → Recommendation</strong></p>",
        unsafe_allow_html=True,
    )

    # Generate insights from actual data
    try:
        # Insight 1: Top category
        df_cat = execute_query_df(
            "SELECT category, ROUND(SUM(sales),2) as rev, ROUND(100.0*SUM(sales)/(SELECT SUM(sales) FROM orders),1) as share FROM orders o JOIN products p ON o.product_id=p.product_id GROUP BY category ORDER BY rev DESC LIMIT 1"
        )
        # Insight 2: Segment contribution
        df_seg = execute_query_df(
            "SELECT segment, ROUND(SUM(sales),2) as rev, COUNT(DISTINCT c.customer_id) as custs FROM orders o JOIN customers c ON o.customer_id=c.customer_id GROUP BY segment ORDER BY rev DESC"
        )
        # Insight 3: Repeat purchase
        df_repeat = execute_query_df(
            "WITH co AS (SELECT customer_id, COUNT(DISTINCT order_id) as cnt FROM orders GROUP BY customer_id) SELECT ROUND(100.0*SUM(CASE WHEN cnt>1 THEN 1 END)/COUNT(*),1) as rate FROM co"
        )
        # Insight 4: Regional performance
        df_region = execute_query_df(
            "SELECT c.region, ROUND(SUM(sales),2) as rev FROM orders o JOIN customers c ON o.customer_id=c.customer_id GROUP BY c.region ORDER BY rev DESC"
        )
        # Insight 5: Product concentration
        df_conc = execute_query_df(
            "SELECT ROUND(100.0*SUM(top_rev)/total_rev,1) as conc FROM (SELECT SUM(sales) as top_rev FROM (SELECT SUM(sales) as sales FROM orders GROUP BY product_id ORDER BY sales DESC LIMIT 50)), (SELECT SUM(sales) as total_rev FROM orders) WHERE total_rev > 0"
        )
        # Insight 6: Discount impact
        df_disc = execute_query_df(
            "SELECT CASE WHEN discount>0 THEN 'Discounted' ELSE 'Full Price' END as type, ROUND(AVG(sales),2) as avg_sale, ROUND(AVG(profit),2) as avg_profit, COUNT(*) as cnt FROM orders GROUP BY type"
        )
    except Exception:
        pass

    insights = []

    # Build insights from data if available
    if not df_cat.empty and df_cat["rev"].iloc[0] > 0:
        cat_name = df_cat["category"].iloc[0]
        cat_rev = df_cat["rev"].iloc[0]
        cat_share = df_cat["share"].iloc[0]
        insights.append({
            "Observation": f"{cat_name} leads revenue generation",
            "Evidence": f"The {cat_name} category generates ${cat_rev:,.0f} in revenue, representing {cat_share}% of total sales.",
            "Interpretation": f"{cat_name} products are the primary revenue driver. Investment in this category yields the highest return.",
            "Action": "Continue to prioritize {cat_name} inventory and marketing. Explore cross-selling opportunities with lower-performing categories.".format(cat_name=cat_name),
        })

    if not df_seg.empty:
        top_seg = df_seg.iloc[0]
        seg_name = top_seg["segment"]
        seg_rev = top_seg["rev"]
        insights.append({
            "Observation": f"{seg_name} segment generates highest revenue",
            "Evidence": f"The {seg_name} customer segment accounts for ${seg_rev:,.0f} in total revenue.",
            "Interpretation": f"Understanding the {seg_name} segment's preferences and purchasing patterns can inform targeted marketing strategies.",
            "Action": "Develop segment-specific promotions and product bundles for the {seg_name} segment.".format(seg_name=seg_name),
        })

    repeat_rate = df_repeat["rate"].iloc[0] if not df_repeat.empty else 0
    if repeat_rate > 0:
        insights.append({
            "Observation": f"Customer retention rate is {repeat_rate}%",
            "Evidence": f"{repeat_rate}% of customers have made more than one purchase.",
            "Interpretation": "A significant portion of revenue comes from repeat customers, indicating brand loyalty.",
            "Action": "Implement a loyalty program to further increase repeat purchase rates and customer lifetime value.",
        })

    if not df_region.empty:
        top_region = df_region.iloc[0]
        bot_region = df_region.iloc[-1]
        insights.append({
            "Observation": f"{top_region['region']} outperforms other regions",
            "Evidence": f"{top_region['region']} leads with ${top_region['rev']:,.0f} in revenue. {bot_region['region']} trails at ${bot_region['rev']:,.0f}.",
            "Interpretation": "Regional performance disparities indicate uneven market penetration or varying demand patterns.",
            "Action": "Investigate {bot_region} market conditions and develop targeted growth strategies.".format(bot_region=bot_region["region"]),
        })

    if not df_conc.empty:
        conc = df_conc["conc"].iloc[0]
        insights.append({
            "Observation": f"Top 50 products drive {conc}% of revenue",
            "Evidence": f"The highest-revenue 50 products account for {conc}% of total sales.",
            "Interpretation": "Revenue is concentrated among a relatively small number of products, creating both opportunity and risk.",
            "Action": "Ensure consistent availability of top products. Develop strategies to grow mid-tier products into top performers.",
        })

    if not df_disc.empty and len(df_disc) >= 2:
        full_row = df_disc[df_disc["type"] == "Full Price"]
        disc_row = df_disc[df_disc["type"] == "Discounted"]
        if not full_row.empty and not disc_row.empty:
            full_avg = full_row["avg_sale"].iloc[0]
            disc_avg = disc_row["avg_sale"].iloc[0]
            full_profit = full_row["avg_profit"].iloc[0]
            disc_profit = disc_row["avg_profit"].iloc[0]
            insights.append({
                "Observation": "Discounted items show different profitability",
                "Evidence": f"Full-price items average ${full_avg:,.2f} per sale (profit: ${full_profit:,.2f}) vs. discounted at ${disc_avg:,.2f} (profit: ${disc_profit:,.2f}).",
                "Interpretation": "Discounting drives volume but reduces per-unit margins. The net effect on overall profitability depends on volume elasticity.",
                "Action": "Analyze discount elasticity to optimize promotional pricing. Avoid excessive discounts that erode profitability.",
            })

    for i, insight in enumerate(insights):
        with st.expander(f"{i+1}. {insight['Observation']}", expanded=i == 0):
            st.markdown(
                f"""
                <div style="padding:0.5rem 0;">
                    <p><strong style="color:#285C48;">Observation:</strong> {insight['Observation']}</p>
                    <p><strong style="color:#285C48;">Evidence:</strong> {insight['Evidence']}</p>
                    <p><strong style="color:#285C48;">Interpretation:</strong> {insight['Interpretation']}</p>
                    <p><strong style="color:#285C48;">Recommended Action:</strong> {insight['Action']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if not insights:
        st.info("Business insights will be generated once the database is populated.")

# ── Future Improvements ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
st.markdown("<h3>Future Improvements</h3>", unsafe_allow_html=True)
st.markdown(
    """
    <ul style="color:#6B706D;line-height:1.8;">
        <li><strong>Real-time data:</strong> Connect to live data sources via API or database connection.</li>
        <li><strong>Forecasting:</strong> Add predictive analytics using time-series forecasting models.</li>
        <li><strong>Anomaly detection:</strong> Automatically flag unusual patterns in sales, orders, or customer behavior.</li>
        <li><strong>Custom SQL:</strong> Enable user-defined SQL queries with read-only sandboxing.</li>
        <li><strong>User authentication:</strong> Multi-user support with role-based access control.</li>
        <li><strong>Report scheduling:</strong> Automated report generation and email distribution.</li>
        <li><strong>Geographic mapping:</strong> Interactive map visualization for regional analysis.</li>
        <li><strong>Data refresh:</strong> Automatic data refresh with change tracking and versioning.</li>
    </ul>
    """,
    unsafe_allow_html=True,
)