DELETE FROM geocacher_stat;

INSERT INTO geocacher_stat
(geocacher_id, uid, created_count, found_count, av_grade, av_his_cach_grade, country, region)
SELECT geocacher.id, geocacher.uid,
NULL, NULL, NULL, NULL,
gc.name,
gcs.name
FROM geocacher
LEFT JOIN geo_country gc ON geocacher.country_iso3=gc.iso3
LEFT JOIN geo_country_subject gcs ON gc.iso=gcs.country_iso AND geocacher.admin_code=gcs.code;



UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT logcrt.author_uid as author_uid, COUNT(logcrt.id) as cnt
    FROM log_create_cach logcrt
    GROUP BY logcrt.author_uid
) as tt ON gstat.uid = tt.author_uid
SET gstat.created_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.cacher_uid as uid, COUNT(log_.id) as cnt
    FROM log_seek_cach log_
    GROUP BY log_.cacher_uid
) as tt ON gstat.uid = tt.uid
SET gstat.found_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.cacher_uid as uid, AVG(log_.grade) as grade
    FROM log_seek_cach log_
    GROUP BY log_.cacher_uid
) as tt ON gstat.uid = tt.uid
SET gstat.av_grade=tt.grade;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT g.uid as uid, AVG(log_.grade) as grade
    FROM log_seek_cach log_
    LEFT JOIN cach ON log_.cach_pid=cach.pid
    LEFT JOIN geocacher g ON cach.author_id = g.id
    GROUP BY cach.author_id
) as tt ON gstat.uid = tt.uid
SET gstat.av_his_cach_grade=tt.grade;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.author_uid as author_uid, COUNT(log_.id) as cnt
    FROM log_create_cach log_
    LEFT JOIN cach ON log_.cach_pid=cach.pid
    WHERE cach.type_code IN (%s)
    GROUP BY log_.author_uid
) as tt ON gstat.uid = tt.author_uid
SET gstat.vi_created_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.cacher_uid as uid, COUNT(log_.id) as cnt
    FROM log_seek_cach log_
    LEFT JOIN cach ON log_.cach_pid=cach.pid
    WHERE cach.type_code IN (%s)
    GROUP BY log_.cacher_uid
) as tt ON gstat.uid = tt.uid
SET gstat.vi_found_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.author_uid as author_uid, COUNT(log_.id) as cnt
    FROM log_create_cach log_
    WHERE YEAR(created_date) = YEAR(NOW())
    GROUP BY log_.author_uid
) as tt ON gstat.uid = tt.author_uid
SET gstat.curr_created_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.cacher_uid as uid, COUNT(log_.id) as cnt
    FROM log_seek_cach log_
    WHERE YEAR(found_date) = YEAR(NOW())
    GROUP BY log_.cacher_uid
) as tt ON gstat.uid = tt.uid
SET gstat.curr_found_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.author_uid as author_uid, COUNT(log_.id) as cnt
    FROM log_create_cach log_
    LEFT JOIN cach ON log_.cach_pid=cach.pid
    WHERE YEAR(log_.created_date) = YEAR(NOW())
      AND  cach.type_code IN (%s)
    GROUP BY log_.author_uid
) as tt ON gstat.uid = tt.author_uid
SET gstat.vi_curr_created_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.cacher_uid as uid, COUNT(log_.id) as cnt
    FROM log_seek_cach log_
    LEFT JOIN cach ON log_.cach_pid=cach.pid
    WHERE YEAR(found_date) = YEAR(NOW())
      AND cach.type_code IN (%s)
    GROUP BY log_.cacher_uid
) as tt ON gstat.uid = tt.uid
SET gstat.vi_curr_found_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.author_uid as author_uid, COUNT(log_.id) as cnt
    FROM log_create_cach log_
    LEFT JOIN cach ON log_.cach_pid=cach.pid
    WHERE NOT cach.type_code IN (%s)
    GROUP BY log_.author_uid
) as tt ON gstat.uid = tt.author_uid
SET gstat.tr_created_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.cacher_uid as uid, COUNT(log_.id) as cnt
    FROM log_seek_cach log_
    LEFT JOIN cach ON log_.cach_pid=cach.pid
    WHERE NOT cach.type_code IN (%s)
    GROUP BY log_.cacher_uid
) as tt ON gstat.uid = tt.uid
SET gstat.tr_found_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.author_uid as author_uid, COUNT(log_.id) as cnt
    FROM log_create_cach log_
    LEFT JOIN cach ON log_.cach_pid=cach.pid
    WHERE YEAR(log_.created_date) = YEAR(NOW())
      AND NOT cach.type_code IN (%s)
    GROUP BY log_.author_uid
) as tt ON gstat.uid = tt.author_uid
SET gstat.tr_curr_created_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.cacher_uid as uid, COUNT(log_.id) as cnt
    FROM log_seek_cach log_
    LEFT JOIN cach ON log_.cach_pid=cach.pid
    WHERE YEAR(found_date) = YEAR(NOW())
      AND  NOT cach.type_code IN (%s)
    GROUP BY log_.cacher_uid
) as tt ON gstat.uid = tt.uid
SET gstat.tr_curr_found_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.author_uid as author_uid, COUNT(log_.id) as cnt
    FROM log_create_cach log_
    WHERE YEAR(created_date) = YEAR(NOW())-1
    GROUP BY log_.author_uid
) as tt ON gstat.uid = tt.author_uid
SET gstat.last_created_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.cacher_uid as uid, COUNT(log_.id) as cnt
    FROM log_seek_cach log_
    WHERE YEAR(found_date) = YEAR(NOW())-1
    GROUP BY log_.cacher_uid
) as tt ON gstat.uid = tt.uid
SET gstat.last_found_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.author_uid as author_uid, COUNT(log_.id) as cnt
    FROM log_create_cach log_
    LEFT JOIN cach ON log_.cach_pid=cach.pid
    WHERE (YEAR(log_.created_date) = YEAR(NOW())-1)
      AND cach.type_code IN (%s)
    GROUP BY log_.author_uid
) as tt ON gstat.uid = tt.author_uid
SET gstat.vi_last_created_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.cacher_uid as uid, COUNT(log_.id) as cnt
    FROM log_seek_cach log_
    LEFT JOIN cach ON log_.cach_pid=cach.pid
    WHERE (YEAR(found_date) = YEAR(NOW())-1)
      AND cach.type_code IN (%s)
    GROUP BY log_.cacher_uid
) as tt ON gstat.uid = tt.uid
SET gstat.vi_last_found_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.author_uid as author_uid, COUNT(log_.id) as cnt
    FROM log_create_cach log_
    LEFT JOIN cach ON log_.cach_pid=cach.pid
    WHERE (YEAR(log_.created_date) = YEAR(NOW())-1)
      AND  NOT cach.type_code IN (%s)
    GROUP BY log_.author_uid
) as tt ON gstat.uid = tt.author_uid
SET gstat.tr_last_created_count=tt.cnt;

UPDATE geocacher_stat gstat
LEFT JOIN (
    SELECT log_.cacher_uid as uid, COUNT(log_.id) as cnt
    FROM log_seek_cach log_
    LEFT JOIN cach ON log_.cach_pid=cach.pid
    WHERE (YEAR(found_date) = YEAR(NOW())-1)
      AND NOT cach.type_code IN (%s)
    GROUP BY log_.cacher_uid
) as tt ON gstat.uid = tt.uid
SET gstat.tr_last_found_count=tt.cnt;

--DELETE FROM geocacher_stat
--WHERE found_count IS NULL OR found_count < 1;




