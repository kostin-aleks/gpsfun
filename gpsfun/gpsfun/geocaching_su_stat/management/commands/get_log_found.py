#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
     get_log_found.py

DESCRIPTION
     Loads log of countries with ISO codes and updates db table
"""
import requests
from django.core.management.base import BaseCommand
from gpsfun.main.GeoCachSU.models import (Cach, LogSeekCach, Geocacher)
from gpsfun.DjHDGutils.dbutils import get_object_or_none
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_caches_data)


class Command(BaseCommand):
    help = 'Load logs for found caches'

    def handle(self, *args, **options):
        with requests.Session() as session:
            post = session.post(
                'https://geocaching.su',
                data=LOGIN_DATA
            )

            r = session.get('https://geocaching.su')
            if not logged(r.text):
                print('Authorization failed')
            else:
                ids = LogSeekCach.objects.all().values_list('cacher_uid', flat=True)
                for uid in Geocacher.objects.exclude(
                        uid__in=ids).values_list('uid', flat=True)[:2000]:
                    r = session.get(
                        'http://www.geocaching.su/site/popup/userstat.php',
                        params={'s': 2, 'uid': uid}
                    )
                    for (cid, found_date, grade, x) in get_caches_data(uid, r.text):
                        cache = get_object_or_none(Cach, pid=cid)

                        if cache and found_date:
                            the_log, created = LogSeekCach.objects.get_or_create(
                                cacher_uid=uid,
                                cach_pid=cid)

                            the_log.found_date = found_date
                            the_log.grade = grade
                            the_log.save()



        log(UPDATE_TYPE.gcsu_logs_found, 'OK')
        return 'List of found caches has updated'
