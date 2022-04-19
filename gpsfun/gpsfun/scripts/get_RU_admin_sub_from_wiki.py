#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import connection
import unittest
import djyptestutils as yplib
from time import time
from datetime import datetime, date
import re
from BeautifulSoup import BeautifulSoup
from geocaching_su_crawler.Geoname.models import GeoRUSSubject


def check_cach(cach):
    def get_coordinates(cell):
        coordinates = cell.text
        parts = t2.findall(coordinates)[0]
        if len(parts) == 4:
            ns_degree, ns_minute, ew_degree, ew_minute = parts
        parts = t3.findall(coordinates)
        NS = parts[0]
        parts = t4.findall(coordinates)
        EW = parts[0]

        return ns_degree, ns_minute, ew_degree, ew_minute, NS, EW

    def get_type(cell):
        return cell.text

    def get_class(cell):
        class_ = None
        if cell:
            parts = cell.contents
            items = []
            for p in parts:
                txt = p.string
                if txt and nottag(txt):
                    items.append(txt)
            class_ = ';'.join(items)
        return class_

    def get_mestnost(cell):
        oblast = country = None
        parts = cell.contents
        if len(parts):
            country = parts[0]
        if len(parts) > 2:
            oblast = parts[2]
        return country, oblast

    def get_dostupnost(cell):
        parts = cell.contents
        dostupnost = parts[0].split(':')[1].strip()
        mestnost = parts[2].split(':')[1].strip()
        return dostupnost, mestnost

    def get_town(cell):
        return cell.text

    def get_grade(cell):
        grade = None
        if cell.img:
            grade = cell.img.get('title')
        return grade

    def get_attributes(element):
        attr = None
        items = []
        imgs =  element.findAll('img')
        for img in imgs:
            if 'images/attrib/' in img.get('src'):
                items.append(img.get('title'))
            attr = ';'.join(items)
        return attr

    url = 'http://www.geocaching.su/?pn=101&cid=%d'%int(cach.pid)
    try:
        yplib.get(url)
    except:
        print('exception')
        return False
    soup=yplib.soup()
    h = soup.find('h1', {'class':'hdr'})
    t = re.compile('([^\[]+)\[.+\]')
    t1 = re.compile('[^\[]+\[([^\[\]]+\/[^\[\]]+)\]')
    t2 = re.compile('[N,S]\s(\d+)\&\#176\;\s([\d\.]+).+[E,W]\s(\d+)\&\#176\;\s([\d\.]+)')
    t3 = re.compile('([N,S]\s\d+\&\#176\;\s[\d\.]+.)')
    t4 = re.compile('([E,W]\s\d+\&\#176\;\s[\d\.]+.)')
    t5 = re.compile('WinPopup\(\'profile\.php\?pid\=(\d+)')

    name = None
    items = t.findall(h.text)
    if items:
        name = items[0]
    full_code = None
    items = t1.findall(h.text)
    if items:
        full_code = items[0]
        type_code, pid = full_code.split('/')

    tbl = soup.find('table', attrs={'cellpadding':3, 'width':160})
    rows = tbl.findAll('tr')

    ns_degree = ns_minute = ew_degree = ew_minute = NS = EW = None
    country = oblast = town = None
    dostupnost = mestnost = None
    cach_type = cach_class = None
    grade = attr = None

    act = None
    for row in rows:
        tds = row.findAll('td')
        ths = row.findAll('th')
        td = None
        if tds:
            td = tds[0]

        cell = None
        if act:
            if ths:
                cell = ths[0]
            elif tds:
                cell = tds[1]
            if act == 'coord':
                ns_degree, ns_minute, ew_degree, ew_minute, NS, EW = get_coordinates(cell)
            if act == 'mestnost':
                country, oblast = get_mestnost(cell)
            if act == 'dostupnost':
                dostupnost, mestnost = get_dostupnost(cell)
            if act == 'town':
                town = get_town(cell)
            if act == 'grade':
                grade = get_grade(cell)
            act = None

        if td and td.text.startswith(u'Тип:'):
            cach_type = get_type(tds[1])
            act = None
        if td and td.text.startswith(u'Класс:'):
            cach_class = get_class(tds[1])
            act = None
        if td and td.text.startswith(u'КООРДИНАТЫ'):
            act = 'coord'
        if td and td.text.startswith(u'МЕСТНОСТЬ'):
            act = 'mestnost'
        if td and td.text.startswith(u'БЛИЖАЙШИЙ'):
            act = 'town'
        if td and td.text.startswith(u'ОЦЕНКИ'):
            act = 'dostupnost'
        if td and td.text.startswith(u'РЕЙТИНГ'):
            act = 'grade'
        if td and td.text.startswith(u'АТРИБУТЫ'):
            attr = get_attributes(tbl)
            act = None

    created_by = created_date = changed_date = coauthors = None
    div = soup.findAll('div', attrs={'style':'padding: 5px; font-family: Verdana; font-weight: bold;'})[0]
    a = div.a
    if a:
        onclick = a.get('onclick')
        if onclick:
            pid = t5.findall(onclick)
            if pid:
                created_by = int(pid[0])

    parts = div.contents
    for p in parts:
        txt = p.string

        if txt and nottag(txt):
            txt = txt.string.strip()
            if txt.startswith(u'Создан:'):
                items = txt.split()
                if len(items) == 2:
                    created_date = items[1]
                    if created_date:
                        day, month, year = [int(s) for s in created_date.split('.')]
                    created_date = date(year, month, day)

            if txt.startswith(u'(отредактирован'):
                txt = txt[1:-1]
                items = txt.split()
                if len(items) == 2:
                    changed_date = items[1]
                    if changed_date:
                        day, month, year = [int(s) for s in changed_date.split('.')]
                    changed_date = date(year, month, day)

            if txt.startswith(u'Компаньоны:'):
                coauthors = 'yes'

    the_cach = TheCach()
    the_cach.pid = cach.pid
    the_cach.code = '%s%s' % (type_code, the_cach.pid)

    the_cach.name = text_or_none(name)
    the_cach.cach_type = text_or_none(cach_type)
    the_cach.cach_class = text_or_none(cach_class)
    the_cach.loc_NS = char_or_none(NS)
    the_cach.loc_EW = char_or_none(EW)
    the_cach.loc_NS_degree = int_or_none(ns_degree)
    the_cach.loc_EW_degree = int_or_none(ew_degree)
    the_cach.loc_NS_minute = float_or_none(ns_minute)
    the_cach.loc_EW_minute = float_or_none(ew_minute)
    the_cach.country = text_or_none(country)
    the_cach.oblast = text_or_none(oblast)
    the_cach.town = text_or_none(town)
    the_cach.dostupnost = int_or_none(dostupnost)
    the_cach.mestnost = int_or_none(mestnost)
    the_cach.grade = float_or_none(grade)
    the_cach.cach_attr = text_or_none(attr)
    the_cach.created_by = created_by
    the_cach.created_date = created_date
    the_cach.changed_date = changed_date
    the_cach.coauthors = coauthors

    print(the_cach.name.encode('utf8'))
    if True:
        cach.__dict__.update(the_cach.__dict__)
        print('save', cach.pid)
        cach.save()

    return True

def main():
    LOAD_ = True

    start = time()

    yplib.set_up()
    yplib.set_debugging(False)


    if LOAD_:
        GeoRUSSubject.objects.all().delete()
        yplib.get('http://ru.wikipedia.org/wiki/%D0%9A%D0%BE%D0%B4%D1%8B_%D1%81%D1%83%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B9%D1%81%D0%BA%D0%BE%D0%B9_%D0%A4%D0%B5%D0%B4%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D0%B8')
        soup=yplib.soup()
        tbl = soup.find('table', {'class': "sortable standard"})
        rows = tbl.findAll('tr')
        for row in rows:
            cells = row.findAll('td')
            print(cells)
            if cells:
                subject = GeoRUSSubject(country_iso='RU', geoname_id=0)
                cell = cells[0]
                a = cell.find('a')
                if a:
                    subject.name = a.text
                    subject.ascii_name = cells[1].text
                    subject.code = cells[2].text
                    subject.gai_code = cells[3].text
                    subject.iso_3166_2_code = cells[4].text

                    subject.save()

    elapsed = time() - start
    print("Elapsed time -->", elapsed)

if __name__ == '__main__':
    main()
