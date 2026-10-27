-- 07: Advanced Analysis
-- Business questions: Complex analytical patterns using advanced SQL techniques
-- Techniques: Window functions, CTEs, subqueries, date arithmetic, conditional aggregation

-- ██ WINDOW FUNCTIONS ██

-- Running revenue total by month
SELECT
    strftime('%Y-%m', order_date) AS month,
    ROUND(SUM(sales), 2) AS monthly_revenue,
    ROUND(SUM(SUM(sales)) OVER (ORDER BY strftime('%Y-%m', order_date)), 2) AS running_total,
    ROUND(AVG(SUM(sales)) OVER (ORDER BY strftime('%Y-%m', order_date) ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS moving_avg_3m
FROM orders
GROUP BY month
ORDER BY month;

-- Product ranking within category
SELECT
    p.category,
    p.product_name,
    ROUND(SUM(o.sales), 2) AS revenue,
    RANK() OVER (PARTITION BY p.category ORDER BY SUM(o.sales) DESC) AS rank_in_category,
    ROUND(100.0 * SUM(o.sales) / SUM(SUM(o.sales)) OVER (PARTITION BY p.category), 2) AS pct_of_category
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category, p.product_id
ORDER BY p.category, rank_in_category;

-- ██ CTE (Common Table Expressions) ██

-- Customer lifetime value (CLV) segments
WITH customer_metrics AS (
    SELECT
        c.customer_id,
        c.customer_name,
        c.segment,
        COUNT(DISTINCT o.order_id) AS order_count,
        ROUND(SUM(o.sales), 2) AS lifetime_value,
        ROUND(AVG(o.sales), 2) AS avg_order_value,
        CAST(julianday('2025-01-01') - julianday(MAX(o.order_date)) AS INTEGER) AS days_since_last_order
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id
)
SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(lifetime_value), 2) AS avg_lifetime_value,
    ROUND(AVG(order_count), 2) AS avg_orders,
    ROUND(AVG(days_since_last_order), 0) AS avg_days_inactive
FROM customer_metrics
GROUP BY segment
ORDER BY avg_lifetime_value DESC;

-- ██ SUBQUERIES ██

-- Products sold above average category price
SELECT
    p.product_name,
    p.category,
    ROUND(AVG(o.sales), 2) AS avg_sale_price,
    ROUND((SELECT AVG(sales) FROM orders o2
           JOIN products p2 ON o2.product_id = p2.product_id
           WHERE p2.category = p.category), 2) AS category_avg_price,
    ROUND(AVG(o.sales) - (SELECT AVG(sales) FROM orders o2
           JOIN products p2 ON o2.product_id = p2.product_id
           WHERE p2.category = p.category), 2) AS price_difference
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id
HAVING AVG(o.sales) > (SELECT AVG(sales) FROM orders o2
                         JOIN products p2 ON o2.product_id = p2.product_id
                         WHERE p2.category = p.category)
ORDER BY price_difference DESC
LIMIT 10;

-- ██ CONDITIONAL AGGREGATION ██

-- Monthly sales with conditional columns
SELECT
    strftime('%Y-%m', order_date) AS month,
    ROUND(SUM(CASE WHEN discount = 0 THEN sales ELSE 0 END), 2) AS full_price_revenue,
    ROUND(SUM(CASE WHEN discount > 0 THEN sales ELSE 0 END), 2) AS discounted_revenue,
    ROUND(100.0 * SUM(CASE WHEN discount > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_discounted_items,
    ROUND(AVG(CASE WHEN discount > 0 THEN discount END) * 100, 2) AS avg_discount_pct
FROM orders
GROUP BY month
ORDER BY month;

-- ██ DATE ANALYSIS ██

-- Day-of-week analysis
SELECT
    CASE CAST(strftime('%w', order_date) AS INTEGER)
        WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_of_week,
    ROUND(SUM(sales), 2) AS revenue,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(AVG(sales), 2) AS avg_order_value
FROM orders
GROUP BY strftime('%w', order_date)
ORDER BY strftime('%w', order_date);