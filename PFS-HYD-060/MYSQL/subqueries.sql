create database company;

use company;

create table employees(
	id int not null primary key, 
    name varchar(30),
    dept varchar(20),
    salary int unsigned
);

insert into employees(id, name, dept, salary)
values(101, "ravi", "IT", 50),
	(102, "Ram", "IT", 45),
	(103, "sam", "IT", 42),
	(104, "sanju", "sales", 40),
	(105, "geethu", "sales", 35),
	(106, "divya", "sales", 38),
	(107, "mahi", "hr", 35),
	(108, "babu", "IT", 40);
    
select * from employees;

--
select avg(salary) from employees;

select * from employess
where salary > (average salary);
	
select * from employees
where salary > 40.62;

select * from employees
where salary > (select avg(salary) from employees);

-- get the employees details who belongs to 101's dept
select * from employees
where dept = (select dept from employees
				where id = 101);
                
-- get empoloyees details whose salary is morethan the 
--                          sales dept maximum salary
select * from employees
where salary > (select max(salary) from employees
				where dept = 'sales');

select * from employees;
-- get sales and hr dept employee details
select * from employees
where dept in ('sales', 'hr');

--  get the employees details who belomngs to either 104's or 107's dept
select * from employees 
where dept in (select dept from employees
				where id in (104, 107));
				
	
select * from employees 
where dept not in (select dept from employees
				where id in (104, 107));
                
-- Any and All Operator
-- Return the employees details whose salary is
--                       grater than any one's salary in sales dept
select * from employees 
where salary > any(select salary from employees
					where dept = 'sales');
                    
-- get the maximum salary employee details
select * from employees
order by salary desc
limit 1;

select * from employees
where salary = (select max(salary) from employees);

-- get minimum and maximum salary employee details
select * from employees
where salary = (select max(salary) from employees) or
		salary = (select min(salary) from employees);
        
-- nested subquery

--  get the employees details who belongs to either 104's or 107's dept
select * from employees 
where id in (select id from employees
				where dept in (select dept from employees 
								where id in (104, 107)
                                )
			);
            
            
            
-- return the dept's whose employee count is more than 1
select dept, count(*) as totalcount from employees
group by dept
having count(*) > 1;








select dept, totalcount 
from (select dept, count(*) as totalcount from employees
	group by dept) as Dept_emp_count
where totalcount > 1;


-- return depts whose avg salary is morethan sales dept avg salary
select dept , avg(salary) from employees
group by dept
having avg(salary) > (select avg(salary) from employees
						where dept = 'sales');



