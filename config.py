"""
Project configuration and constants.
"""

import pathlib

# Project root
PROJECT_ROOT = pathlib.Path(__file__).parent.resolve()

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_DIR = PROJECT_ROOT / "database"
SQL_DIR = PROJECT_ROOT / "sql"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Database
DB_PATH = DATA_DIR / "sales_intelligence.db"

# Dataset configuration
DATASET_NAME = "Superstore Retail Dataset (Synthetic)"
DATASET_SOURCE = "Generated sample data modeled after Tableau's Sample - Superstore dataset"
DATASET_ROWS = 9994
DATASET_LICENSE = "Open for demonstration and educational use"

# App metadata
APP_NAME = "Sales Intelligence"
APP_SUBTITLE = "SQL Analytics System"
APP_VERSION = "1.0.0"
APP_YEAR = "2026"

# Navigation pages
PAGES = [
    "Overview",
    "Revenue Analysis",
    "Product Intelligence",
    "Customer Intelligence",
    "Regional Performance",
    "SQL Explorer",
    "Data Quality",
    "Methodology",
]

PAGE_IDS = {
    "Overview": "01",
    "Revenue Analysis": "02",
    "Product Intelligence": "03",
    "Customer Intelligence": "04",
    "Regional Performance": "05",
    "SQL Explorer": "06",
    "Data Quality": "07",
    "Methodology": "08",
}

PAGE_DESCRIPTIONS = {
    "Overview": "Key performance indicators, revenue trends, and category breakdown.",
    "Revenue Analysis": "Deep dive into revenue drivers, growth trends, and order patterns.",
    "Product Intelligence": "Product ranking, category performance, and profitability analysis.",
    "Customer Intelligence": "Customer segments, purchase behavior, and RFM analysis.",
    "Regional Performance": "Geographic revenue distribution and regional comparisons.",
    "SQL Explorer": "Interactive exploration of analytical SQL queries behind the dashboard.",
    "Data Quality": "Data integrity checks and validation results.",
    "Methodology": "Analytical methodology, KPI definitions, and business insights.",
}

# Date format
DATE_FORMAT = "%Y-%m-%d"

# Color palette (industrial minimal)
COLORS = {
    "background": "#F3F3EF",
    "surface": "#FFFFFF",
    "text_primary": "#191B1A",
    "text_secondary": "#6B706D",
    "border": "#D9DDD7",
    "accent_primary": "#285C48",
    "accent_secondary": "#637D8A",
    "positive": "#2E7D5E",
    "negative": "#A0504A",
    "chart_grid": "#E5E7E2",
    "chart_colors": ["#285C48", "#637D8A", "#8B6F5E", "#5A7A6E", "#9B8E7A", "#4A6B5A"],
}