#!/usr/bin/env python
"""
NAME
     get_new_caches.py

DESCRIPTION
     Calculates statistics
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    """ Command """
    help = 'Calculates statistics'

    def handle(self, *args, **options):
        """ handle """
        call_command('calculate_cache_statistics')
        call_command('calculate_search_statistics')
        call_command('calculate_geocacher_statistics')

        return 'Statistics is calculated'
