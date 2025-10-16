--1. Assign row numbers to customers ordered by credit limit descending
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_CREDIT_LIMIT,
    ROW_NUMBER() OVER (ORDER BY CUST_CREDIT_LIMIT DESC) AS row_num
FROM SH.CUSTOMERS;

--2. Rank customers within each state by credit limit
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_STATE_PROVINCE,
    CUST_CREDIT_LIMIT,
    RANK() OVER (PARTITION BY CUST_STATE_PROVINCE ORDER BY CUST_CREDIT_LIMIT DESC) AS rank_within_state
FROM SH.CUSTOMERS;

--3. Use DENSE_RANK() to find the top 5 credit holders per country
SELECT *
FROM (
    SELECT 
        CUST_ID,
        CUST_FIRST_NAME,
        CUST_LAST_NAME,
        COUNTRY_ID,
        CUST_CREDIT_LIMIT,
        DENSE_RANK() OVER (PARTITION BY COUNTRY_ID ORDER BY CUST_CREDIT_LIMIT DESC) AS dense_rank
    FROM SH.CUSTOMERS
)
WHERE dense_rank <= 5;

--4. Divide customers into 4 quartiles based on their credit limit using NTILE(4)
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_CREDIT_LIMIT,
    NTILE(4) OVER (ORDER BY CUST_CREDIT_LIMIT) AS quartile
FROM SH.CUSTOMERS;

--5. Calculate a running total of credit limits ordered by customer_id
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_CREDIT_LIMIT,
    SUM(CUST_CREDIT_LIMIT) OVER (ORDER BY CUST_ID) AS running_total
FROM SH.CUSTOMERS;

--6. Show cumulative average credit limit by country
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    COUNTRY_ID,
    CUST_CREDIT_LIMIT,
    AVG(CUST_CREDIT_LIMIT) OVER (PARTITION BY COUNTRY_ID ORDER BY CUST_ID ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_average
FROM SH.CUSTOMERS;

--7. Compare each customer’s credit limit to the previous one using LAG()
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_CREDIT_LIMIT,
    LAG(CUST_CREDIT_LIMIT) OVER (ORDER BY CUST_ID) AS prev_credit
FROM SH.CUSTOMERS;

--8. Show next customer’s credit limit using LEAD()
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_CREDIT_LIMIT,
    LEAD(CUST_CREDIT_LIMIT) OVER (ORDER BY CUST_ID) AS next_credit
FROM SH.CUSTOMERS;

--9. Display the difference between each customer’s credit limit and the previous one
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_CREDIT_LIMIT,
    CUST_CREDIT_LIMIT - LAG(CUST_CREDIT_LIMIT) OVER (ORDER BY CUST_ID) AS diff_prev
FROM SH.CUSTOMERS;

--10. For each country, display the first and last credit limit using FIRST_VALUE() and LAST_VALUE()
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    COUNTRY_ID,
    CUST_CREDIT_LIMIT,
    FIRST_VALUE(CUST_CREDIT_LIMIT) OVER (PARTITION BY COUNTRY_ID ORDER BY CUST_ID ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_credit,
    LAST_VALUE(CUST_CREDIT_LIMIT) OVER (PARTITION BY COUNTRY_ID ORDER BY CUST_ID ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_credit
FROM SH.CUSTOMERS;

--11. Compute percentage rank (PERCENT_RANK()) of customers based on credit limit
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_CREDIT_LIMIT,
    PERCENT_RANK() OVER (ORDER BY CUST_CREDIT_LIMIT) AS percentage_rank
FROM SH.CUSTOMERS;

--12. Show each customer’s position in percentile (CUME_DIST())
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_CREDIT_LIMIT,
    CUME_DIST() OVER (ORDER BY CUST_CREDIT_LIMIT) AS cum_dist
FROM SH.CUSTOMERS;

--13. Display the difference between the maximum and current credit limit for each customer
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_CREDIT_LIMIT,
    MAX(CUST_CREDIT_LIMIT) OVER () - CUST_CREDIT_LIMIT AS diff_max
FROM SH.CUSTOMERS;

--14. Rank income levels by their average credit limit
SELECT 
    CUST_INCOME_LEVEL,
    AVG(CUST_CREDIT_LIMIT) AS Avg_credit,
    RANK() OVER (ORDER BY AVG(CUST_CREDIT_LIMIT) DESC) AS Rank_income
FROM SH.CUSTOMERS
GROUP BY CUST_INCOME_LEVEL;

--15. Calculate the average credit limit over the last 10 customers (sliding window)
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_CREDIT_LIMIT,
    AVG(CUST_CREDIT_LIMIT) OVER (ORDER BY CUST_ID ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS moving_averageg_10
FROM SH.CUSTOMERS;

--16. For each state, calculate the cumulative total of credit limits ordered by city
SELECT 
    CUST_ID,
    CUST_STATE_PROVINCE,
    CUST_CITY,
    CUST_CREDIT_LIMIT,
    SUM(CUST_CREDIT_LIMIT) OVER (PARTITION BY CUST_STATE_PROVINCE ORDER BY CUST_CITY ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_total
FROM SH.CUSTOMERS;

--17. Find customers whose credit limit equals the median credit limit (use PERCENTILE_CONT(0.5))
SELECT *
FROM (
    SELECT 
        CUST_ID,
        CUST_FIRST_NAME,
        CUST_LAST_NAME,
        CUST_CREDIT_LIMIT,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CUST_CREDIT_LIMIT) OVER () AS median_credit
    FROM SH.CUSTOMERS
)
WHERE CUST_CREDIT_LIMIT = median_credit;

--18. Display the highest 3 credit holders per state using ROW_NUMBER() and PARTITION BY 
SELECT *
FROM (
    SELECT 
        CUST_ID,
        CUST_FIRST_NAME,
        CUST_LAST_NAME,
        CUST_STATE_PROVINCE,
        CUST_CREDIT_LIMIT,
        ROW_NUMBER() OVER (PARTITION BY CUST_STATE_PROVINCE ORDER BY CUST_CREDIT_LIMIT DESC) AS row_num
    FROM SH.CUSTOMERS
)
WHERE row_num <= 3;

--19. Identify customers whose credit limit increased compared to previous row (using LAG)
SELECT *
FROM (
    SELECT 
        CUST_ID,
        CUST_FIRST_NAME,
        CUST_LAST_NAME,
        CUST_CREDIT_LIMIT,
        LAG(CUST_CREDIT_LIMIT) OVER (ORDER BY CUST_ID) AS prev_credit
    FROM SH.CUSTOMERS
)
WHERE CUST_CREDIT_LIMIT > prev_credit;

--20. Calculate moving average of credit limits with a window of 3
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_CREDIT_LIMIT,
    AVG(CUST_CREDIT_LIMIT) OVER (ORDER BY CUST_ID ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_average_3
FROM SH.CUSTOMERS;

--21. Show cumulative percentage of total credit limit per country
SELECT 
    CUST_ID,
    COUNTRY_ID,
    CUST_CREDIT_LIMIT,
    SUM(CUST_CREDIT_LIMIT) OVER (PARTITION BY COUNTRY_ID ORDER BY CUST_ID) /
    SUM(CUST_CREDIT_LIMIT) OVER (PARTITION BY COUNTRY_ID) * 100 AS cum_percentage
FROM SH.CUSTOMERS;

--22. Rank customers by age (derived from CUST_YEAR_OF_BIRTH)
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    2025 - CUST_YEAR_OF_BIRTH AS age,
    RANK() OVER (ORDER BY 2025 - CUST_YEAR_OF_BIRTH DESC) AS age_rank
FROM SH.CUSTOMERS;

--23. Calculate difference in age between current and previous customer in the same state
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_STATE_PROVINCE,
    2025 - CUST_YEAR_OF_BIRTH AS age,
    (2025 - CUST_YEAR_OF_BIRTH) - LAG(2025 - CUST_YEAR_OF_BIRTH) OVER (PARTITION BY CUST_STATE_PROVINCE ORDER BY CUST_ID) AS age_diff
FROM SH.CUSTOMERS;

--24. Use RANK() and DENSE_RANK() to show how ties are treated differently
SELECT 
    CUST_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CUST_CREDIT_LIMIT,
    RANK() OVER (ORDER BY CUST_CREDIT_LIMIT DESC) AS rank_value,
    DENSE_RANK() OVER (ORDER BY CUST_CREDIT_LIMIT DESC) AS dense_rank_value
FROM SH.CUSTOMERS;

--25. Compare each state’s average credit limit with country average using window partition
SELECT 
    CUST_ID,
    CUST_STATE_PROVINCE,
    COUNTRY_ID,
    CUST_CREDIT_LIMIT,
    AVG(CUST_CREDIT_LIMIT) OVER (PARTITION BY CUST_STATE_PROVINCE) AS state_avg,
    AVG(CUST_CREDIT_LIMIT) OVER (PARTITION BY COUNTRY_ID) AS country_avg
FROM SH.CUSTOMERS;

--26. Show total credit per state and also its rank within each country
SELECT 
    CUST_STATE_PROVINCE,
    COUNTRY_ID,
    SUM(CUST_CREDIT_LIMIT) AS total_credit,
    RANK() OVER (PARTITION BY COUNTRY_ID ORDER BY SUM(CUST_CREDIT_LIMIT) DESC) AS rank_within_country
FROM SH.CUSTOMERS
GROUP BY COUNTRY_ID, CUST_STATE_PROVINCE;

--27. Find customers whose credit limit is above the 90th percentile of their income level
SELECT *
FROM (
    SELECT 
        CUST_ID,
        CUST_FIRST_NAME,
        CUST_LAST_NAME,
        CUST_INCOME_LEVEL,
        CUST_CREDIT_LIMIT,
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY CUST_CREDIT_LIMIT) OVER (PARTITION BY CUST_INCOME_LEVEL) AS percentile_90
    FROM SH.CUSTOMERS
)
WHERE CUST_CREDIT_LIMIT > percentile_90;

--28. Display top 3 and bottom 3 customers per country by credit limit
SELECT *
FROM (
    SELECT 
        CUST_ID,
        CUST_FIRST_NAME,
        CUST_LAST_NAME,
        COUNTRY_ID,
        CUST_CREDIT_LIMIT,
        ROW_NUMBER() OVER (PARTITION BY COUNTRY_ID ORDER BY CUST_CREDIT_LIMIT DESC) AS rank_desc,
        ROW_NUMBER() OVER (PARTITION BY COUNTRY_ID ORDER BY CUST_CREDIT_LIMIT ASC) AS rank_asc
    FROM SH.CUSTOMERS
)
WHERE rank_desc <= 3 OR rank_asc <= 3;

--29. Calculate rolling sum of 5 customers’ credit limit within each country
SELECT 
    CUST_ID,
    COUNTRY_ID,
    CUST_CREDIT_LIMIT,
    SUM(CUST_CREDIT_LIMIT) OVER (PARTITION BY COUNTRY_ID ORDER BY CUST_ID ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_sum_5
FROM SH.CUSTOMERS;

--30. For each marital status, display the most and least wealthy customers using analytical functions
SELECT *
FROM (
    SELECT 
        CUST_ID,
        CUST_FIRST_NAME,
        CUST_LAST_NAME,
        CUST_MARITAL_STATUS,
        CUST_CREDIT_LIMIT,
        RANK() OVER (PARTITION BY CUST_MARITAL_STATUS ORDER BY CUST_CREDIT_LIMIT DESC) AS rank_high,
        RANK() OVER (PARTITION BY CUST_MARITAL_STATUS ORDER BY CUST_CREDIT_LIMIT ASC) AS rank_low
    FROM SH.CUSTOMERS
)
WHERE rank_high = 1 OR rank_low = 1;
