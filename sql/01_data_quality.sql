-- 01: Data Quality Checks
-- Business question: What data quality issues exist in the sales database?
-- Technique: Data profiling, validation queries, referential integrity checks

-- Total row count
SELECT 'Total Orders' AS check_name, COUNT(*) AS records_affected, 'info' AS severity,
       'Total order line items in the database' AS description FROM orders
UNION ALL

-- Duplicate transactions
SELECT 'Duplicate Transactions', COUNT(*) - COUNT(DISTINCT order_id || product_id), 'high',
       'Order line items with the same order and product combination' FROM orders
WHERE (order_id, product_id) IN (
    SELECT order_id, product_id FROM orders GROUP BY order_id, product_id HAVING COUNT(*) > 1
)
UNION ALL

-- Missing values in key fields
SELECT 'Missing Customer References',
       COUNT(*) - COUNT(customer_id), 'high',
       'Orders without a valid customer reference' FROM orders
WHERE customer_id IS NULL OR customer_id = ''
UNION ALL

-- Missing ship dates
SELECT 'Missing Ship Dates',
       COUNT(*) - COUNT(ship_date), 'low',
       'Orders where the ship date is not recorded' FROM orders
WHERE ship_date IS NULL OR ship_date = ''
UNION ALL

-- Invalid quantity (negative or zero)
SELECT 'Invalid Quantities',
       COUNT(*), 'medium',
       'Orders with negative or zero quantity (may be returns or corrections)' FROM orders
WHERE quantity <= 0
UNION ALL

-- Negative or zero sales
SELECT 'Negative or Zero Sales',
       COUNT(*), 'medium',
       'Orders with non-positive sales values (credits, returns, or errors)' FROM orders
WHERE sales <= 0
UNION ALL

-- Extreme discount values
SELECT 'Extreme Discounts',
       COUNT(*), 'low',
       'Orders with discounts exceeding 50%' FROM orders
WHERE discount > 0.5
UNION ALL

-- Referential integrity: orders without matching customer
SELECT 'Orphan Orders (Customers)',
       COUNT(*), 'high',
       'Orders referencing customers that do not exist in the customer table' FROM orders o
WHERE NOT EXISTS (SELECT 1 FROM customers c WHERE c.customer_id = o.customer_id)
UNION ALL

-- Referential integrity: orders without matching product
SELECT 'Orphan Orders (Products)',
       COUNT(*), 'high',
       'Orders referencing products that do not exist in the product table' FROM orders o
WHERE NOT EXISTS (SELECT 1 FROM products p WHERE p.product_id = o.product_id)
UNION ALL

-- Future dates
SELECT 'Future Order Dates',
       COUNT(*), 'medium',
       'Orders with order dates in the future' FROM orders
WHERE order_date > date('now')
UNION ALL

-- Ship date before order date
SELECT 'Ship Date Before Order Date',
       COUNT(*), 'medium',
       'Orders where the ship date precedes the order date' FROM orders
WHERE ship_date < order_date
UNION ALL

-- Category inconsistencies
SELECT 'Empty or Unknown Categories',
       COUNT(*), 'medium',
       'Products with missing or non-standard categories' FROM products
WHERE category IS NULL OR category = ''
UNION ALL

-- Negative profit margins
SELECT 'Negative Profit Orders',
       COUNT(*), 'low',
       'Orders where profit is negative (sold at a loss)' FROM orders
WHERE profit < 0
;