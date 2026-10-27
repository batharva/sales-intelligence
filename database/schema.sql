-- Sales Intelligence Database Schema
-- Modeled after retail sales data with dimensions and facts

-- Customers dimension
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment TEXT NOT NULL CHECK(segment IN ('Consumer', 'Corporate', 'Home Office')),
    country TEXT DEFAULT 'United States',
    region TEXT NOT NULL CHECK(region IN ('East', 'West', 'Central', 'South')),
    state TEXT,
    city TEXT,
    postal_code TEXT
);

-- Products dimension
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL
);

-- Orders fact table
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    ship_date TEXT,
    ship_mode TEXT CHECK(ship_mode IN ('Standard Class', 'Second Class', 'First Class', 'Same Day')),
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    sales REAL NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity != 0),
    discount REAL DEFAULT 0 CHECK(discount >= 0 AND discount <= 1),
    profit REAL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_product_id ON orders(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_region ON customers(region);
CREATE INDEX IF NOT EXISTS idx_orders_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_customers_region ON customers(region);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_subcategory ON products(subcategory);