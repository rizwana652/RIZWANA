Joins with Analytical Logic (10 Questions)

1. Join SH.CUSTOMERS and SH.SALES to find customers with the highest sales totals.

SELECT 
    C.CUST_ID,
    C.CUST_FIRST_NAME || ' ' || C.CUST_LAST_NAME AS CUSTOMER_NAME,
    SUM(S.AMOUNT_SOLD) AS TOTAL_SALES
FROM 
    SH.CUSTOMERS C
JOIN 
    SH.SALES S
ON 
    C.CUST_ID = S.CUST_ID
GROUP BY 
    C.CUST_ID, C.CUST_FIRST_NAME, C.CUST_LAST_NAME
ORDER BY 
    TOTAL_SALES DESC;


2. For each customer, show their total sales amount and their rank within country.

SELECT 
    C.CUST_ID,
    C.CUST_FIRST_NAME || ' ' || C.CUST_LAST_NAME AS CUSTOMER_NAME,
    C.COUNTRY_ID,
    SUM(S.QUANTITY_SOLD) AS TOTAL_SALES,
    RANK() OVER (
        PARTITION BY C.COUNTRY_ID 
        ORDER BY SUM(S.AMOUNT_SOLD) DESC
    ) AS SALES_RANK_WITHIN_COUNTRY
FROM 
    SH.CUSTOMERS C
JOIN 
    SH.SALES S
ON 
    C.CUST_ID = S.CUST_ID
GROUP BY 
    C.CUST_ID, C.CUST_FIRST_NAME, C.CUST_LAST_NAME, C.COUNTRY_ID
ORDER BY 
    C.COUNTRY_ID, SALES_RANK_WITHIN_COUNTRY;

3. Find customers who purchased more than average sales amount of their country.

SELECT 
    C.CUST_ID,
    C.CUST_FIRST_NAME || ' ' || C.CUST_LAST_NAME AS CUSTOMER_NAME,
    C.COUNTRY_ID,
    SUM(S.AMOUNT_SOLD) AS TOTAL_SALES
FROM 
    SH.CUSTOMERS C
JOIN 
    SH.SALES S
ON 
    C.CUST_ID = S.CUST_ID
GROUP BY 
    C.CUST_ID, C.CUST_FIRST_NAME, C.CUST_LAST_NAME, C.COUNTRY_ID
HAVING 
    SUM(S.AMOUNT_SOLD) > (
        SELECT 
            AVG(SUM(S2.AMOUNT_SOLD))
        FROM 
            SH.CUSTOMERS C2
        JOIN 
            SH.SALES S2
        ON 
            C2.CUST_ID = S2.CUST_ID
        WHERE 
            C2.COUNTRY_ID = C.COUNTRY_ID
        GROUP BY 
            C2.COUNTRY_ID
    )
ORDER BY 
    C.COUNTRY_ID, TOTAL_SALES DESC;

4. Display top 3 spenders per state.
SELECT 
    CUST_STATE_PROVINCE,
    CUST_ID,
    CUSTOMER_NAME,
    TOTAL_SALES,
    SALES_RANK
FROM (
    SELECT 
        C.CUST_STATE_PROVINCE,
        C.CUST_ID,
        C.CUST_FIRST_NAME || ' ' || C.CUST_LAST_NAME AS CUSTOMER_NAME,
        SUM(S.AMOUNT_SOLD) AS TOTAL_SALES,
        RANK() OVER (
            PARTITION BY C.CUST_STATE_PROVINCE
            ORDER BY SUM(S.AMOUNT_SOLD) DESC
        ) AS SALES_RANK
    FROM 
        SH.CUSTOMERS C
    JOIN 
        SH.SALES S
    ON 
        C.CUST_ID = S.CUST_ID
    GROUP BY 
        C.CUST_STATE_PROVINCE, C.CUST_ID, C.CUST_FIRST_NAME, C.CUST_LAST_NAME
)
WHERE 
    SALES_RANK <= 3
ORDER BY 
    CUST_STATE_PROVINCE, SALES_RANK;




5. Rank customers within each country by total sales quantity.

SELECT 
    C.CUST_ID,
    C.CUST_FIRST_NAME || ' ' || C.CUST_LAST_NAME AS CUSTOMER_NAME,
    C.COUNTRY_ID,
    SUM(S.QUANTITY_SOLD) AS TOTAL_QUANTITY,
    RANK() OVER (
        PARTITION BY C.COUNTRY_ID 
        ORDER BY SUM(S.QUANTITY_SOLD) DESC
    ) AS SALES_RANK
FROM 
    SH.CUSTOMERS C
JOIN 
    SH.SALES S
ON 
    C.CUST_ID = S.CUST_ID
GROUP BY 
    C.CUST_ID, C.CUST_FIRST_NAME, C.CUST_LAST_NAME, C.COUNTRY_ID
ORDER BY 
    C.COUNTRY_ID, SALES_RANK;

6. Calculate each customer’s contribution percentage to country-level sales.
SELECT 
    C.COUNTRY_ID,
    C.CUST_ID,
    C.CUST_FIRST_NAME || ' ' || C.CUST_LAST_NAME AS CUSTOMER_NAME,
    SUM(S.AMOUNT_SOLD) AS TOTAL_SALES,
    ROUND(
        100 * SUM(S.AMOUNT_SOLD) / 
        SUM(SUM(S.AMOUNT_SOLD)) OVER (PARTITION BY C.COUNTRY_ID),
        2
    ) AS PERCENT_CONTRIBUTION
FROM 
    SH.CUSTOMERS C
JOIN 
    SH.SALES S
ON 
    C.CUST_ID = S.CUST_ID
GROUP BY 
    C.COUNTRY_ID, C.CUST_ID, C.CUST_FIRST_NAME, C.CUST_LAST_NAME
ORDER BY 
    C.COUNTRY_ID, PERCENT_CONTRIBUTION DESC;


7. Identify customers whose sales have decreased compared to previous month.

-- Step 1: Aggregate sales per customer per month
WITH monthly_sales AS (
    SELECT 
        C.CUST_ID,
        C.CUST_FIRST_NAME || ' ' || C.CUST_LAST_NAME AS CUSTOMER_NAME,
        TO_CHAR(S.TIME_ID, 'YYYY-MM') AS SALES_MONTH,
        SUM(S.AMOUNT_SOLD) AS TOTAL_SALES
    FROM 
        SH.CUSTOMERS C
    JOIN 
        SH.SALES S
    ON 
        C.CUST_ID = S.CUST_ID
    GROUP BY 
        C.CUST_ID, C.CUST_FIRST_NAME, C.CUST_LAST_NAME, TO_CHAR(S.TIME_ID, 'YYYY-MM')
),

-- Step 2: Apply LAG() to compare with previous month
sales_comparison AS (
    SELECT 
        CUST_ID,
        CUSTOMER_NAME,
        SALES_MONTH,
        TOTAL_SALES,
        LAG(TOTAL_SALES) OVER (
            PARTITION BY CUST_ID 
            ORDER BY SALES_MONTH
        ) AS PREV_MONTH_SALES
    FROM 
        monthly_sales
)

-- Step 3: Select only those customers whose sales dropped
SELECT 
    CUST_ID,
    CUSTOMER_NAME,
    SALES_MONTH,
    TOTAL_SALES,
    PREV_MONTH_SALES
FROM 
    sales_comparison
WHERE 
    TOTAL_SALES < PREV_MONTH_SALES
ORDER BY 
    CUST_ID, SALES_MONTH;



8.Show customers who have never made a sale.

SELECT 
    C.CUST_ID,
    C.CUST_FIRST_NAME || ' ' || C.CUST_LAST_NAME AS CUSTOMER_NAME,
    C.COUNTRY_ID
FROM 
    SH.CUSTOMERS C
LEFT JOIN 
    SH.SALES S
ON 
    C.CUST_ID = S.CUST_ID
WHERE 
    S.CUST_ID IS NULL
ORDER BY 
    C.CUST_ID;

9. Find correlation between credit limit and total sales (using GROUP BY + analytics).
SELECT 
    C.COUNTRY_ID,
    CORR(TOTAL_SALES, CUST_CREDIT_LIMIT) AS CORR_CREDIT_TOTALSALES
FROM (
    SELECT 
        C.CUST_ID,
        C.COUNTRY_ID,
        C.CUST_CREDIT_LIMIT,
        SUM(S.AMOUNT_SOLD) AS TOTAL_SALES
    FROM 
        SH.CUSTOMERS C
    LEFT JOIN 
        SH.SALES S
    ON 
        C.CUST_ID = S.CUST_ID
    GROUP BY 
        C.CUST_ID, C.COUNTRY_ID, C.CUST_CREDIT_LIMIT
) CUSTOMER_SALES
GROUP BY 
    C.COUNTRY_ID
ORDER BY 
    C.COUNTRY_ID;


10. Show moving average of monthly sales per customer.
WITH monthly_sales AS (
    SELECT 
        C.CUST_ID,
        C.CUST_FIRST_NAME || ' ' || C.CUST_LAST_NAME AS CUSTOMER_NAME,
        TO_CHAR(S.TIME_ID, 'YYYY-MM') AS SALES_MONTH,
        SUM(S.AMOUNT_SOLD) AS TOTAL_SALES
    FROM 
        SH.CUSTOMERS C
    JOIN 
        SH.SALES S
    ON 
        C.CUST_ID = S.CUST_ID
    GROUP BY 
        C.CUST_ID, C.CUST_FIRST_NAME, C.CUST_LAST_NAME, TO_CHAR(S.TIME_ID, 'YYYY-MM')
)
SELECT 
    CUST_ID,
    CUSTOMER_NAME,
    SALES_MONTH,
    TOTAL_SALES,
    ROUND(
        AVG(TOTAL_SALES) OVER (
            PARTITION BY CUST_ID 
            ORDER BY SALES_MONTH
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2
    ) AS MOVING_AVG_3M
FROM 
    monthly_sales
ORDER BY 
    CUST_ID, SALES_MONTH;