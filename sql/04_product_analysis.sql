-- 04: Product Analysis
-- Business question: Which products perform best and why?
-- Technique: Ranking, window functions, category aggregation, concentration analysis

-- Top 10 products by revenue
SELECT
    p.product_name,
    p.category,
    p.subcategory,
    ROUND(SUM(o.sales), 2) AS revenue,
    SUM(o.quantity) AS quantity_sold,
    ROUND(SUM(o.profit), 2) AS profit,
    ROUND(CASE WHEN SUM(o.sales) > 0 THEN (SUM(o.profit) / SUM(o.sales)) * 100 ELSE 0 END, 2) AS profit_margin_pct,
    ROW_NUMBER() OVER (ORDER BY SUM(o.sales) DESC) AS rank
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10;

-- Top 10 products by quantity sold
SELECT
    p.product_name,
    p.category,
    p.subcategory,
    SUM(o.quantity) AS quantity_sold,
    ROUND(SUM(o.sales), 2) AS revenue,
    ROUND(SUM(o.profit), 2) AS profit,
    ROW_NUMBER() OVER (ORDER BY SUM(o.quantity) DESC) AS rank
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id
ORDER BY quantity_sold DESC
LIMIT 10;

-- Bottom 10 products by revenue
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
HAVING SUM(o.sales) > 0
ORDER BY revenue ASC
LIMIT 10;

-- Category performance summary
SELECT
    p.category,
    COUNT(DISTINCT p.product_id) AS unique_products,
    ROUND(SUM(o.sales), 2) AS total_revenue,
    SUM(o.quantity) AS total_quantity,
    ROUND(AVG(o.sales), 2) AS avg_revenue_per_sale,
    ROUND(SUM(o.profit), 2) AS total_profit,
    ROUND(100.0 * SUM(o.sales) / SUM(SUM(o.sales)) OVER (), 2) AS revenue_share_pct
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- Revenue concentration (top N products share of total)
SELECT
    p.product_name,
    p.category,
    ROUND(SUM(o.sales), 2) AS product_revenue,
    ROUND(100.0 * SUM(o.sales) / (SELECT SUM(sales) FROM orders WHERE sales > 0), 2) AS share_pct,
    ROUND(
        100.0 * SUM(SUM(o.sales)) OVER (ORDER BY SUM(o.sales) DESC)
        / (SELECT SUM(sales) FROM orders WHERE sales > 0),
    2) AS cumulative_share_pct
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE o.sales > 0
GROUP BY p.product_id
ORDER BY product_revenue DESC
LIMIT 20;

-- Product sales trends (monthly for top products)
SELECT
    p.product_id,
    p.product_name,
    strftime('%Y-%m', o.order_date) AS month,
    ROUND(SUM(o.sales), 2) AS revenue,
    SUM(o.quantity) AS quantity
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE p.product_id IN (
    SELECT product_id FROM orders GROUP BY product_id ORDER BY SUM(sales) DESC LIMIT 5
)
GROUP BY p.product_id, month
ORDER BY p.product_name, month;