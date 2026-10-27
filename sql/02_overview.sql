-- 02: Executive Overview Queries
-- Business question: What are the top-level business metrics?
-- Technique: Aggregation, date filtering, window functions

-- Overall KPI summary
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(AVG(sales), 2) AS avg_order_value,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(profit), 2) AS total_profit
FROM orders
WHERE sales > 0;

-- Revenue by month
SELECT
    strftime('%Y-%m', order_date) AS month,
    ROUND(SUM(sales), 2) AS revenue,
    SUM(quantity) AS units_sold,
    COUNT(DISTINCT order_id) AS orders
FROM orders
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;

-- Revenue by category
SELECT
    p.category,
    ROUND(SUM(o.sales), 2) AS total_revenue,
    SUM(o.quantity) AS units_sold,
    ROUND(SUM(o.profit), 2) AS total_profit,
    ROUND(AVG(o.sales), 2) AS avg_sale
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- Top 5 products by revenue
SELECT
    p.product_name,
    p.category,
    p.subcategory,
    ROUND(SUM(o.sales), 2) AS revenue,
    SUM(o.quantity) AS quantity_sold,
    ROUND(SUM(o.profit), 2) AS profit
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 5;

-- Revenue by region
SELECT
    c.region,
    ROUND(SUM(o.sales), 2) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(AVG(o.sales), 2) AS avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.region
ORDER BY revenue DESC;

-- Customer segment contribution
SELECT
    c.segment,
    ROUND(SUM(o.sales), 2) AS revenue,
    COUNT(DISTINCT c.customer_id) AS customer_count,
    ROUND(AVG(o.sales), 2) AS avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY revenue DESC;

-- Recent orders
SELECT
    o.order_id,
    o.order_date,
    c.customer_name,
    p.product_name,
    o.sales,
    o.quantity,
    c.region
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
ORDER BY o.order_date DESC
LIMIT 10;

-- Comparison period summary (same period, previous year)
-- Use parameter markers for dates; this is a template
SELECT
    CASE WHEN order_date BETWEEN ? AND ? THEN 'current' ELSE 'previous' END AS period,
    ROUND(SUM(sales), 2) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders
FROM orders
WHERE (order_date BETWEEN ? AND ?) OR (order_date BETWEEN ? AND ?)
GROUP BY period;