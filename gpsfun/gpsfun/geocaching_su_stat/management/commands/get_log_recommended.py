#!/usr/bin/env python
"""
NAME
     get_log_recommended.py

DESCRIPTION
     Loads log of recommendations for all geocachers and updates db table
"""

import requests
from django.core.management.base import BaseCommand
from gpsfun.main.GeoCachSU.models import (Cach, LogRecommendCach, Geocacher)
from gpsfun.main.db_utils import get_object_or_none
from gpsfun.main.models import log, UpdateType
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_caches_data)


class Command(BaseCommand):
    """ Command """
    help = 'Update list of recommended caches for all geocachers'

    def handle(self, *args, **options):
        with requests.Session() as session:
            session.post(
                'https://geocaching.su',
                data=LOGIN_DATA
            )
            response = session.get('https://geocaching.su')
            if not logged(response.text):
                print('Authorization failed')
            else:
                ids = LogRecommendCach.objects.all().values_list(
                    'cacher_uid', flat=True)
                for uid in Geocacher.objects.exclude(uid__in=ids).values_list('uid', flat=True):
                    response = session.get(
                        'http://www.geocaching.su/site/popup/userstat.php',
                        params={'s': 3, 'uid': uid}
                    )
                    for (cid, any_x, any_y, any_z) in get_caches_data(response.text):
                        cache = get_object_or_none(Cach, pid=cid)

                        if cache:
                            LogRecommendCach.objects.get_or_create(cacher_uid=uid, cach_pid=cid)

        log(UpdateType.gcsu_logs_recommended, 'OK')
        return 'List of recommended caches has updated'
