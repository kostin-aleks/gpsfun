#!/usr/bin/env python
"""
NAME
     update_geokrety.py

DESCRIPTION
     Updates geokrets
"""

from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UpdateType
from gpsfun.main.GeoKrety.models import GeoKret, Location


class Command(BaseCommand):
    """ command """
    help = 'Updates geokrets'

    def handle(self, *args, **options):
        """ handler """
        sincedate = datetime.now() - timedelta(days=7)
        sincedatestr = sincedate.strftime('%Y%m%d%H%M%S')
        with requests.Session() as session:
            result = session.get(
                'http://geokrety.org/export_oc.php',
                params={'modifiedsince': sincedatestr}
            )

            soup = BeautifulSoup(result.text, 'lxml')
            all_krety = soup.find_all('geokret')

            for kret in all_krety:
                gkid = int(kret.get('id') or 0)
                if not gkid:
                    continue

                name = kret.find('name').text
                distance = kret.distancetravelled.text
                position = kret.position
                latitude = float(position.get('latitude') or 0)
                longitude = float(position.get('longitude') or 0)
                waypoints = kret.waypoints
                wpoint = waypoints.find_all('waypoint')
                waypoint = wpoint[0].text if wpoint else None
                state = kret.state.text

                geokret = GeoKret.objects.get_or_create(gkid=gkid)[0]
                if geokret:
                    if name:
                        geokret.name = name
                    geokret.distance = distance
                    if geokret.location is None:
                        geokret.location = Location.objects.create(
                            NS_degree=latitude,
                            EW_degree=longitude)
                    else:
                        geokret.location.NS_degree = latitude
                        geokret.location.EW_degree = longitude
                        geokret.location.save()

                    geokret.waypoint = waypoint
                    geokret.state = int(state or 0)

                    geokret.save()

        log(UpdateType.geokrety_updated, 'OK')

        return 'Geokrety are updated'
