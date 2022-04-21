#!/usr/bin/env python
"""
NAME
     get_log_created.py

DESCRIPTION
     Loads list of created caches and updates db table
"""
import requests
from django.core.management.base import BaseCommand
from gpsfun.main.GeoCachSU.models import (Cach, LogCreateCach, Geocacher)
from gpsfun.DjHDGutils.dbutils import get_object_or_none
from gpsfun.main.models import log, UpdateType
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_caches_data)


class Command(BaseCommand):
    """ Command """
    help = 'Update list of created caches for all geocachers'

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
                ids = LogCreateCach.objects.all().values_list('author_uid', flat=True)
                for uid in Geocacher.objects.exclude(
                    uid__in=ids).values_list('uid', flat=True):
                    response = session.get(
                        'http://www.geocaching.su/site/popup/userstat.php',
                        params={'s': 1, 'uid': uid}
                    )

                    for (cid, found_date, grade, coauthor) in \
                        get_caches_data(uid, response.text):
                        cache = get_object_or_none(Cach, pid=cid)

                        if cache:
                            the_log, created = LogCreateCach.objects.get_or_create(
                                author_uid=uid,
                                cach_pid=cid)

                            the_log.created_date = cache.created_date
                            the_log.coauthor = coauthor
                            the_log.save()

        log(UpdateType.gcsu_logs_created, 'OK')
        return 'List of created caches has updated'
