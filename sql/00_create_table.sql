-- Create the table used for the prepared purchase data.
-- Run this after connecting to an empty InsightFlow database.

CREATE TABLE retail_purchases (
    invoice_no TEXT,
    stock_code TEXT,
    description TEXT,
    quantity INTEGER,
    invoice_date TIMESTAMP,
    unit_price NUMERIC,
    customer_id TEXT,
    country TEXT,
    is_cancellation BOOLEAN,
    line_amount NUMERIC
);