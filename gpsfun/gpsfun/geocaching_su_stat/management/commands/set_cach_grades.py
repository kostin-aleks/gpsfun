#!/usr/bin/env python
"""
NAME
     set_cache_grades.py

DESCRIPTION
     Set grade for all caches
"""

from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UpdateType
from gpsfun.geocaching_su_stat.sql import RAWSQL
from gpsfun.main.db_utils import execute_query


class Command(BaseCommand):
    """ Command """
    help = 'Set grades for all caches'

    def handle(self, *args, **options):
        execute_query(RAWSQL['set_caches_grades'])

        log(UpdateType.set_caches_locations, 'OK')

        return 'Grades of caches has updated'
