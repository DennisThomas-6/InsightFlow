-- 1. Check purchase totals.
SELECT
    COUNT(*) AS purchase_lines,
    COUNT(DISTINCT invoice_no) AS distinct_invoices,
    ROUND(SUM(line_amount), 2) AS purchase_total
FROM retail_purchases;


-- 2. Monthly purchase summary.
SELECT
    DATE_TRUNC('month', invoice_date)::date AS month,
    ROUND(SUM(line_amount), 2) AS purchase_total,
    COUNT(DISTINCT invoice_no) AS invoice_count
FROM retail_purchases
GROUP BY DATE_TRUNC('month', invoice_date)::date
ORDER BY month;


-- 3. Top 10 countries.
SELECT
    country,
    ROUND(SUM(line_amount), 2) AS purchase_total,
    COUNT(DISTINCT invoice_no) AS invoice_count
FROM retail_purchases
GROUP BY country
ORDER BY purchase_total DESC
LIMIT 10;


-- 4. Top 10 items in the working product view.
SELECT
    stock_code,
    description,
    ROUND(SUM(line_amount), 2) AS purchase_total,
    SUM(quantity) AS quantity_purchased
FROM retail_purchases
WHERE stock_code NOT IN ('DOT', 'POST', 'M')
   OR stock_code IS NULL
GROUP BY stock_code, description
ORDER BY SUM(line_amount) DESC
LIMIT 10;


-- 5. RFM measures for the first 10 customers.
SELECT
    customer_id,
    MAX(invoice_date) AS last_purchase,
    DATE '2011-12-10' - MAX(invoice_date)::date AS recency,
    COUNT(DISTINCT invoice_no) AS frequency,
    ROUND(SUM(line_amount), 2) AS monetary
FROM retail_purchases
WHERE customer_id IS NOT NULL
GROUP BY customer_id
ORDER BY customer_id
LIMIT 10;


-- 6. Identified-customer reconciliation.
SELECT
    COUNT(DISTINCT customer_id) AS customers,
    ROUND(SUM(line_amount), 2) AS customer_purchase_total
FROM retail_purchases
WHERE customer_id IS NOT NULL;