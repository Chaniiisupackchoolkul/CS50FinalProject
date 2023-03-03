
-- CREATE TABLE users (
-- 	id 			INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
-- 	username 	TEXT NOT NULL,
-- 	hash	TEXT NOT NULL
-- );

-- CREATE TABLE questions (
-- 	id 			INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
-- 	subject		TEXT NOT NULL,
-- 	level 		TEXT NOT NULL,
-- 	question	TEXT NOT NULL,
-- 	choice		TEXT NOT NULL,
-- 	answer		INTEGER NOT NULL
-- );

-- CREATE TABLE exams (
-- 	id 			INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
-- 	name		TEXT NOT NULL,
-- 	subject		TEXT NOT NULL,
-- 	level 		TEXT NOT NULL,
-- 	times		NUMERIC NOT NULL DEFAULT 600
-- );

-- CREATE TABLE exams_set (
-- 	id 			INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
-- 	exams_id	INTEGER NOT NULL,
-- 	question_id	INTEGER NOT NULL
-- );

-- CREATE TABLE exams_history (
-- 	id 			INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
-- 	user_id		INTEGER NOT NULL,
-- 	exams_id	INTEGER NOT NULL,
-- 	created_time TEXT NOT NULL,
-- 	score		NUMERIC NOT NULL DEFAULT 0
-- );

-- insert into `users` (`username`, `password`) values ("mrkad", "1234");
-- pip install -r requirements.txt


-- pages
-- 	login,
-- 	index 	search exams select subject + level
-- 	exam	Start exams (counting)
-- 	history view score + answer (modal)

-- select q.*
-- FROM questions q
-- join exams_set ex on ex.question_id=q.id
-- where ex.exams_id=1;

-- .schema
-- select * from exams_history;

-- select subject FROM exams group by subject;

-- admin
-- 	create 	question
-- 	create 	exams
-- 	add		question to exams

-- finalProjectPramary = 	Primary school
-- finalProjectMid			Junior high School
-- finalProjectHeight		Senior high School

-- eng-ps
-- eng-Junior
-- eng-high

-- insert into exams (name, subject, level) values ('P-No.1','english','Senior high School');
-- insert into exams (name, subject, level) values ('P-No.2','english','Senior high School');
-- insert into exams (name, subject, level) values ('P-No.3','english','Senior high School');
-- insert into exams (name, subject, level) values ('P-No.4','english','Senior high School');
-- insert into exams (name, subject, level) values ('P-No.5','english','Senior high School');
-- insert into exams (name, subject, level) values ('P-No.6','english','Senior high School');
-- insert into exams (name, subject, level) values ('P-No.7','english','Senior high School');
-- insert into exams (name, subject, level) values ('P-No.8','english','Senior high School');
-- insert into exams (name, subject, level) values ('P-No.9','english','Senior high School');
-- insert into exams (name, subject, level) values ('P-No.10','english','Senior high School');

-- delete from exams where id >87;
-- delete from exams_set where exams_id >87;

select * from exams where subject='english';

-- 138-147

-- insert into exams_set (exams_id, question_id)
select "143", q.id from questions q
where level='Senior high School'
and subject='english'
and q.id not in (
    select question_id from exams_set
)
limit 10;

select * from users;


-- select * from exams_set where id=4;
-- select count(*) from questions where subject='english' and level='Primary school';
-- select count(*) from questions where subject='english' and level='Junior high School';
-- select count(*) from questions where subject='english' and level='Senior high School';

