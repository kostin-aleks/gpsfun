#!/usr/bin/env python
"""
NAME
     get_new_log_created.py

DESCRIPTION
     Loads list of last created caches and updates db table
"""
import requests
from django.core.management.base import BaseCommand
from gpsfun.main.GeoCachSU.models import (Cach, LogCreateCach)
from gpsfun.main.db_utils import get_object_or_none
from gpsfun.main.models import log, UpdateType
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_caches_data, get_geocachers_uids)


class Command(BaseCommand):
    """ Command """
    help = 'Update list of last created caches for all geocachers'

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
                response = session.get(
                    'http://www.geocaching.su/',
                    params={'pn': 107}
                )

                for uid in get_geocachers_uids(response.text):
                    response = session.get(
                        'http://www.geocaching.su/site/popup/userstat.php',
                        params={'s': 1, 'uid': uid}
                    )

                    for (cid, found_date, grade, coauthor) in get_caches_data(response.text):
                        cache = get_object_or_none(Cach, pid=cid)

                        if cache:
                            the_log, created = LogCreateCach.objects.get_or_create(
                                author_uid=uid,
                                cach_pid=cid)
                            if created:
                                the_log.created_date = cache.created_date
                                the_log.coauthor = coauthor
                                the_log.save()

        log(UpdateType.gcsu_new_logs_created, 'OK')
        return 'List of created caches has updated'
