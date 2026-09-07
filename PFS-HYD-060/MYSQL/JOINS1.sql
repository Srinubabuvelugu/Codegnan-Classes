use classicmodels;

select * from customers;
select * from orders;
-- get the customer details who placed and order
select c.customernumber, customername, ordernumber from customers c
inner join orders o 
on c.customernumber = o.customernumber;

select DISTINCT c.customernumber, customername from customers c
inner join orders o 
on c.customernumber = o.customernumber;

-- GET THE CUSTOMER DETAILS WHOSE ORDER IS SHIPPED

select DISTINCT c.customernumber, customername, ORDERNUMBER from customers c
inner join orders o 
on c.customernumber = o.customernumber
WHERE O.STATUS = "SHIPPED";

select DISTINCT c.customernumber, customername from customers c
inner join orders o 
on c.customernumber = o.customernumber
WHERE O.STATUS = "SHIPPED";

SELECT * FROM ORDERS;
-- GET THE CUSTOMER DETAILS WHOSE ORDER IS CANCELLED
select  c.customernumber, customername from customers c
inner join orders o 
on c.customernumber = o.customernumber
WHERE O.STATUS = "CANCELLED";

-- EQUIE JOIN
SELECT C.CUSTOMERNUMBER, CUSTOMERNAME FROM CUSTOMERS C, ORDERS O 
WHERE C.CUSTOMERNUMBER = O.CUSTOMERNUMBER AND O.STATUS = "CANCELLED";

-- GET EACH CUSTOMERS TOTAL ODERS COUNT
select  c.customernumber, customername, COUNT(*) TOTAL_ORDERS from customers c
inner join orders o 
on c.customernumber = o.customernumber
GROUP BY C.CUSTOMERNUMBER
ORDER BY TOTAL_ORDERS DESC;

-- GET THE EACH CUSTOMER TOTAL SHIPPED ORDERS COUNT
select  c.customernumber, customername, COUNT(*) TOTAL_ORDERS from customers c
inner join orders o 
on c.customernumber = o.customernumber
WHERE O.STATUS = "SHIPPED"
GROUP BY C.CUSTOMERNUMBER
ORDER BY TOTAL_ORDERS DESC;


select  c.customernumber, customername, COUNT(*) TOTAL_ORDERS from customers c
inner join orders o 
on c.customernumber = o.customernumber
WHERE O.STATUS = "SHIPPED"
GROUP BY C.CUSTOMERNUMBER
HAVING COUNT(*) > 3
ORDER BY TOTAL_ORDERS DESC;


-- NATURAL JOIN 
-- GET THE ORDER PLACED CUSTOMER DETAILS
select distinct c.customernumber, customername from customers c
NATURAL join orders O;

SELECT * FROM EMPLOYEES;
select c.customernumber, customername, EMPLOYEENUMBER from customers c
NATURAL join  EMPLOYEES;

-- CROSS JOIN
select c.customernumber, customernamE from customers c
CROSS join  EMPLOYEES;