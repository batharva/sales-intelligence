-- 06: Regional Analysis
-- Business question: How does performance vary by region?
-- Technique: Grouped aggregations, comparison with averages, category mix, ranking

-- Revenue and orders by region
SELECT
    c.region,
    ROUND(SUM(o.sales), 2) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(o.quantity) AS units_sold,
    ROUND(AVG(o.sales), 2) AS avg_order_value,
    ROUND(SUM(o.profit), 2) AS profit,
    ROUND(100.0 * SUM(o.sales) / SUM(SUM(o.sales)) OVER (), 2) AS revenue_share_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.region
ORDER BY revenue DESC;

-- Regional comparison with company average
WITH regional_stats AS (
    SELECT
        c.region,
        ROUND(SUM(o.sales), 2) AS revenue,
        COUNT(DISTINCT o.order_id) AS orders,
        ROUND(AVG(o.sales), 2) AS avg_order_value,
        ROUND(SUM(o.profit) / NULLIF(SUM(o.sales), 0) * 100, 2) AS profit_margin_pct
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY c.region
),
company_avg AS (
    SELECT
        ROUND(AVG(avg_order_value), 2) AS avg_aov,
        ROUND(AVG(profit_margin_pct), 2) AS avg_margin
    FROM regional_stats
)
SELECT
    rs.region,
    rs.revenue,
    rs.orders,
    rs.avg_order_value,
    ca.avg_aov AS company_avg_aov,
    ROUND(rs.avg_order_value - ca.avg_aov, 2) AS aov_vs_company_avg,
    rs.profit_margin_pct,
    ca.avg_margin AS company_avg_margin,
    ROUND(rs.profit_margin_pct - ca.avg_margin, 2) AS margin_vs_company_avg
FROM regional_stats rs
CROSS JOIN company_avg ca
ORDER BY rs.revenue DESC;

-- Regional category mix
SELECT
    c.region,
    p.category,
    ROUND(SUM(o.sales), 2) AS revenue,
    ROUND(100.0 * SUM(o.sales) / SUM(SUM(o.sales)) OVER (PARTITION BY c.region), 2) AS region_category_share_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.region, p.category
ORDER BY c.region, revenue DESC;

-- Regional performance by year
SELECT
    strftime('%Y', o.order_date) AS year,
    c.region,
    ROUND(SUM(o.sales), 2) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY year, c.region
ORDER BY year, revenue DESC;

-- Customer density by region
SELECT
    region,
    COUNT(DISTINCT customer_id) AS customers,
    ROUND(100.0 * COUNT(DISTINCT customer_id) / SUM(COUNT(DISTINCT customer_id)) OVER (), 2) AS customer_share_pct
FROM customers
GROUP BY region
ORDER BY customers DESC;