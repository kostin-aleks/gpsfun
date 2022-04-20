""" sql queries """

RAWSQL = {
    'all_types_by_author': """
    select distinct c.type_code
    from log_seek_cach l
    left join cach c on l.cach_pid = c.pid
    left join geocacher g on c.author_id = g.id
    where c.pid is not null and g.uid=%s
    order by c.type_code
    """,

    'all_types_by_cacher': """
    select distinct c.type_code
    from log_seek_cach l
    left join cach c on l.cach_pid = c.pid
    where c.pid is not null and l.cacher_uid=%s
    order by c.type_code
    """,

    'geocachers_found_my_caches': """
    select cacher_uid, g.nickname,
           count(l.id) as cnt,
           max(found_date) as last_found_date,
           avg(l.grade) as av_grade
    from log_seek_cach l
    left join cach c on l.cach_pid = c.pid
    left join geocacher g on l.cacher_uid = g.uid
    left join geocacher g1 on c.author_id = g1.id
    where c.pid is not null and g1.uid=%s
    group by cacher_uid, g.nickname
    order by cnt desc
    """,

    'found_by_me_caches_owners': """
    select g.uid, g.nickname,
           count(l.id) as cnt,
           max(found_date) as last_found_date,
           avg(l.grade) as av_grade
    from log_seek_cach l
    left join cach c on l.cach_pid = c.pid
    left join geocacher g on c.author_id = g.id
    where c.pid is not null and l.cacher_uid=%s
    group by g.uid, g.nickname
    order by cnt desc
    """,

    'found_my_caches_by_cacher_type': """
    select cacher_uid, c.type_code, count(l.id) as cnt
    from log_seek_cach l
    left join cach c on l.cach_pid = c.pid
    left join geocacher g on c.author_id = g.id
    where c.pid is not null and g.uid=%s
    group by cacher_uid, c.type_code
    """,

    'i_found_caches_by_cacher_type': """
    select g.uid, c.type_code, count(l.id) as cnt
    from log_seek_cach l
    left join cach c on l.cach_pid = c.pid
    left join geocacher g on c.author_id = g.id
    where c.pid is not null and l.cacher_uid=%s
    group by g.uid, c.type_code
    """,

    'count_cacher_recommends': """
    select cacher_uid, count(l.id) as cnt
    from log_recommend_cach l
    left join cach c on l.cach_pid = c.pid
    left join geocacher g on c.author_id = g.id
    where c.pid is not null and g.uid=%s
    group by cacher_uid
    """,

    'count_my_recommends': """
    select g.uid, count(l.id) as cnt
    from log_recommend_cach l
    left join cach c on l.cach_pid = c.pid
    left join geocacher g on c.author_id = g.id
    where c.pid is not null and l.cacher_uid=%s
    group by g.uid
    """,

    'found_by_years': """
    SELECT YEAR(found_date), MONTH(found_date), COUNT(*) as cnt
    FROM log_seek_cach
    WHERE found_date IS NOT NULL
    GROUP BY YEAR(found_date), MONTH(found_date)
    """,

    'real_created_by_years': """
    SELECT YEAR(lcc.created_date), MONTH(lcc.created_date), COUNT(*) as cnt
    FROM log_create_cach lcc
    LEFT JOIN cach ON lcc.cach_pid=cach.pid
    WHERE lcc.created_date IS NOT NULL AND
    cach.type_code IN ('TR','MS')
    GROUP BY YEAR(lcc.created_date), MONTH(lcc.created_date)
    """,

    'caches_created_by_years': """
    SELECT YEAR(created_date), MONTH(created_date), COUNT(*) as cnt
    FROM log_create_cach
    WHERE created_date IS NOT NULL
    GROUP BY YEAR(created_date), MONTH(created_date)
    """,

    'virt_created_by_years': """
    SELECT YEAR(lcc.created_date), MONTH(lcc.created_date), COUNT(*) as cnt
    FROM log_create_cach lcc
    LEFT JOIN cach ON lcc.cach_pid=cach.pid
    WHERE lcc.created_date IS NOT NULL AND
    cach.type_code IN ('VI','MV')
    GROUP BY YEAR(lcc.created_date), MONTH(lcc.created_date)""",

    'geocacher_one_year_found_by_months': """
    SELECT MONTH(found_date) as month_, COUNT(l.id) as cnt
    FROM log_seek_cach as l
    WHERE l.cacher_uid=%s AND YEAR(l.found_date)=%s
    GROUP BY MONTH(found_date)
    """,

    'geocacher_one_year_created_by_months': """
    SELECT MONTH(created_date) as month_, COUNT(l.id) as cnt
    FROM log_create_cach as l
    WHERE l.author_uid=%s AND YEAR(l.created_date)=%s
    GROUP BY MONTH(created_date)
    """,

    'first_year_found': """
    SELECT MIN(YEAR(found_date))
    FROM log_seek_cach
    WHERE cacher_uid=%s
    """,

    'first_year_created': """
    SELECT MIN(YEAR(created_date))
    FROM log_create_cach
    WHERE author_uid=%s
    """,

    'geocacher_found_caches_by_type': """
    SELECT cach.type_code, COUNT(l.id) as cnt
    FROM log_seek_cach as l
    LEFT JOIN cach ON l.cach_pid=cach.pid
    WHERE l.cacher_uid=%s AND cach.pid IS NOT NULL
    GROUP BY cach.type_code
    ORDER BY cnt desc
    """,

    'geocacher_created_caches_by_type': """
    SELECT cach.type_code, COUNT(l.id) as cnt
    FROM log_create_cach as l
    LEFT JOIN cach ON l.cach_pid=cach.pid
    WHERE l.author_uid=%s AND cach.pid IS NOT NULL
    GROUP BY cach.type_code
    ORDER BY cnt desc
    """,

    'set_caches_grades': """
    UPDATE cach
    LEFT JOIN (
    SELECT cach_pid, AVG(grade) as avg_grade
    FROM log_seek_cach
    GROUP BY cach_pid
    ) as tt ON cach.pid = tt.cach_pid
    SET cach.grade = tt.avg_grade
    """,
}
