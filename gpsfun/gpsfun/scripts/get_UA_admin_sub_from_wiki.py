#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import connection
import unittest
import djyptestutils as yplib
from time import time
from datetime import datetime, date
import re
from BeautifulSoup import BeautifulSoup
from geocaching_su_crawler.Geoname.models import GeoUKRSubject


def main():
    LOAD_ = True

    start = time()

    yplib.set_up()
    yplib.set_debugging(False)


    if LOAD_:
        GeoUKRSubject.objects.all().delete()
        yplib.get('http://en.wikipedia.org/wiki/ISO_3166-2:UA')
        soup=yplib.soup()
        tbl = soup.find('table', {'class': "wikitable sortable"})
        rows = tbl.findAll('tr')
        for row in rows:
            cells = row.findAll('td')
            if cells:
                subject = GeoUKRSubject(country_iso='UA', geoname_id=0)
                cell = cells[1]
                a = cell.find('a')
                if a:
                    subject.ascii_name = a.text
                    subject.name = ''
                    fullcode = cells[0].text.split('-')
                    subject.code = fullcode[1]

                    subject.save()

    elapsed = time() - start
    print("Elapsed time -->", elapsed)

if __name__ == '__main__':
    main()
