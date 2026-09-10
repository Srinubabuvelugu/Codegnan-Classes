create database It_company;

use it_company;

create table employees(
id int auto_increment primary key, 
name varchar(30),
dept varchar(20),
salary int unsigned
);

-- insert data into table 
insert into employees(name, dept, salary)
values("ravi", "IT", 45000),
	("ram", "IT", 45000),
	("sam", "IT", 50000),
	("siri", "hr", 38000),
	("mahi", "hr", 35000),
	("sasi", "IT", 55000),
	("sanju", "sales", 45000),
	("ritviik", "sales", 30000),
	("raju", "IT", 36000),
	("malli", "sales", 33000),
	("anju", "IT", 36000);
    
    
    
-- select employees table data
select * from employees;

-- find the average salary of employees
select avg(salary) as Avg_salary from employees;

-- find the employee details whose salary is morethan average salary of employees
select * from employees
where salary > 40727.2727;

select * from employees
where salary > (select avg(salary) as Avg_salary from employees);
    
-- get the maximum salary salary employee details
select * from employees
where salary = (select max(salary) from employees);
-- get the minimum salary employee details
select * from employees
where salary = (select min(salary) from employees);
-- get the employee details who belongs to 'Ravi's dept
select * from employees
where dept = (select dept from employees where name='ravi') and name != 'Ravi';

	
-- 2. Multi row subqueries
-- get the maximum and minimum salary employees details
select * from employees
where salary = (select max(salary) from employees) 
or
salary = (select min(salary) from employees);

-- return the employee details either they belongs to sasi's or ritvik's dept
select * from employees
where dept in (select dept from employees where name in ('sasi','ritviik'));

-- get the employees details whose salary is graterthan any one's sales dept salary
select * from employees
where salary > ANY(select salary from employees where dept ='sales');


-- subquery in select clause
select 10 as Total;
select (select max(salary) from employees);

-- sub query in having
-- find the each dept total salary
-- return the depts whose avg salary is graterthan the average salary of employees
select dept, avg(salary) as Total_salary from employees
group by dept
having avg(salary) > (select avg(salary) from employees);

-- sub query in from class
-- derived tables
select * from 
	(select dept, count(*) as Total_count from employees group by dept) 
as Employees_count_table
where total_count > 2;

-- nested query

