INSERT INTO dim_customers (customer_id, customer_name, segment, region, state)
SELECT customer_id, MIN(customer_name), MIN(segment), MIN(region), MIN(state)
FROM sales
WHERE customer_id IS NOT NULL
GROUP BY customer_id;

INSERT INTO dim_products (product_id, product_name, category, sub_category)
SELECT product_id, MIN(product_name), MIN(category), MIN(sub_category)
FROM sales
WHERE product_id IS NOT NULL
GROUP BY product_id;
