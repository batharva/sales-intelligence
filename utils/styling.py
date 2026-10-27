"""
Utility functions for CSS styling and UI components.
Provides the industrial-minimal theme across the application.
"""

import streamlit as st
from config import COLORS


def load_css() -> str:
    """Return the custom CSS string for the industrial-minimal theme."""
    return f"""
    <style>
        /* ── Base ─────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}

        .stApp {{
            background-color: {COLORS['background']};
        }}

        .main .block-container {{
            padding: 1.5rem 2rem 2rem 2rem;
            max-width: 1400px;
        }}

        /* ── Typography ───────────────────────────────────── */
        h1, h2, h3, h4, h5, h6 {{
            color: {COLORS['text_primary']};
            font-weight: 600;
            letter-spacing: -0.01em;
        }}

        h1 {{
            font-size: 1.75rem;
            margin-bottom: 0.25rem;
        }}

        h2 {{
            font-size: 1.25rem;
            font-weight: 500;
        }}

        h3 {{
            font-size: 1.1rem;
            font-weight: 500;
        }}

        p {{
            color: {COLORS['text_secondary']};
            font-size: 0.9rem;
        }}

        /* ── Sidebar ──────────────────────────────────────── */
        section[data-testid="stSidebar"] {{
            background-color: {COLORS['surface']};
            border-right: 1px solid {COLORS['border']};
            padding: 0;
        }}

        section[data-testid="stSidebar"] .block-container {{
            padding: 1.5rem 1rem;
        }}

        .sidebar-logo {{
            font-size: 1.1rem;
            font-weight: 700;
            color: {COLORS['text_primary']};
            letter-spacing: 0.02em;
            margin-bottom: 0.1rem;
        }}

        .sidebar-subtitle {{
            font-size: 0.7rem;
            font-weight: 500;
            color: {COLORS['accent_primary']};
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 1.5rem;
        }}

        .sidebar-divider {{
            border: none;
            border-top: 1px solid {COLORS['border']};
            margin: 0.75rem 0;
        }}

        .sidebar-footer {{
            font-size: 0.65rem;
            color: {COLORS['text_secondary']};
            text-align: left;
            padding-top: 0.75rem;
            border-top: 1px solid {COLORS['border']};
        }}

        /* Navigation radio buttons */
        div[data-testid="stRadio"] > label {{
            font-size: 0.85rem;
            font-weight: 500;
            color: {COLORS['text_secondary']};
        }}

        div[data-testid="stRadio"] > div {{
            gap: 0.15rem;
        }}

        div[data-testid="stRadio"] div[role="radiogroup"] > label {{
            background-color: transparent;
            border: none;
            border-radius: 0;
            padding: 0.35rem 0.5rem;
            transition: background-color 0.15s;
        }}

        div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {{
            background-color: {COLORS['background']};
        }}

        div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {{
            background-color: {COLORS['background']};
            border-left: 3px solid {COLORS['accent_primary']};
        }}

        /* ── Header ───────────────────────────────────────── */
        .section-header {{
            font-size: 0.7rem;
            font-weight: 600;
            color: {COLORS['accent_secondary']};
            letter-spacing: 0.15em;
            text-transform: uppercase;
            margin-bottom: 0.1rem;
        }}

        .page-title {{
            font-size: 1.75rem;
            font-weight: 700;
            color: {COLORS['text_primary']};
            margin: 0 0 0.15rem 0;
            line-height: 1.2;
        }}

        .page-description {{
            font-size: 0.9rem;
            color: {COLORS['text_secondary']};
            margin-bottom: 0.5rem;
        }}

        .header-meta {{
            font-size: 0.75rem;
            color: {COLORS['text_secondary']};
            margin: 0.25rem 0;
        }}

        .header-divider {{
            border: none;
            border-top: 1px solid {COLORS['border']};
            margin: 0.75rem 0 1.25rem 0;
        }}

        /* ── KPI Cards ────────────────────────────────────── */
        .kpi-container {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            padding: 0.9rem 1rem;
            margin-bottom: 0.75rem;
        }}

        .kpi-label {{
            font-size: 0.65rem;
            font-weight: 600;
            color: {COLORS['text_secondary']};
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin: 0;
        }}

        .kpi-value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: {COLORS['text_primary']};
            margin: 0.1rem 0;
            line-height: 1.2;
        }}

        .kpi-delta {{
            font-size: 0.75rem;
            font-weight: 500;
            margin: 0;
        }}

        .kpi-delta.positive {{
            color: {COLORS['positive']};
        }}

        .kpi-delta.negative {{
            color: {COLORS['negative']};
        }}

        .kpi-delta.neutral {{
            color: {COLORS['text_secondary']};
        }}

        /* ── Charts ───────────────────────────────────────── */
        .stPlotlyChart {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            padding: 0.75rem;
        }}

        /* ── DataFrames ───────────────────────────────────── */
        div[data-testid="stDataFrame"] {{
            border: 1px solid {COLORS['border']};
        }}

        div[data-testid="stDataFrame"] table {{
            font-size: 0.8rem;
        }}

        div[data-testid="stDataFrame"] th {{
            background-color: {COLORS['background']};
            color: {COLORS['text_primary']};
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            border-bottom: 2px solid {COLORS['border']};
        }}

        div[data-testid="stDataFrame"] td {{
            border-bottom: 1px solid {COLORS['border']};
        }}

        /* ── Expander ─────────────────────────────────────── */
        div[data-testid="stExpander"] {{
            border: 1px solid {COLORS['border']};
            border-radius: 0;
        }}

        div[data-testid="stExpander"] summary {{
            font-weight: 500;
            font-size: 0.85rem;
        }}

        /* ── Form elements ────────────────────────────────── */
        .stSelectbox, .stMultiSelect, .stDateInput, .stSlider {{
            font-size: 0.85rem;
        }}

        div[data-baseweb="select"] > div {{
            border: 1px solid {COLORS['border']};
            border-radius: 0;
        }}

        div[data-baseweb="select"] > div:hover {{
            border-color: {COLORS['accent_primary']};
        }}

        /* ── Buttons ──────────────────────────────────────── */
        .stButton button {{
            border: 1px solid {COLORS['border']};
            border-radius: 0;
            background-color: {COLORS['surface']};
            color: {COLORS['text_primary']};
            font-size: 0.8rem;
            font-weight: 500;
            padding: 0.35rem 0.9rem;
            transition: all 0.15s;
        }}

        .stButton button:hover {{
            border-color: {COLORS['accent_primary']};
            background-color: {COLORS['background']};
        }}

        .stButton button:active {{
            background-color: {COLORS['accent_primary']};
            color: white;
        }}

        /* ── Download button ──────────────────────────────── */
        .stDownloadButton button {{
            border: 1px solid {COLORS['accent_primary']};
            border-radius: 0;
            background-color: transparent;
            color: {COLORS['accent_primary']};
            font-size: 0.8rem;
            font-weight: 500;
            padding: 0.3rem 0.8rem;
        }}

        .stDownloadButton button:hover {{
            background-color: {COLORS['accent_primary']};
            color: white;
        }}

        /* ── SQL Code block ───────────────────────────────── */
        .sql-code {{
            background-color: #1E1E1E;
            color: #D4D4D4;
            font-family: 'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
            font-size: 0.8rem;
            padding: 1rem;
            border-radius: 0;
            overflow-x: auto;
            line-height: 1.5;
            white-space: pre-wrap;
            word-break: break-word;
        }}

        .sql-code .keyword {{ color: #569CD6; }}
        .sql-code .function {{ color: #DCDCAA; }}
        .sql-code .string {{ color: #CE9178; }}
        .sql-code .number {{ color: #B5CEA8; }}
        .sql-code .comment {{ color: #6A9955; font-style: italic; }}
        .sql-code .operator {{ color: #D4D4D4; }}

        /* ── Status indicators ────────────────────────────── */
        .status-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 6px;
        }}

        .status-active {{ background-color: {COLORS['positive']}; }}
        .status-inactive {{ background-color: {COLORS['negative']}; }}

        /* ── Empty state ──────────────────────────────────── */
        .empty-state {{
            text-align: center;
            padding: 2rem;
            color: {COLORS['text_secondary']};
            border: 1px dashed {COLORS['border']};
            margin: 1rem 0;
        }}

        .empty-state p {{
            font-size: 0.9rem;
            margin: 0.25rem 0;
        }}

        /* ── Utility ──────────────────────────────────────── */
        .text-muted {{
            color: {COLORS['text_secondary']};
            font-size: 0.75rem;
        }}

        .text-monospace {{
            font-family: 'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
            font-size: 0.8rem;
        }}

        .thin-divider {{
            border: none;
            border-top: 1px solid {COLORS['border']};
            margin: 0.5rem 0;
        }}
    </style>
    """


def apply_css():
    """Inject custom CSS into the Streamlit app."""
    st.markdown(load_css(), unsafe_allow_html=True)


def render_section_header(page_name: str):
    """Render the standard page header with section ID, title, description, and meta info."""
    from config import PAGE_IDS, PAGE_DESCRIPTIONS
    section_id = PAGE_IDS.get(page_name, "00")
    description = PAGE_DESCRIPTIONS.get(page_name, "")

    # Determine the current date range from session state if available
    date_range_str = ""
    if "date_range" in st.session_state and st.session_state.date_range:
        dr = st.session_state.date_range
        if len(dr) == 2:
            date_range_str = f"{dr[0].strftime('%b %d, %Y')} — {dr[1].strftime('%b %d, %Y')}"

    st.markdown(
        f'<div class="section-header">{section_id} / {page_name.upper()}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="page-title">{page_name}</div>',
        unsafe_allow_html=True,
    )
    if description:
        st.markdown(
            f'<div class="page-description">{description}</div>',
            unsafe_allow_html=True,
        )
    if date_range_str:
        st.markdown(
            f'<div class="header-meta">Selected period: {date_range_str}</div>',
            unsafe_allow_html=True,
        )
    st.markdown('<hr class="header-divider" />', unsafe_allow_html=True)


def metric_card(label: str, value: str, delta: str = None, delta_positive: bool = None, tooltip: str = None):
    """Render a custom metric card with industrial-minimal styling."""
    delta_class = "neutral"
    if delta_positive is True:
        delta_class = "positive"
    elif delta_positive is False:
        delta_class = "negative"

    delta_html = ""
    if delta is not None:
        delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>'

    tooltip_html = f' title="{tooltip}"' if tooltip else ""

    html = f"""
    <div class="kpi-container"{tooltip_html}>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """
    return html


def render_empty_state(message: str = "No data available for the current selection."):
    """Render an empty state message."""
    st.markdown(
        f'<div class="empty-state"><p>{message}</p></div>',
        unsafe_allow_html=True,
    )


def sql_code_block(sql: str):
    """Render SQL code with basic syntax highlighting via CSS classes."""
    import html

    escaped = html.escape(sql)

    # Simple keyword highlighting via regex replacement in markdown
    # We use a pre block with the sql-code class
    highlighted = """
    <pre class="sql-code">{code}</pre>
    """.format(code=escaped)

    return highlighted