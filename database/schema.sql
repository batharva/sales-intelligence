-- Fact table: one row per order line, exactly as loaded (staging layer).
CREATE TABLE sales (
    row_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id      TEXT,
    order_date    TEXT,      -- ISO-8601 (YYYY-MM-DD); NULL when the source value could not be parsed
    ship_date     TEXT,
    customer_id   TEXT,
    customer_name TEXT,
    segment       TEXT,
    region        TEXT,
    state         TEXT,
    category      TEXT,
    sub_category  TEXT,
    product_id    TEXT,
    product_name  TEXT,
    quantity      INTEGER,
    sales         REAL,      -- net line revenue as recorded (after discount)
    discount      REAL,      -- fraction, 0.20 = 20 %
    profit        REAL
);

-- Dimension tables derived from the fact table (see dimensions.sql).
CREATE TABLE dim_customers (
    customer_id   TEXT PRIMARY KEY,
    customer_name TEXT,
    segment       TEXT,
    region        TEXT,
    state         TEXT
);

CREATE TABLE dim_products (
    product_id   TEXT PRIMARY KEY,
    product_name TEXT,
    category     TEXT,
    sub_category TEXT
);

-- Build metadata (source, timestamps, optional-column flags).
CREATE TABLE meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX idx_sales_date     ON sales (order_date);
CREATE INDEX idx_sales_customer ON sales (customer_id);
CREATE INDEX idx_sales_product  ON sales (product_id);
CREATE INDEX idx_sales_order    ON sales (order_id);
