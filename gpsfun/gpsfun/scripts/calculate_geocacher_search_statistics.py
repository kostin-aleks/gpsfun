#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time
from datetime import date
from gpsfun.main.db_utils import execute_query
from gpsfun.main.models import log
from gpsfun.main.GeoCachSU.models import Cach, CachStat
import django
django.setup()


def main():
    start = time()

    for cache in Cach.objects.all():
        cache_stat, created = CachStat.objects.get_or_create(
            cach=cache,
            cach_pid=cache.pid)
        cache_stat.calculate_points()

    sql = """
    insert into geocacher_search_stat
    (geocacher_id, geocacher_pid, country, region)
    select g.id, g.pid, c.name, gcs.name
    from geocacher g
    left join geocacher_search_stat gss
        on g.pid = gss.geocacher_pid
    left join geo_country c
        on g.country_iso3 = c.iso3
    left join geo_country_subject gcs
        on c.iso = gcs.country_iso and g.admin_code = gcs.code
    where gss.geocacher_pid is null
    """
    execute_query(sql)

    sql = """
        update geocacher_search_stat gss
        set
        points=(
            select ROUND(sum(IFNULL(cs.points, 0))) as points_sum
            from  log_seek_cach lsc
            left join cach_stat cs on lsc.cach_pid = cs.cach_pid
            where lsc.cacher_pid = gss.geocacher_pid
        ),
        year_points=(
            select ROUND(sum(IFNULL(cs.points, 0))) as points_sum
            from  log_seek_cach lsc
            left join cach_stat cs on lsc.cach_pid = cs.cach_pid
            where YEAR(lsc.found_date)=%s and
                  lsc.cacher_pid = gss.geocacher_pid
        )
    """ % date.today().year
    execute_query(sql)

    elapsed = time() - start
    print "Elapsed time -->", elapsed
    log('gcsu_rating', 'OK')

if __name__ == '__main__':
    main()
