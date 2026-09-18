create database bank;
use bank;

create table accounts(
	id int, 
	name varchar(30),
	amount int unsigned
);

insert into accounts(id, name, amount)
values(1001, "Remo", 5000),(1002, "Sumo", 10000), (1003, "Maruthi", 2000);


select * from accounts;

-- Transfer 2000 from 1001 to 1003
-- debit operation
update accounts set amount = amount - 2000
where id = 1001;
set Sql_safe_updates= 0;

select * from accounts;
-- Credit operation
update accounts set amount = amount + 2000
where id = 1003;


-- Implementing Transaction


update accounts set amount = amount + 2000
where id = 1005;

begin;
-- Transfer 2000 from 1001 to 1003
-- debit operation
update accounts set amount = amount - 2000
where id = 1002;

select * from accounts;
-- Credit operation
update accounts set amount = amount + 2000
where id = 1005;

commit;
rollback;



-- Transfer 2000 from 1002 to 1001
-- Transfer 2000  from 1002 to 1003
begin;

-- debit operation
update accounts set amount = amount - 2000
where id = 1002;

savepoint p1;
select * from accounts;
-- Credit operation
update accounts set amount = amount + 2000
where id = 1001;
savepoint p2;
-- debit operation
update accounts set amount = amount - 2000
where id = 1002;
savepoint p3;
select * from accounts;
-- Credit operation
update accounts set amount = amount + 2000
where id = 1005;
savepoint p4;


rollback to p2;
select * from accounts;