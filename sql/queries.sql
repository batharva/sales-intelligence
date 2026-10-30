-- Whitelisted analytical queries. `f` is the sidebar-filtered sales table (bound parameters).
-- name: Largest order lines
-- group: Basic queries
-- question: Which individual order lines brought in the most revenue?
-- technique: SELECT, ORDER BY, LIMIT
-- reading: Large single lines show where one-off deals drive revenue.
SELECT order_id, order_date, product, quantity, ROUND(sales, 2) AS sales
FROM f
ORDER BY sales DESC
LIMIT 10;
-- end
-- name: Revenue by category
-- group: Aggregations and grouping
-- question: How much revenue and volume does each category generate?
-- technique: GROUP BY, SUM, ROUND
-- reading: Compare category shares before deciding where to focus assortment.
SELECT category, ROUND(SUM(sales), 2) AS total_revenue, SUM(quantity) AS units_sold
FROM f
GROUP BY category
ORDER BY total_revenue DESC;
-- end
-- name: Monthly revenue with month-over-month growth
-- group: Date analysis
-- question: How does revenue change from month to month?
-- technique: strftime, CTE, LAG window, NULLIF
-- reading: Growth is NULL for the first month and when the prior month is zero.
WITH m AS (
  SELECT strftime('%Y-%m', order_date) AS month, SUM(sales) AS revenue FROM f GROUP BY 1
)
SELECT month, ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 1) AS mom_growth_pct
FROM m ORDER BY month;
-- end
-- name: Top products ranked within category
-- group: Window functions
-- question: Which products lead their own category?
-- technique: RANK() OVER (PARTITION BY ...)
-- reading: Ranking inside a category avoids comparing items with very different price points.
SELECT * FROM (
  SELECT category, product, ROUND(SUM(sales), 2) AS revenue,
         RANK() OVER (PARTITION BY category ORDER BY SUM(sales) DESC) AS rank_in_category
  FROM f GROUP BY category, product
) WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;
-- end
-- name: Running revenue total
-- group: Window functions
-- question: How does cumulative revenue build over time?
-- technique: SUM() OVER (ORDER BY ...)
-- reading: A flattening curve signals slowing sales in that window.
WITH m AS (SELECT strftime('%Y-%m', order_date) AS month, SUM(sales) AS revenue FROM f GROUP BY 1)
SELECT month, ROUND(revenue, 2) AS revenue, ROUND(SUM(revenue) OVER (ORDER BY month), 2) AS cumulative_revenue
FROM m ORDER BY month;
-- end
-- name: One-time versus repeat customers
-- group: Customer analysis
-- question: What share of customers ordered more than once?
-- technique: CTE, COUNT DISTINCT, CASE
-- reading: This is repeat purchase rate within the filter window, not retention.
WITH c AS (SELECT customer_id, COUNT(DISTINCT order_id) AS orders, SUM(sales) AS revenue FROM f GROUP BY 1)
SELECT CASE WHEN orders > 1 THEN 'Repeat' ELSE 'One-time' END AS customer_type,
       COUNT(*) AS customers, ROUND(SUM(revenue), 2) AS revenue
FROM c GROUP BY 1;
-- end
-- name: Region versus company average order value
-- group: Joins
-- question: Which regions have a higher or lower AOV than the company overall?
-- technique: CROSS JOIN to a scalar subquery
-- reading: Differences are descriptive; check order counts before acting on small gaps.
SELECT r.region, r.orders, ROUND(r.revenue / r.orders, 2) AS region_aov, ROUND(t.aov, 2) AS company_aov,
       ROUND(100.0 * (r.revenue / r.orders - t.aov) / t.aov, 1) AS vs_company_pct
FROM (SELECT region, SUM(sales) AS revenue, COUNT(DISTINCT order_id) AS orders FROM f GROUP BY region) r
CROSS JOIN (SELECT SUM(sales) * 1.0 / COUNT(DISTINCT order_id) AS aov FROM f) t
ORDER BY vs_company_pct DESC;
-- end
-- name: Non-positive sales lines
-- group: Data quality
-- question: Which lines have zero or negative sales?
-- technique: WHERE filter, ORDER BY
-- reading: These may be legitimate returns or credits; they are flagged, not removed.
SELECT order_id, order_date, product, quantity, sales FROM f WHERE sales <= 0 ORDER BY sales LIMIT 50;
-- end
