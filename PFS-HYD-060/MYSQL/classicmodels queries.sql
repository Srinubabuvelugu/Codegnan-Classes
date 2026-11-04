
use classicmodels;
select * from payments;

-- get year, month, date from paymentdate
select paymentdate, year(paymentdate), month(paymentdate),
extract(day from paymentdate)
from payments;

-- 2. get the 2004 year payments
select * from payments
where year(paymentdate) =2004;
-- 3. get the payments before 2003 - 09 - 01
select * from payments
where paymentdate < '2003-09-01';
-- 4. get the payments in may 2003(descending order as per the amount)
select * from payments
where paymentdate between '2003-05-01'and '2003-5-31';

select * from payments
where year(paymentdate) = 2003 and  month(paymentdate) = 5;
-- 5. Get 2003's jan and feb records
select * from payments
where paymentdate between '2003-01-01'and '2003-02-28';

select * from payments
where year(paymentdate) = 2003 and  
	(month(paymentdate) = 1 or month(paymentdate) = 2);
    
select * from payments
where year(paymentdate) = 2003 and  
	(month(paymentdate) in (1,2));
-- 6. Find the total payments
select count(*) as Total_payments from payments;
-- 7. Find the each year total payments
select year(paymentdate), count(*) as Total_payments from payments
group by year(paymentdate);

-- 8. Find the total payments of every month in year
select year(paymentdate) as Year,month(paymentdate) as Month, count(*) as Total_payments from payments
group by year(paymentdate), month(paymentdate)
order by year asc, month desc;

-- 9. get the total amount in descnding order of every every year(round to 2 decima values)
select year(paymentdate), round(sum(amount), 2) as Total_amount from payments
group by year(paymentdate)
order by total_amount desc;
-- 10. which year have more payments
select year(paymentdate) from payments
group by year(paymentdate)
order by count(*) desc
limit 1;
-- 11. get total payments in every month of 2004
select month(paymentdate), count(*) as Total_Payments from payments
where year(paymentdate) = 2004
group by month(paymentdate);
-- 12. get top3 total payment months in 2003
select month(paymentdate), count(*) as Total_Payments from payments
where year(paymentdate) = 2003
group by month(paymentdate)
order by total_payments desc
limit 3;