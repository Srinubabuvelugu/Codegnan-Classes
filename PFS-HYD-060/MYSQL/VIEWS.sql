-- views
use classicmodels;
select * from customers;
select * from orders;
-- get the customer details who placed an order by using subquery
select * from customers
where customernumber in (select customernumber from orders);

-- create a view, order placed customer details
CREATE VIEW ORDER_PLACED_CUSTOMERS AS
SELECT * FROM CUSTOMERS
WHERE CUSTOMERNUMBER IN (select customernumber from orders);
-- SELECTING VIEW DATA
SELECT * FROM ORDER_PLACED_CUSTOMERS;

-- SELECT SCHOOL DETABASE
USE SCHOOL;
SELECT * FROM STUDENTS;

-- CREATE VIEW WITH 6TH CLASS STUDENTS 
