--A. Aggregation & Grouping (20 Questions)

1. Find the total, average, minimum, and maximum credit limit of all customers.
SELECT 
    SUM(CUST_CREDIT_LIMIT) AS Total_Credit_Limit,
    AVG(CUST_CREDIT_LIMIT) AS Average_Credit_Limit,
    MIN(CUST_CREDIT_LIMIT) AS Minimum_Credit_Limit,
    MAX(CUST_CREDIT_LIMIT) AS Maximum_Credit_Limit
FROM SH.CUSTOMERS;


2.Count the number of customers in each income level.
SELECT COUNT(CUST_INCOME_LEVEL)AS NO_OF_CUSTOMERS FROM SH.CUSTOMERS

3.Show total credit limit by state and country.
SELECT COUNTRY_ID,CUST_STATE_PROVINCE, 
SUM(CUST_CREDIT_LIMIT)AS Total_Credit_Limit FROM SH.CUSTOMERS
 GROUP BY COUNTRY_ID, CUST_STATE_PROVINCE 
 ORDER BY COUNTRY_ID, CUST_STATE_PROVINCE

4.Display average credit limit for each marital status and gender combination.
SELECT CUST_MARITAL_STATUS,CUST_GENDER,
 SUM(CUST_CREDIT_LIMIT)AS Total_Credit_Limit FROM SH.CUSTOMERS
 GROUP BY CUST_MARITAL_STATUS,CUST_GENDER
  ORDER BY CUST_MARITAL_STATUS,CUST_GENDER


5.Find the top 3 states with the highest average credit limit.
SELECT 
    CUST_STATE_PROVINCE,
    AVG(CUST_CREDIT_LIMIT) AS Average_Credit_Limit
FROM SH.CUSTOMERS
GROUP BY 
    CUST_STATE_PROVINCE
ORDER BY 
    Average_Credit_Limit DESC
FETCH FIRST 3 ROWS ONLY;


6.Find the country with the maximum total customer credit limit.
SELECT COUNTRY_ID, Total_Credit_Limit
FROM (
    SELECT 
        COUNTRY_ID,
        SUM(CUST_CREDIT_LIMIT) AS Total_Credit_Limit
    FROM SH.CUSTOMERS
    GROUP BY COUNTRY_ID
    ORDER BY Total_Credit_Limit DESC
)
WHERE ROWNUM = 1;




7.Show the number of customers whose credit limit exceeds their state average.
SELECT COUNT(*) 
FROM SH.CUSTOMERS C
WHERE CUST_CREDIT_LIMIT > (
    SELECT AVG(CUST_CREDIT_LIMIT)
    FROM SH.CUSTOMERS
    WHERE CUST_STATE_PROVINCE = C.CUST_STATE_PROVINCE
)

8.Calculate total and average credit limit for customers born after 1980.
SELECT 
    SUM(CUST_CREDIT_LIMIT) AS Total_Credit_Limit,
    AVG(CUST_CREDIT_LIMIT) AS Average_Credit_Limit
FROM SH.CUSTOMERS
WHERE CUST_YEAR_OF_BIRTH  > 1980;

9.Find states having more than 50 customers.
SELECT CUST_STATE_PROVINCE, COUNT(*) AS NUM_CUSTOMERS FROM SH.CUSTOMERS GROUP BY CUST_STATE_PROVINCE HAVING COUNT(*)> 50 ORDER BY NUM_CUSTOMERS DESC;

10.List countries where the average credit limit is higher than the global average.

SELECT COUNTRY_ID, AVG(CUST_CREDIT_LIMIT)
FROM SH.customers
GROUP BY COUNTRY_ID
HAVING AVG(CUST_CREDIT_LIMIT)> ( 
    SELECT AVG(CUST_CREDIT_LIMIT)
    FROM SH.CUSTOMERS
)
11.Calculate the variance and standard deviation of customer credit limits by country.
SELECT 
    COUNTRY_ID,
    VARIANCE(CUST_CREDIT_LIMIT) AS Credit_Limit_Variance,
    STDDEV(CUST_CREDIT_LIMIT) AS Credit_Limit_StdDev
FROM SH.CUSTOMERS
GROUP BY COUNTRY_ID
ORDER BY COUNTRY_ID;

12.Find the state with the smallest range (max–min) in credit limits.
SELECT CUST_STATE_PROVINCE_ID ,
     MAX(CUST_CREDIT_LIMIT) - MIN(CUST_CREDIT_LIMIT) AS CREDIT_RANGE
FROM SH.CUSTOMERS 
GROUP BY CUST_STATE_PROVINCE_ID
ORDER BY CREDIT_RANGE ASC
FETCH FIRST ROW ONLY

13.Show the total number of customers per income level and the percentage contribution of each.
SELECT 
    CUST_INCOME_LEVEL,
    COUNT(*) AS TOTAL_CUSTOMERS,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 
        2
    ) AS PERCENT_CONTRIBUTION
FROM 
    SH.CUSTOMERS
GROUP BY 
    CUST_INCOME_LEVEL
ORDER BY 
    TOTAL_CUSTOMERS DESC;

14.For each income level, find how many customers have NULL credit limits.
SELECT 
    CUST_INCOME_LEVEL,
    COUNT(*) AS NULL_CREDITS
FROM SH.CUSTOMERS WHERE CUST_CREDIT_LIMIT IS NULL
GROUP BY CUST_INCOME_LEVEL
ORDER BY CUST_INCOME_LEVEL ASC

15.Display countries where the sum of credit limits exceeds 10 million.
SELECT COUNTRY_ID,
  SUM(CUST_CREDIT_LIMIT)AS Total_Credit_Limit
FROM SH.customers
GROUP BY COUNTRY_ID 
HAVING Total_Credit_Limit > 10000000
ORDER BY Total_Credit_Limit DESC;

16.Find the state that contributes the highest total credit limit to its country.

SELECT COUNTRY_ID,CUST_STATE_PROVINCE_ID,
  SUM(CUST_CREDIT_LIMIT)AS Total_Credit_Limit
FROM SH.customers
GROUP BY COUNTRY_ID,CUST_STATE_PROVINCE_ID
HAVING Total_Credit_Limit = (SELECT MAX(SUM(CUST_CREDIT_LIMIT)) FROM SH.CUSTOMERS 
     WHERE COUNTRY_ID = SH.CUSTOMERS.COUNTRY_ID
     GROUP BY CUST_STATE_PROVINCE_ID)

17.Show total credit limit per year of birth, sorted by total descending.

SELECT 
    EXTRACT(YEAR FROM CUST_YEAR_OF_BIRTH) AS YEAR_OF_BIRTH,
    SUM(CUST_CREDIT_LIMIT) AS TOTAL_CREDIT_LIMIT
FROM 
    SH.CUSTOMERS
GROUP BY 
    EXTRACT(YEAR FROM CUST_YEAR_OF_BIRTH)
ORDER BY 
    TOTAL_CREDIT_LIMIT DESC;




18.Identify customers who hold the maximum credit limit in their respective country.
 
 SELECT CUST_ID, COUNTRY_ID,CUST_CREDIT_LIMIT
 FROM SH.CUSTOMERS C
 WHERE CUST_CREDIT_LIMIT = (SELECT MAX(CUST_CREDIT_LIMIT)FROM SH.CUSTOMERS 
                              WHERE COUNTRY_ID=C.COUNTRY_ID);

19.Show the difference between maximum and average credit limit per country.

SELECT COUNTRY_ID, 
       MAX(CUST_CREDIT_LIMIT)AS TOTAL_CREDIT_LIMIT - AVG(CUST_CREDIT_LIMIT) AS MAX_AVG_DIFFERENCE
FROM SH.CUSTOMERS 
GROUP BY COUNTRY_ID;

20.Display the overall rank of each state based on its total credit limit (using GROUP BY + analytic rank).
 SELECT CUST_STATE_PROVINCE_ID, 
    SUM(CUST_CREDIT_LIMIT) AS TOTAL_CREDIT_LIMIT,
    RANK() OVER (ORDER BY SUM(CUST_CREDIT_LIMIT) DESC ) AS STATE_RANK
FROM SH.CUSTOMERS 
GROUP BY CUST_STATE_PROVINCE_ID 
ORDER BY STATE_RANK;