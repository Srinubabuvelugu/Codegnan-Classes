-- set operators
use classicmodels;

select * from employees;
select * from orders;
select * from customers;

-- get the cutomernumbers who placed an order
(select customernumber from customers)
intersect
(select customernumber from orders);

(select customernumber from customers)
union all
(select customernumber from orders);

-- get customernumbers who didn't placed an order
(select customernumber from customers)
except
(select customernumber from orders);
select * from orders
where customernumber=124;




