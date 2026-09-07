-- 
use classicmodels;

-- 1.get the cuurent date, and current time
select now();
-- 2. get the current timestamp
select current_timestamp(), now();
-- 3. get the current timestamp format as (day-month-year 12h fromat time)
select date_format(now(), "%d-%m-%Y %h:%i:%s %p") as Current_tim;
-- 4. how old are you (in terms of years)
select floor(datediff(now(), "2025-09-01")/365);

select * from orders;
-- 5. get the order details which order comments is not null
select * from orders
where comments is not null;
-- 6. get the order details which order is not able to
--                              deliver within required date
select * from orders
where shippeddate > requireddate;
-- 7. find the how many days taken for every delivary (in descending order)
select ordernumber, orderdate, shippeddate, 
		Datediff(shippeddate, orderdate) as Deleviry_time
from orders
order by deleviry_time desc;
-- 8. find the each year total successful deleviries count
select * from orders;
select year(orderdate), count(*) as Total_count from orders
where status = "Shipped"
group by year(orderdate);



