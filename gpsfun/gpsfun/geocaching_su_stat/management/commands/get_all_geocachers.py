#!/usr/bin/env python
"""
NAME
     get_all_geocachers.py

DESCRIPTION
     Loads list of all geocachers and updates db table
"""
from django.core.management.base import BaseCommand
import requests
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_user_profile)


class Command(BaseCommand):
    """ Command """
    help = 'Loads list of all geocachers'

    def handle(self, *args, **options):
        with requests.Session() as session:
            session.post(
                'https://geocaching.su',
                data=LOGIN_DATA,
            )

            response = session.get('https://geocaching.su')
            if not logged(response.text):
                print('Authorization failed')
            else:
                for uid in range(200000):
                    response = session.get(
                        f'http://www.geocaching.su/profile.php?uid={uid}')
                    geocacher = get_user_profile(uid, response.text)
                    if geocacher:
                        print(uid, geocacher.id, geocacher.nickname)

        log(UPDATE_TYPE.gcsu_geocachers, 'OK')
        return 'List of geocachers has updated'
