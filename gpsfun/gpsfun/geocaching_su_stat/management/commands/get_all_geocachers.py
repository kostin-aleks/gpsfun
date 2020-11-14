#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    help = 'Loads list of all geocachers'

    def handle(self, *args, **options):
        with requests.Session() as session:
            post = session.post(
                'https://geocaching.su',
                data=LOGIN_DATA,
            )

            r = session.get('https://geocaching.su')
            if not logged(r.text):
                print('Authorization failed')
            else:
                for uid in range(200000):
                    r = session.get(
                        'http://www.geocaching.su/profile.php?uid=%d' % uid)
                    geocacher = get_user_profile(uid, r.text)
                    if geocacher:
                        print(uid, geocacher.id, geocacher.nickname)

        log(UPDATE_TYPE.gcsu_geocachers, 'OK')
        return 'List of geocachers has updated'
