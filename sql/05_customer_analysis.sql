-- 05: Customer Analysis
-- Business question: Who are our customers and how do they behave?
-- Technique: Customer segmentation, RFM analysis, repeat purchase analysis, distribution

-- Customer summary metrics
SELECT
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(SUM(sales) / NULLIF(COUNT(DISTINCT customer_id), 0), 2) AS avg_revenue_per_customer,
    ROUND(AVG(sales), 2) AS avg_order_value
FROM orders
WHERE sales > 0;

-- Repeat purchase rate
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM orders
    GROUP BY customer_id
)
SELECT
    COUNT(CASE WHEN order_count > 1 THEN 1 END) AS repeat_customers,
    COUNT(*) AS total_customers,
    ROUND(100.0 * COUNT(CASE WHEN order_count > 1 THEN 1 END) / COUNT(*), 2) AS repeat_purchase_rate_pct
FROM customer_orders;

-- One-time vs repeat customers
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count,
        ROUND(SUM(sales), 2) AS total_spent
    FROM orders
    GROUP BY customer_id
)
SELECT
    CASE WHEN order_count = 1 THEN 'One-Time' ELSE 'Repeat' END AS customer_type,
    COUNT(*) AS customer_count,
    ROUND(SUM(total_spent), 2) AS total_revenue,
    ROUND(AVG(total_spent), 2) AS avg_revenue_per_customer
FROM customer_orders
GROUP BY customer_type;

-- Average order value by segment
SELECT
    c.segment,
    ROUND(AVG(o.sales), 2) AS avg_order_value,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(o.sales), 2) AS total_revenue,
    COUNT(DISTINCT c.customer_id) AS customer_count
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY avg_order_value DESC;

-- Top 10 customers by revenue
SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    c.region,
    ROUND(SUM(o.sales), 2) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS order_count,
    ROUND(AVG(o.sales), 2) AS avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id
ORDER BY total_revenue DESC
LIMIT 10;

-- Purchase frequency distribution
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM orders
    GROUP BY customer_id
)
SELECT
    order_count AS frequency,
    COUNT(*) AS customer_count
FROM customer_orders
GROUP BY order_count
ORDER BY frequency;

-- RFM Segmentation
WITH customer_rfm AS (
    SELECT
        c.customer_id,
        CAST(julianday('2025-01-01') - julianday(MAX(o.order_date)) AS INTEGER) AS recency,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(o.sales), 2) AS monetary
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id
),
rfm_scores AS (
    SELECT
        customer_id,
        recency,
        frequency,
        monetary,
        NTILE(4) OVER (ORDER BY recency DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary ASC) AS m_score
    FROM customer_rfm
)
SELECT
    customer_id,
    recency,
    frequency,
    monetary,
    r_score, f_score, m_score,
    CASE
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 1 AND m_score >= 1 THEN 'Loyal Customers'
        WHEN r_score >= 3 AND f_score <= 2 AND m_score <= 2 THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 2 THEN 'Needs Attention'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Lost'
        ELSE 'Other'
    END AS rfm_segment
FROM rfm_scores;