-- ===================================================================
-- TARGET SQL CASE STUDY - COMPLETE SOLUTION (MySQL Version)
-- Dataset: Target Brazil E-commerce (2016-2018)
-- ===================================================================

-- ===================================================================
-- SECTION 1: INITIAL EXPLORATION
-- ===================================================================

-- 1.1 Data type of all columns in the "customers" table
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'customers'
ORDER BY ORDINAL_POSITION;

-- 1.2 Get the time range between which the orders were placed
SELECT 
    MIN(order_purchase_timestamp) AS first_order_date,
    MAX(order_purchase_timestamp) AS last_order_date,
    DATEDIFF(MAX(order_purchase_timestamp), MIN(order_purchase_timestamp)) AS total_days
FROM orders;

-- 1.3 Count the Cities & States of customers who ordered during the given period
SELECT 
    COUNT(DISTINCT c.customer_city) AS total_cities,
    COUNT(DISTINCT c.customer_state) AS total_states
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id;

-- ===================================================================
-- SECTION 2: IN-DEPTH EXPLORATION
-- ===================================================================

-- 2.1 Is there a growing trend in the no. of orders placed over the past years?
SELECT 
    YEAR(order_purchase_timestamp) AS order_year,
    COUNT(*) AS total_orders,
    LAG(COUNT(*)) OVER (ORDER BY YEAR(order_purchase_timestamp)) AS previous_year_orders,
    CASE 
        WHEN LAG(COUNT(*)) OVER (ORDER BY YEAR(order_purchase_timestamp)) IS NULL THEN NULL
        ELSE ((COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY YEAR(order_purchase_timestamp))) * 100.0 / 
              LAG(COUNT(*)) OVER (ORDER BY YEAR(order_purchase_timestamp)))
    END AS year_over_year_growth_pct
FROM orders
GROUP BY YEAR(order_purchase_timestamp)
ORDER BY order_year;

-- 2.2 Can we see some kind of monthly seasonality in terms of the no. of orders being placed?
SELECT 
    YEAR(order_purchase_timestamp) AS order_year,
    MONTH(order_purchase_timestamp) AS order_month,
    COUNT(*) AS total_orders
FROM orders
GROUP BY YEAR(order_purchase_timestamp), MONTH(order_purchase_timestamp)
ORDER BY order_year, order_month;

-- 2.3 During what time of the day, do the Brazilian customers mostly place their orders?
-- 0-6 hrs : Dawn, 7-12 hrs : Mornings, 13-18 hrs : Afternoon, 19-23 hrs : Night
SELECT 
    CASE 
        WHEN HOUR(order_purchase_timestamp) BETWEEN 0 AND 6 THEN 'Dawn'
        WHEN HOUR(order_purchase_timestamp) BETWEEN 7 AND 12 THEN 'Morning'
        WHEN HOUR(order_purchase_timestamp) BETWEEN 13 AND 18 THEN 'Afternoon'
        WHEN HOUR(order_purchase_timestamp) BETWEEN 19 AND 23 THEN 'Night'
    END AS time_of_day,
    COUNT(*) AS order_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM orders
GROUP BY 
    CASE 
        WHEN HOUR(order_purchase_timestamp) BETWEEN 0 AND 6 THEN 'Dawn'
        WHEN HOUR(order_purchase_timestamp) BETWEEN 7 AND 12 THEN 'Morning'
        WHEN HOUR(order_purchase_timestamp) BETWEEN 13 AND 18 THEN 'Afternoon'
        WHEN HOUR(order_purchase_timestamp) BETWEEN 19 AND 23 THEN 'Night'
    END
ORDER BY order_count DESC;

-- ===================================================================
-- SECTION 3: EVOLUTION OF E-COMMERCE ORDERS IN THE BRAZIL REGION
-- ===================================================================

-- 3.1 Get the month on month no. of orders placed in each state
SELECT 
    c.customer_state,
    YEAR(o.order_purchase_timestamp) AS order_year,
    MONTH(o.order_purchase_timestamp) AS order_month,
    COUNT(*) AS total_orders
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_state, YEAR(o.order_purchase_timestamp), MONTH(o.order_purchase_timestamp)
ORDER BY c.customer_state, order_year, order_month;

-- 3.2 How are the customers distributed across all the states?
SELECT 
    customer_state,
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(COUNT(DISTINCT customer_id) * 100.0 / SUM(COUNT(DISTINCT customer_id)) OVER (), 2) AS percentage
FROM customers
GROUP BY customer_state
ORDER BY total_customers DESC;

-- ===================================================================
-- SECTION 4: IMPACT ON ECONOMY
-- ===================================================================

-- 4.1 Get the % increase in the cost of orders from year 2017 to 2018 
-- (include months between Jan to Aug only)
WITH OrderCosts AS (
    SELECT 
        YEAR(o.order_purchase_timestamp) AS order_year,
        SUM(p.payment_value) AS total_cost
    FROM orders o
    INNER JOIN payments p ON o.order_id = p.order_id
    WHERE YEAR(o.order_purchase_timestamp) IN (2017, 2018)
        AND MONTH(o.order_purchase_timestamp) BETWEEN 1 AND 8
    GROUP BY YEAR(o.order_purchase_timestamp)
)
SELECT 
    (SELECT total_cost FROM OrderCosts WHERE order_year = 2018) AS cost_2018,
    (SELECT total_cost FROM OrderCosts WHERE order_year = 2017) AS cost_2017,
    ROUND(((SELECT total_cost FROM OrderCosts WHERE order_year = 2018) - 
           (SELECT total_cost FROM OrderCosts WHERE order_year = 2017)) * 100.0 / 
          (SELECT total_cost FROM OrderCosts WHERE order_year = 2017), 2) AS percentage_increase;

-- 4.2 Calculate the Total & Average value of order price for each state
SELECT 
    c.customer_state,
    SUM(oi.price) AS total_order_price,
    AVG(oi.price) AS avg_order_price
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY total_order_price DESC;

-- 4.3 Calculate the Total & Average value of order freight for each state
SELECT 
    c.customer_state,
    SUM(oi.freight_value) AS total_freight_value,
    AVG(oi.freight_value) AS avg_freight_value
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY total_freight_value DESC;

-- ===================================================================
-- SECTION 5: ANALYSIS BASED ON SALES, FREIGHT AND DELIVERY TIME
-- ===================================================================

-- 5.1 Find the no. of days taken to deliver each order from the order's purchase date as delivery time.
-- Also, calculate the difference (in days) between the estimated & actual delivery date of an order.
SELECT 
    o.order_id,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp) AS time_to_deliver,
    DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date) AS diff_estimated_delivery
FROM orders o
WHERE o.order_delivered_customer_date IS NOT NULL
    AND o.order_estimated_delivery_date IS NOT NULL;

-- 5.2 Find out the top 5 states with the highest & lowest average freight value
-- Highest
SELECT 
    c.customer_state,
    AVG(oi.freight_value) AS avg_freight_value
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY avg_freight_value DESC
LIMIT 5;

-- Lowest
SELECT 
    c.customer_state,
    AVG(oi.freight_value) AS avg_freight_value
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY avg_freight_value ASC
LIMIT 5;

-- 5.3 Find out the top 5 states with the highest & lowest average delivery time
-- Highest
SELECT 
    c.customer_state,
    AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)) AS avg_delivery_time
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY avg_delivery_time DESC
LIMIT 5;

-- Lowest
SELECT 
    c.customer_state,
    AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)) AS avg_delivery_time
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY avg_delivery_time ASC
LIMIT 5;

-- 5.4 Find out the top 5 states where the order delivery is really fast as compared to the estimated date of delivery
SELECT 
    c.customer_state,
    AVG(DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date)) AS avg_days_faster_than_estimated
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_delivered_customer_date IS NOT NULL
    AND o.order_estimated_delivery_date IS NOT NULL
GROUP BY c.customer_state
HAVING AVG(DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date)) > 0
ORDER BY avg_days_faster_than_estimated DESC
LIMIT 5;

-- ===================================================================
-- SECTION 6: ANALYSIS BASED ON THE PAYMENTS
-- ===================================================================

-- 6.1 Find the month on month no. of orders placed using different payment types
SELECT 
    YEAR(o.order_purchase_timestamp) AS order_year,
    MONTH(o.order_purchase_timestamp) AS order_month,
    p.payment_type,
    COUNT(DISTINCT o.order_id) AS order_count
FROM orders o
INNER JOIN payments p ON o.order_id = p.order_id
GROUP BY YEAR(o.order_purchase_timestamp), MONTH(o.order_purchase_timestamp), p.payment_type
ORDER BY order_year, order_month, payment_type;

-- 6.2 Find the no. of orders placed on the basis of the payment installments that have been paid
SELECT 
    payment_installments,
    COUNT(DISTINCT order_id) AS order_count
FROM payments
GROUP BY payment_installments
ORDER BY payment_installments;

-- ===================================================================
-- ADDITIONAL INSIGHTS QUERIES
-- ===================================================================

-- A.1 Top 10 products by sales volume
SELECT 
    p.product_category_name,
    COUNT(oi.order_item_id) AS total_items_sold,
    SUM(oi.price) AS total_revenue
FROM order_items oi
INNER JOIN products p ON oi.product_id = p.product_id
WHERE p.product_category_name IS NOT NULL
GROUP BY p.product_category_name
ORDER BY total_items_sold DESC
LIMIT 10;

-- A.2 Customer retention analysis - customers with multiple orders
SELECT 
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END) AS repeat_customers,
    ROUND(COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END) * 100.0 / 
          COUNT(DISTINCT customer_id), 2) AS retention_rate
FROM (
    SELECT 
        customer_id,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
) AS customer_orders;

-- A.3 Average order value by state
SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(p.payment_value) AS total_revenue,
    AVG(p.payment_value) AS avg_order_value
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN payments p ON o.order_id = p.order_id
GROUP BY c.customer_state
ORDER BY avg_order_value DESC;

-- A.4 Order status distribution
SELECT 
    order_status,
    COUNT(*) AS order_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;

-- A.5 Review score analysis
SELECT 
    review_score,
    COUNT(*) AS review_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM reviews
WHERE review_score IS NOT NULL
GROUP BY review_score
ORDER BY review_score DESC;

-- ===================================================================
-- END OF SQL QUERIES
-- ===================================================================

