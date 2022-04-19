#!/usr/bin/env python
"""
NAME
     map_update_all_geosites.py

DESCRIPTION
     Runs all commands to update map items
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    """ command """
    help = 'Runs all commands to update map items'

    def handle(self, *args, **options):
        call_command('map_update_opencaching')
        call_command('map_update_shukach_caches')
        call_command('map_update_su_caches')
