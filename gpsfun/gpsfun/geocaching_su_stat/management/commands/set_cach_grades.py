#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
     set_cache_grades.py

DESCRIPTION
     Set grade for all caches
"""

import requests
from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.geocaching_su_stat.sql import RAWSQL
from gpsfun.main.db_utils import execute_query


class Command(BaseCommand):
    help = 'Set grades for all caches'

    def handle(self, *args, **options):
        execute_query(RAWSQL['set_caches_grades'])

        log(UPDATE_TYPE.set_caches_locations, 'OK')

        return 'Grades of caches has updated'
