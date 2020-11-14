DELETE FROM cach_stat;

INSERT INTO cach_stat
(cach_id, geocacher_id, cach_pid, recommend_count, found_count, rank)
SELECT cach.id, gcr.id, cach.pid,
(SELECT COUNT(logrec.cacher_uid) FROM log_recommend_cach logrec WHERE logrec.cach_pid=cach.pid) as recommend_count,
(SELECT COUNT(logfnd.cacher_uid) FROM log_seek_cach logfnd WHERE logfnd.cach_pid=cach.pid) as found_count,
NULL
FROM cach
LEFT JOIN geocacher gcr ON cach.author_id=gcr.id
WHERE gcr.id IS NOT NULL
HAVING found_count > 0;

UPDATE cach_stat
SET rank = (POW(1+IFNULL(recommend_count,0),1.2)/(1 + IFNULL(found_count,0)/10.0)*100.0);
