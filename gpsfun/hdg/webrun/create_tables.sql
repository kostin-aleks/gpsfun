create table jobs(
       id serial NOT NULL PRIMARY KEY,
       command varchar(255) NOT NULL,
       args varchar(255) NOT NULL,
       secure_key varchar(32) UNIQUE NOT NULL,
       added timestamp with time zone NULL,
       started timestamp with time zone NULL,
       finished timestamp with time zone NULL,
       -- TODO: change to int
       worker_pid varchar(50),
       status varchar(50) NOT NULL -- TODO: add checkout 'wait', 'running', 'finished'
);

create table results(
       id serial NOT NULL PRIMARY KEY,
       job_id integer NOT NULL REFERENCES jobs (id) DEFERRABLE INITIALLY DEFERRED,
       results text NULL,
       error text NULL
);


create table files(
       id serial NOT NULL PRIMARY KEY,
       job_id integer NOT NULL REFERENCES jobs (id) DEFERRABLE INITIALLY DEFERRED,
       type varchar(20) NOT NULL, -- TODO: add checkout 'input', 'output'
       filename varchar(100) NULL, -- TODO: add unique with job_id
       url varchar(255) NULL,
       path varchar(255) NULL

);