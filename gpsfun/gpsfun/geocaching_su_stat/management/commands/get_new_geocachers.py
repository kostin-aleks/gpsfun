#!/usr/bin/env python
"""
NAME
     get_new_geocachers.py

DESCRIPTION
     Loads list of new geocachers and updates db table
"""
from django.core.management.base import BaseCommand
from django.db.models import Max
import requests
from gpsfun.main.GeoCachSU.models import Geocacher
from gpsfun.main.models import log, UpdateType
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_user_profile)


class Command(BaseCommand):
    """ Command """
    help = 'Loads list of new geocachers'

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
                last_uid = Geocacher.objects.all().aggregate(
                    last_uid=Max('uid'))['last_uid']

                for uid in range(last_uid, last_uid + 1000):
                    response = session.get(
                        f'http://www.geocaching.su/profile.php?uid={uid}')

                    geocacher = get_user_profile(uid, response.text)
                    if geocacher:
                        print(uid, geocacher.id, geocacher.nickname)

        log(UpdateType.gcsu_new_geocachers, 'OK')
        return 'List of geocachers has updated'
