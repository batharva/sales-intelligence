"""
Page 5: SQL Explorer
Interactive exploration of analytical SQL queries behind the dashboard.
"""

import streamlit as st
import pandas as pd
import time
import html

from config import COLORS
from utils.styling import render_section_header, render_empty_state
from utils.database import execute_query, execute_query_df, is_database_ready
from utils.queries import load_all_queries

st.markdown("<div style='margin-top:-2rem;'></div>", unsafe_allow_html=True)
render_section_header("SQL Explorer")

st.markdown(
    '<p style="font-size:0.85rem;color:#6B706D;">'
    "Browse and execute the analytical SQL queries that power this dashboard. "
    "Each query is a predefined, read-only operation against the sales database."
    "</p>",
    unsafe_allow_html=True,
)

if not is_database_ready():
    render_empty_state("Database is not available. Please seed the database first.")
    st.stop()

# Load queries
all_queries = load_all_queries()

if not all_queries:
    render_empty_state("No SQL query files found in the sql/ directory.")
    st.stop()

# ── Query Browser ──
categories = list(all_queries.keys())

c1, c2 = st.columns([1, 2])

with c1:
    st.markdown("<h4>Query Library</h4>", unsafe_allow_html=True)

    # Category selector
    category_names = [
        "Basic Queries", "Aggregations & Grouping", "Joins",
        "Date Analysis", "Product Analysis", "Customer Analysis",
        "Window Functions", "CTEs & Advanced", "Data Quality",
    ]

    selected_category = st.selectbox(
        "Category",
        categories,
        format_func=lambda x: x,
        key="sql_cat",
        label_visibility="collapsed",
    )

    if selected_category and selected_category in all_queries:
        queries = all_queries[selected_category]
        query_names = [q.name for q in queries]
        selected_query_name = st.selectbox(
            "Query",
            query_names,
            key="sql_query",
            label_visibility="collapsed",
        )

        # Find selected query
        selected_query = None
        for q in queries:
            if q.name == selected_query_name:
                selected_query = q
                break

        if selected_query:
            st.markdown(
                f'<div style="font-size:0.75rem;color:#637D8A;margin-top:0.5rem;">'
                f'<strong>Technique:</strong> {selected_query.technique or "N/A"}'
                f'</div>',
                unsafe_allow_html=True,
            )
            if selected_query.description:
                st.markdown(
                    f'<div style="font-size:0.75rem;color:#6B706D;margin-top:0.25rem;">'
                    f'<strong>Business Question:</strong> {selected_query.description}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

with c2:
    if selected_query:
        st.markdown("<h4>SQL Query</h4>", unsafe_allow_html=True)

        # Execute button
        execute_col, status_col = st.columns([1, 3])
        with execute_col:
            run_clicked = st.button("▶ Execute Query", key="sql_execute")
        with status_col:
            status_placeholder = st.empty()

        # SQL code display with syntax coloring
        sql_display = selected_query.sql

        # Basic syntax highlighting
        highlighted_sql = html.escape(sql_display)
        # Simple SQL keyword highlighting via HTML replace
        keywords = [
            "SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING", "LIMIT",
            "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "ON",
            "AS", "AND", "OR", "NOT", "IN", "BETWEEN", "LIKE",
            "SUM", "COUNT", "AVG", "MIN", "MAX", "ROUND", "COALESCE", "NULLIF",
            "CASE", "WHEN", "THEN", "ELSE", "END",
            "OVER", "PARTITION BY", "ROW_NUMBER", "RANK", "LAG", "NTILE",
            "WITH", "RECURSIVE",
            "DISTINCT", "UNION ALL", "EXISTS",
            "CAST", "STRFTIME", "JULIANDAY", "DATE",
            "ASC", "DESC",
        ]
        for kw in keywords:
            highlighted_sql = highlighted_sql.replace(
                kw, f'<span style="color:#569CD6;font-weight:500;">{kw}</span>'
            )
        # Highlight strings
        import re as re_mod
        highlighted_sql = re_mod.sub(
            r"'([^']*)'",
            r"<span style='color:#CE9178;'>'\1'</span>",
            highlighted_sql,
        )
        # Highlight numbers
        highlighted_sql = re_mod.sub(
            r"\b(\d+\.?\d*)\b",
            r"<span style='color:#B5CEA8;'>\1</span>",
            highlighted_sql,
        )

        st.markdown(
            f'<pre style="background-color:#1E1E1E;color:#D4D4D4;font-family:\'Cascadia Code\',\'Fira Code\',\'Consolas\',monospace;font-size:0.8rem;padding:1rem;overflow-x:auto;line-height:1.6;border-radius:0;max-height:400px;overflow-y:auto;">{highlighted_sql}</pre>',
            unsafe_allow_html=True,
        )

        # Copy button
        st.button(
            "📋 Copy SQL",
            key="sql_copy",
            on_click=lambda: st.write(
                f'<script>navigator.clipboard.writeText({repr(sql_display)});</script>',
                unsafe_allow_html=True,
            ),
            help="Copy the SQL query to clipboard",
        )

        # Execute
        if run_clicked:
            try:
                with status_placeholder.status("Executing query...", expanded=False) as s:
                    start_t = time.time()
                    rows, columns, row_count, elapsed_ms = execute_query(sql_display)
                    s.update(state="complete")

                df_result = pd.DataFrame([dict(row) for row in rows]) if rows else pd.DataFrame()

                status_placeholder.markdown(
                    f'<div style="font-size:0.75rem;color:#2E7D5E;">'
                    f"✓ Executed successfully &mdash; {row_count} rows returned in {elapsed_ms}ms"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                if not df_result.empty:
                    st.markdown("<h4>Results</h4>", unsafe_allow_html=True)
                    st.dataframe(df_result, use_container_width=True, hide_index=True)

                    csv = df_result.to_csv(index=False)
                    st.download_button(
                        label="Download Results (CSV)",
                        data=csv,
                        file_name="query_results.csv",
                        mime="text/csv",
                    )
                else:
                    st.info("Query executed successfully but returned no rows.")

            except ValueError as e:
                status_placeholder.markdown(
                    f'<div style="font-size:0.75rem;color:#A0504A;">✗ {str(e)}</div>',
                    unsafe_allow_html=True,
                )
            except Exception as e:
                status_placeholder.markdown(
                    f'<div style="font-size:0.75rem;color:#A0504A;">✗ Error: {str(e)}</div>',
                    unsafe_allow_html=True,
                )

# ── Explanation Section ──
if selected_query:
    st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
    st.markdown("<h4>Business Interpretation</h4>", unsafe_allow_html=True)

    interpretation = f"""
    This query demonstrates **{selected_query.technique or 'analytical SQL'}** techniques.
    It helps answer the question: *{selected_query.description or 'What does this data reveal?'}*
    
    **How to use this analysis:**
    - The results can be filtered using the sidebar controls
    - Data can be exported as CSV for further analysis
    - The query structure can be adapted to answer similar business questions
    """
    st.markdown(interpretation)

    with st.expander("Explanation of SQL Techniques"):
        technique_explanations = {
            "aggregation": "GROUP BY aggregates data into summary rows. SUM, COUNT, AVG compute metrics per group.",
            "window function": "Window functions (OVER, PARTITION BY) compute values across rows related to the current row without collapsing them.",
            "join": "JOINs combine data from multiple tables using related keys (foreign keys).",
            "cte": "Common Table Expressions (WITH clause) create temporary named result sets for complex multi-step queries.",
            "subquery": "Subqueries embed one SELECT inside another, used for comparisons or filtering against aggregated values.",
            "date": "Date functions extract date parts, calculate differences, and enable time-based analysis.",
            "conditional": "CASE expressions implement conditional logic inside SQL queries for custom groupings and flags.",
        }
        for key, explanation in technique_explanations.items():
            st.markdown(f"- **{key.title()}**: {explanation}")

# ── Query Library Reference ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
with st.expander("Query Library Reference"):
    st.markdown(
        """
        | Category | Techniques Used | Business Questions Answered |
        |---|---|---|
        | Data Quality | Data profiling, validation | Are there duplicates, missing values, or referential issues? |
        | Overview | Aggregation, date filtering | What are the top-level business KPIs? |
        | Revenue Analysis | Date aggregation, window functions | How is revenue trending and what drives it? |
        | Product Analysis | Ranking, window functions, concentration | Which products perform best and why? |
        | Customer Analysis | RFM, segmentation, frequency analysis | Who are our customers and how do they behave? |
        | Regional Analysis | Grouped aggregation, comparative analysis | How does performance vary by region? |
        | Advanced Analysis | CTEs, window functions, conditional aggregation | Complex analytical patterns and insights |
        """,
        unsafe_allow_html=True,
    )

# ── Safety Notice ──
st.markdown('<hr class="thin-divider" />', unsafe_allow_html=True)
st.markdown(
    '<p style="font-size:0.7rem;color:#6B706D;">'
    "🔒 This SQL Explorer uses a whitelist of predefined, read-only analytical queries. "
    "Custom SQL input is not supported in the deployed version. "
    "All queries are executed against a local SQLite database with no write capability."
    "</p>",
    unsafe_allow_html=True,
)