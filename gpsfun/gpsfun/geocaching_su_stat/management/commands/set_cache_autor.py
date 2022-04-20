#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
     set_cache_author.py

DESCRIPTION
     Set author for caches with unknown author
"""

import requests
from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.main.GeoCachSU.models import Cach, Geocacher
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_author)


class Command(BaseCommand):
    """ Command """
    help = 'Set cache author'

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
                for cache in Cach.objects.filter(author__isnull=True):
                    response = session.get(
                        'http://www.geocaching.su/',
                        params={'pn': 101, 'cid': cache.pid}
                    )
                    author_uid = get_author(response.text)
                    if author_uid:
                        author = Geocacher.objects.filter(
                            uid=int(author_uid)).first()
                        if author:
                            cache.author = author
                            cache.save()
                            print('saved', cache.pid, author_uid)
                        else:
                            print('not found author', author_uid)


        log(UPDATE_TYPE.set_caches_authors, 'OK')

        return 'Authors of caches have updated'
