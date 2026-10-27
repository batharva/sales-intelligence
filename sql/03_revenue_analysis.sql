-- 03: Revenue Analysis
-- Business question: How is revenue trending and what drives it?
-- Technique: Date aggregation, window functions, growth calculations, subcategories

-- Monthly revenue trend with growth
SELECT
    strftime('%Y-%m', order_date) AS month,
    ROUND(SUM(sales), 2) AS revenue,
    SUM(quantity) AS units_sold,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(AVG(sales), 2) AS avg_order_value,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(
        (SUM(sales) - LAG(SUM(sales)) OVER (ORDER BY strftime('%Y-%m', order_date)))
        / NULLIF(ABS(LAG(SUM(sales)) OVER (ORDER BY strftime('%Y-%m', order_date))), 0) * 100,
    2) AS growth_pct
FROM orders
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;

-- Revenue by category and subcategory
SELECT
    p.category,
    p.subcategory,
    ROUND(SUM(o.sales), 2) AS revenue,
    SUM(o.quantity) AS quantity,
    ROUND(SUM(o.profit), 2) AS profit,
    ROUND(100.0 * SUM(o.sales) / SUM(SUM(o.sales)) OVER (PARTITION BY p.category), 2) AS category_share_pct
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category, p.subcategory
ORDER BY revenue DESC;

-- Revenue by region
SELECT
    c.region,
    ROUND(SUM(o.sales), 2) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(AVG(o.sales), 2) AS avg_order_value,
    ROUND(100.0 * SUM(o.sales) / SUM(SUM(o.sales)) OVER (), 2) AS revenue_share_pct,
    ROUND(SUM(o.profit), 2) AS profit
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.region
ORDER BY revenue DESC;

-- Average order value trend
SELECT
    strftime('%Y-%m', order_date) AS month,
    ROUND(AVG(sales), 2) AS avg_order_value,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(SUM(sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS revenue_per_order
FROM orders
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;

-- Order volume trend
SELECT
    strftime('%Y-%m', order_date) AS month,
    COUNT(DISTINCT order_id) AS unique_orders,
    SUM(quantity) AS total_units,
    ROUND(AVG(quantity), 2) AS avg_units_per_order
FROM orders
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;

-- Revenue contribution by category (year over year)
SELECT
    strftime('%Y', order_date) AS year,
    p.category,
    ROUND(SUM(o.sales), 2) AS revenue,
    ROUND(100.0 * SUM(o.sales) / SUM(SUM(o.sales)) OVER (PARTITION BY strftime('%Y', order_date)), 2) AS contribution_pct
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY year, p.category
ORDER BY year, revenue DESC;