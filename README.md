# Sales Intelligence | SQL Analytics

**Industrial-minimal analytics dashboard built with Streamlit, SQLite, and Python.**

A portfolio-quality business intelligence application that demonstrates SQL-based sales data analysis through an elegant, interactive dashboard. Explore sales performance, product rankings, customer segments, geographic trends, and business insights.

![Dashboard Preview](assets/screenshots/dashboard.png)

---

## Business Problem

Retail businesses generate massive amounts of transactional data, but extracting actionable insights requires:

- **Data literacy gaps**: Not all stakeholders can write SQL
- **Scattered analysis**: Metrics live in spreadsheets, presentations, and ad-hoc queries
- **Inconsistent definitions**: KPIs calculated differently across teams
- **Limited interactivity**: Static reports can't answer follow-up questions

This dashboard solves these problems by providing a **unified, interactive analytics workspace** powered by SQL, accessible through an intuitive interface.

---

## Dashboard Features

| Page | Description |
|---|---|
| **Executive Overview** | Key KPIs, revenue trends, category breakdown, executive summary |
| **Revenue Analysis** | Revenue trends, growth rates, category/regional breakdowns, AOV analysis |
| **Product Intelligence** | Product rankings, category performance, revenue concentration |
| **Customer Intelligence** | Customer segments, RFM analysis, purchase behavior, repeat rate |
| **Regional Performance** | Regional comparisons, category mix, performance vs. company average |
| **SQL Explorer** | Interactive library of analytical SQL queries with execution |
| **Data Quality** | Automated validation checks and data integrity reporting |
| **Methodology** | KPI definitions, schema documentation, business insights |

### Key Capabilities

- **Global filters**: Date range, product category, and region filters across all pages
- **Interactive charts**: Plotly-powered with hover details and responsive sizing
- **Data export**: Download filtered data as CSV from key pages
- **SQL exploration**: Browse, view, and execute predefined analytical queries
- **RFM segmentation**: Automated customer segmentation with quartile scoring
- **Data quality checks**: Real-time validation against the database

---

## Technology Stack

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core programming language |
| **Streamlit** | Web application framework |
| **Pandas** | Data manipulation and analysis |
| **NumPy** | Numerical computations |
| **Plotly** | Interactive data visualization |
| **SQLite** | Lightweight embedded database |
| **SQL** | Analytical queries and data transformation |

---

## Dataset

This project uses a **synthetically generated retail dataset** modeled after the Tableau Sample - Superstore schema. The dataset includes:

- **~10,000 order line items** spanning January 2020 — December 2024
- **~800 customers** across Consumer, Corporate, and Home Office segments
- **~1,800 products** in Furniture, Office Supplies, and Technology categories
- **4 US regions**: East, West, Central, South

The database is automatically generated when the application starts for the first time.

**License**: Open for demonstration and educational use.

---

## SQL Techniques Demonstrated

| Technique | Application |
|---|---|
| **Basic Queries** | SELECT, WHERE, ORDER BY, LIMIT |
| **Aggregations** | GROUP BY, SUM, COUNT, AVG |
| **Joins** | INNER JOIN with foreign keys |
| **Date Functions** | STRFTIME, JULIANDAY, date arithmetic |
| **Window Functions** | ROW_NUMBER, RANK, LAG, NTILE, running totals |
| **Common Table Expressions** | WITH clause for multi-step queries |
| **Subqueries** | Nested SELECTs for comparative analysis |
| **Conditional Aggregation** | CASE expressions in aggregations |
| **RFM Analysis** | Quartile-based customer segmentation |

---

## Database Design

The database follows a **star schema** with a central fact table and two dimension tables:

```
┌─────────────────────┐
│     customers       │──┐
│ (dimension)         │  │
└─────────────────────┘  │
                         │
┌─────────────────────┐  │  ┌─────────────────────┐
│       orders        │──┼──│      products       │
│     (fact table)    │  │  │    (dimension)      │
└─────────────────────┘  │  └─────────────────────┘
                         │
                   customer_id (FK)
                   product_id (FK)
```

---

## Local Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Git (optional)

### Setup Instructions

```bash
# Clone the repository
git clone https://github.com/yourusername/sales-intelligence.git
cd sales-intelligence

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch the application
streamlit run app.py
```

The database will be automatically generated on first launch. You can also manually seed it:

```bash
python database/seed_database.py
```

### Verify Installation

The application should open at `http://localhost:8501` with a fully populated dashboard showing sales metrics, charts, and tables.

---

## Streamlit Community Cloud Deployment

1. Push the repository to GitHub
2. Log in to [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Click **"New app"** and select your repository
4. Set the main file path to `app.py`
5. Click **"Deploy"**

**No additional configuration required.** The database generates automatically on the first run.

---

## Project Structure

```
sales-intelligence/
├── app.py                    # Main application entry point
├── config.py                 # Configuration constants
├── requirements.txt          # Python dependencies
├── README.md                 # Documentation
├── .gitignore                # Git ignore rules
│
├── data/
│   └── README.md             # Dataset documentation
│
├── database/
│   ├── schema.sql            # Database schema
│   └── seed_database.py      # Data generation and seeding
│
├── sql/                      # Analytical SQL queries
│   ├── 01_data_quality.sql
│   ├── 02_overview.sql
│   ├── 03_revenue_analysis.sql
│   ├── 04_product_analysis.sql
│   ├── 05_customer_analysis.sql
│   ├── 06_regional_analysis.sql
│   └── 07_advanced_analysis.sql
│
├── pages/                    # Streamlit multipage files
│   ├── 1_Revenue_Analysis.py
│   ├── 2_Product_Intelligence.py
│   ├── 3_Customer_Intelligence.py
│   ├── 4_Regional_Performance.py
│   ├── 5_SQL_Explorer.py
│   ├── 6_Data_Quality.py
│   └── 7_Methodology.py
│
├── utils/                    # Utility modules
│   ├── data_loader.py
│   ├── database.py
│   ├── queries.py
│   ├── metrics.py
│   └── styling.py
│
└── assets/
    └── screenshots/          # Application screenshots
```

---

## KPI Definitions

| KPI | Definition |
|---|---|
| **Total Revenue** | SUM(sales) across all order line items |
| **Total Orders** | COUNT(DISTINCT order_id) |
| **Units Sold** | SUM(quantity) |
| **Average Order Value** | SUM(sales) / COUNT(DISTINCT order_id) |
| **Unique Customers** | COUNT(DISTINCT customer_id) |
| **Total Profit** | SUM(profit) |
| **Profit Margin** | (SUM(profit) / SUM(sales)) × 100 |
| **Revenue Growth** | ((current - previous) / previous) × 100 |
| **Repeat Purchase Rate** | Customers with >1 order / total customers × 100 |

---

## Analytical Limitations

1. **Synthetic data**: The dataset is generated algorithmically; patterns may not reflect real-world dynamics
2. **No cost data**: Profit margins are calculated from generated values
3. **US only**: Geographic analysis is limited to four US regions
4. **No causal inference**: Correlations do not imply causation
5. **RFM limitations**: Segments are relative to this dataset and require business validation

---

## Future Improvements

- Real-time data source connections
- Predictive analytics and forecasting
- Anomaly detection
- Custom user-defined SQL queries (read-only sandbox)
- User authentication and multi-tenant support
- Report scheduling and email distribution
- Interactive geographic mapping
- Automated data refresh and versioning

---

## License

This project is provided for demonstration and educational purposes. The synthetic dataset is generated algorithmically and does not contain real business data.

---

*Built with Python, Streamlit, SQLite, Plotly, and Pandas.*