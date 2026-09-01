use school;
desc students;

-- insert records into students table
insert into students values(101,"ravi", "male",6, 11, "2015-01-01");

insert into students values(101,"ravi", "male", 11, "2015-01-01");

-- approch 2
insert into students(name, gender, class, age, date_of_birth)
values("babu", "male",7, 12, "2014-01-01"),
		("geethu", "female",8, 13, "2013-01-01");
        
-- fetch table data 
SELECT * FROM STUDENTS;
DESC STUDENTS;
insert into students(NAME, gender, class, age, date_of_birth)
values("PRERANA", "Female",5, 3, "2014-01-");

-- 
create table marks(
	stdid int, 
    s1 tinyint, 
    s2 tinyint,
    s3 tinyint,
    percentage float(4,2),
    foreign key(stdid) references students(stdid)
);

-- insert records into marks
INSERT INTO MARKS(STDID, S1, S2, S3)
VALUES(101,95,93,94),
	(102, 85, 86, 87);
    
    
INSERT INTO MARKS(STDID, S1, S2, S3, PERCENTAGE)
VALUES(105,95,93,94, 94.00);
SELECT * FROM MARKS;
-- UPDATE 5 MARKS FOR 101 STUDENT FOR S1 SUBJECT
SELECT * FROM MARKS 
WHERE STDID = 101;

UPDATE MARKS SET S1 = S1 + 5
WHERE STDID = 101;

SET SQL_SAFE_UPDATES = 0;


-- UPDATE 5 MARKS FOR 102 STUDENT FOR S1 AND S2 SUBJECT
SELECT * FROM MARKS
WHERE STDID = 102;
TRUNCATE TABLE MARKS;
-- UPDATE PERCENTAGE COLUMN AS DERIVED COLUMN
ALTER TABLE MARKS MODIFY COLUMN PERCENTAGE FLOAT(4,2) 
				generated always AS ((S1+S2+S3)/3) STORED;


SELECT * FROM MARKS;
UPDATE MARKS SET S1 = S1 + 5, S2 = S2+ 5
WHERE STDID = 102;

-- ADD TOTAL_MARKS  COLUMN TO MARKS TABLE
ALTER TABLE MARKS ADD COLUMN TOTAL_MARKS INT 
			GENERATED ALWAYS AS (S1+S2+S3) STORED AFTER S3;
SELECT * FROM MARKS;






use school;

select * from students;
insert into students(name, gender, class, age, date_of_birth)
values("sam", "male",7, 12, "2014-05-01"),
		("sashi", "female",9, 14, "2012-06-01"),
        ("sitha", "female",9, 14, "2012-06-01"),
        ("mahi", "male",7, 13, "2013-11-01"),
        ("puspa", "female",9, 14, "2012-06-01"),
        ("sashi", "female",8, 14, "2012-09-01"),
        ("rohit", "male",9, 14, "2012-06-01"),
        ("punth", "male",8, 14, "2012-08-01"),
        ("raj", "male",6, 11, "2015-04-01"),
        ("ram", "male",9, 14, "2012-07-01"),
        ("ravi", "male",10, 15, "2011-07-01");


select * from students;

-- select id and name from students
select stdid, name from students;
-- create backup table for students
CREATE TABLE STUDENTS_BACKUP_TABLE AS
SELECT * FROM STUDENTS;

SELECT * FROM STUDENTS_BACKUP_TABLE;
DESC STUDENTS_BACKUP_TABLE;

-- CREATE A STUDENT INFO TABLE (ID, NAME, CLASS)
CREATE TABLE STUDENT_INFO AS
SELECT STDID, NAME AS STDNAME, CLASS FROM STUDENTS;

SELECT * FROM STUDENT_INFO;

-- CREATE A TABLE 6 CLASS STUDENTS DATA
CREATE TABLE CLASS6 AS
SELECT STDID, NAME FROM STUDENTS
WHERE CLASS = 6;

SELECT * FROM CLASS6;

-- CREATE NEW TABLE STRUCTURE FROM AND EXISTING TABLE STRUCTURE
CREATE TABLE STUDENTS1 AS
SELECT * FROM STUDENTS 
WHERE 1 = 0;

SELECT * FROM STUDENTS1;

CREATE TABLE STUDENTS2 LIKE STUDENTS;
SELECT * FROM STUDENTS2;

