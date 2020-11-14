select distinct LEFT(code, 2) from cach;

SELECT COUNT(*) FROM cach;

SELECT LEFT(code, 2) as type_, COUNT(*) 
FROM cach
GROUP BY type_;

SELECT LEFT(code, 2) as type_, YEAR(created_date) as year_, COUNT(*)
FROM cach
GROUP BY type_, year_;

SELECT COUNT(*) FROM cach WHERE YEAR(created_date)=2010;

SELECT LEFT(code, 2) as type_, YEAR(created_date) as year_, MONTH(created_date) as month_, COUNT(*)
FROM cach
WHERE YEAR(created_date)=2011
GROUP BY type_, year_, month_;



SELECT gc.pid, gc.nickname, gc.created_caches, COUNT(cc.id) as created_
FROM geocacher gc 
LEFT JOIN log_create_cach cc ON cc.author_pid=gc.pid
WHERE cc.id IS NOT NULL
GROUP BY gc.pid, gc.nickname, gc.created_caches
ORDER BY created_ desc 
LIMIT 20;

SELECT gc.pid, gc.nickname, gc.found_caches, COUNT(sc.id) as found_
FROM geocacher gc 
LEFT JOIN log_seek_cach sc ON sc.cacher_pid=gc.pid
WHERE sc.id IS NOT NULL
GROUP BY gc.pid, gc.nickname, gc.created_caches
ORDER BY found_ desc 
LIMIT 20;


SELECT gc.pid, gc.nickname, gc.created_caches, 
(SELECT COUNT(cc.id) FROM log_create_cach cc WHERE cc.author_pid=gc.pid) as created_,
(SELECT COUNT(sc.id) FROM log_seek_cach sc WHERE sc.cacher_pid=gc.pid) as found_
FROM geocacher gc 
ORDER BY created_ desc;

SELECT gc.pid, gc.nickname, gc.created_caches, 
(SELECT COUNT(cc.id) FROM log_create_cach cc WHERE cc.author_pid=gc.pid AND YEAR(created_date)=2010) as created_ ,
(SELECT COUNT(sc.id) FROM log_seek_cach sc WHERE sc.cacher_pid=gc.pid AND YEAR(found_date)=2010) as found_
FROM geocacher gc 
ORDER BY created_ desc
LIMIT 30;

DROP TABLE cach_stat;

CREATE TABLE `cach_stat` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `cach_id` int(10) unsigned NULL,
  `geocacher_id` int(10) unsigned NULL,
  `cach_pid` int(10) unsigned NULL,
  `recommend_count` int(10) unsigned NULL DEFAULT '0',
  `found_count` int(10) DEFAULT '0',
  `rank` float NULL,
  PRIMARY KEY (`id`),
  KEY `cach_id` (`cach_id`),
  KEY `cach_pid` (`cach_pid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


INSERT INTO cach_stat 
(cach_id, geocacher_id, cach_pid, recommend_count, found_count, rank)
SELECT cach.id, gcr.id, cach.pid, 
(SELECT COUNT(logrec.cacher_pid) FROM log_recommend_cach logrec WHERE logrec.cach_pid=cach.pid) as recommend_count,
(SELECT COUNT(logfnd.cacher_pid) FROM log_seek_cach logfnd WHERE logfnd.cach_pid=cach.pid) as found_count,
NULL
FROM cach
LEFT JOIN geocacher gcr ON cach.created_by_pid=gcr.pid
HAVING found_count > 0;

UPDATE cach_stat
SET rank = (POW(1+IFNULL(recommend_count,0),1.2)/(1 + IFNULL(found_count,0)/10.0)*100.0);

ALTER TABLE cach_stat ADD INDEX cach_pid (pid);
ALTER TABLE cach ADD INDEX pid (pid);
ALTER TABLE cach ADD INDEX country_code (country_code);
ALTER TABLE cach ADD INDEX admin_code (admin_code);
ALTER TABLE geocacher ADD INDEX country_iso3 (country_iso3);
ALTER TABLE geocacher ADD INDEX admin_code (admin_code);

SELECT cach_stat.pid, cach.code, cach.name, gc.nickname, cach_stat.recommend_count, cach_stat.found_count, 
(POW(1+IFNULL(cach_stat.recommend_count,0),1.2)/(1 + IFNULL(cach_stat.found_count,0)/10.0)*100.0) as indx
FROM cach_stat
LEFT JOIN cach ON cach_stat.pid=cach.pid
LEFT JOIN geocacher gc ON cach.created_by_pid=gc.pid
ORDER BY indx desc
LIMIT 100;

DELETE FROM cach_stat;

INSERT INTO cach_stat
SELECT cach.pid, 
(SELECT COUNT(logrec.cacher_pid) FROM log_recommend_cach logrec WHERE logrec.cach_pid=cach.pid) as recommend_count,
(SELECT COUNT(logfnd.cacher_pid) FROM log_seek_cach logfnd WHERE logfnd.cach_pid=cach.pid) as found_count 
FROM cach
HAVING found_count > 0;

-- opencaching.pl
SELECT ROUND(POW(1+IFNULL(cach_stat.recommend_count,0),2)/(1 + IFNULL(cach_stat.found_count,0)/10.0)*100.0) as indx,
 cach_stat.recommend_count as RC, cach_stat.found_count as FC, cach.code, cach.name, gc.nickname,
ROUND(cach.grade,2) as grade
FROM cach_stat
LEFT JOIN cach ON cach_stat.pid=cach.pid
LEFT JOIN geocacher gc ON cach.created_by_pid=gc.pid
ORDER BY indx desc
LIMIT 30;

-- Kostin
SELECT cach_stat.pid, cach.code, cach.name, gc.nickname, cach_stat.recommend_count, cach_stat.found_count, 
ROUND((1+IFNULL(cach_stat.recommend_count,0))/(1 + IFNULL(cach_stat.found_count,0)) * POW(1 + IFNULL(cach_stat.found_count,0),1)*1000) as indx
FROM cach_stat
LEFT JOIN cach ON cach_stat.pid=cach.pid
LEFT JOIN geocacher gc ON cach.created_by_pid=gc.pid
ORDER BY indx desc
LIMIT 100;