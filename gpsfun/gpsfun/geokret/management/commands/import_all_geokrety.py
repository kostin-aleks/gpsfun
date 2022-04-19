#!/usr/bin/env python
"""
NAME
     import_all_geokrety.py

DESCRIPTION
     Imports all geokrety
"""

import urllib.request
import bz2
from bs4 import BeautifulSoup
import requests

from django.core.management.base import BaseCommand

from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.main.GeoKrety.models import GeoKret, Location


class Command(BaseCommand):
    """ command """
    help = 'Imports all geokrety'

    def handle(self, *args, **options):
        url = 'https://cdn.geokrety.org/rzeczy/xml/export2-full.xml.bz2'
        filename = '/tmp/export2-full.xml.bz2'
        urllib.request.urlretrieve(url, filename)

        zipfile = bz2.BZ2File(filename)
        data = zipfile.read()
        newfilepath = filename[:-4]
        with open(newfilepath, 'wb') as newfile:
            newfile.write(data)
            newfile.close()

        with open(newfilepath, 'r') as newfile:
            xml = newfile.read()
            newfile.close()

        soup = BeautifulSoup(xml, 'lxml')

        all_krety = soup.find_all('geokret')

        for kret in all_krety:

            gkid = int(kret.get('id') or 0)
            if not gkid:
                continue

            name = kret.get('name')
            distance = int(kret.get('dist') or 0)
            latitude = float(kret.get('lat') or 0)
            longitude = float(kret.get('lon') or 0)
            waypoint = kret.get('waypoint')
            state = int(kret.get('state')) if kret.get('state') else None
            kret_type = kret.get('type') if kret.get('type') else None

            geokret, created = GeoKret.objects.get_or_create(gkid=gkid)
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
                geokret.state = state
                geokret.type_code = kret_type

                geokret.save()


        for kret in GeoKret.objects.filter(name__isnull=True):
            with requests.Session() as session:
                result = session.get(
                    'https://geokrety.org/konkret.php',
                    params={'id': kret.gkid}
                )

                soup = BeautifulSoup(result.text, 'lxml')
                for cell in soup.find_all('td', attrs={'class': 'heading1'}):
                    if cell.text and cell.text.strip().startswith('GeoKret'):
                        strong = cell.find('strong')
                        if strong:
                            kret.name = strong.text
                            kret.save()
                            print(kret.name)

        log(UPDATE_TYPE.geokrety_imported, 'OK')

        return 'Geokrety are imported'
