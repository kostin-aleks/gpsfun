#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
     get_new_log_found.py

DESCRIPTION
     Loads new log of found caches and updates db table
"""
import requests
from django.core.management.base import BaseCommand
from gpsfun.main.GeoCachSU.models import (Cach, LogSeekCach)
from gpsfun.DjHDGutils.dbutils import get_object_or_none
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_caches_data, get_geocachers_uids)


class Command(BaseCommand):
    help = 'Load logs for last found caches'

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
                r = session.get(
                    'http://www.geocaching.su/',
                    params={'pn': 107}
                )
                for uid in get_geocachers_uids(r.text):
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
                            if created:
                                the_log.found_date = found_date
                                the_log.grade = grade
                                the_log.save()

        log(UPDATE_TYPE.gcsu_new_logs_found, 'OK')
        return 'List of found caches has updated'
