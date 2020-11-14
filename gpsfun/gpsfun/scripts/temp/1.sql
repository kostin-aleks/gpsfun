select 
YEAR(ls.found_date), count(ls.id) 
from log_seek_cach ls
left join  cach on ls.cach_pid=cach.pid
where cach.type_code IN ('VI', 'MV')
group by YEAR(ls.found_date);

select 
YEAR(ls.found_date), count(ls.id) 
from log_seek_cach ls
left join  cach on ls.cach_pid=cach.pid
where cach.type_code IN ('TR', 'MS')
group by YEAR(ls.found_date);



select ls.cacher_pid, YEAR(ls.found_date), count(ls.id) as cnt
from log_seek_cach ls
group by ls.cacher_pid, YEAR(ls.found_date)
order by ls.cacher_pid;


create table geocacher_seek_caches
as
select ls.cacher_pid as cacher_pid, cach.type_code as type_code, YEAR(ls.found_date) as year_, count(ls.id) as count_
from log_seek_cach ls
left join  cach on ls.cach_pid=cach.pid
group by ls.cacher_pid, cach.type_code, YEAR(ls.found_date);

alter table geocacher_seek_caches add INDEX cacher (cacher_pid);
alter table geocacher_seek_caches add INDEX type_code (type_code);

select year_, count(distinct cacher_pid) from geocacher_seek_caches group by year_; 

