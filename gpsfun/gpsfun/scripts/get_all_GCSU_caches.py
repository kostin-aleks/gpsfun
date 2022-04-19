#!/usr/bin/env python
"""
Get all GCSU caches
"""

from datetime import datetime, date, timedelta
from time import time
import sys
import codecs
import re

import djyptestutils as yplib
from gpsfun.main.GeoCachSU.models import GEOCACHING_SU_ONMAP_TYPES
from gpsfun.main.GeoMap.models import Geothing, Geosite, Location, Cach
from gpsfun.main.db_utils import execute_query


def check_cach_list(item_list):
    """ check caches list """
    for item in item_list:
        cach, created = Cach.objects.get_or_create(pid=item['id'], code=item['code'])
        check_cach(cach)


def nonempty_cell(cell):
    """ is cell not empty ? """
    result = True
    if not cell or cell=='&nbsp;':
        result = False
    return result

def text_or_none(cell):
    """ get text or None """
    result = None
    if nonempty_cell(cell):
        result = cell.strip()
    return result

def char_or_none(cell):
    """ get one char or None """
    result = None
    if nonempty_cell(cell):
        result = cell.strip()
        result = result[:1]
    return result

def strdate_or_none(cell):
    """ get date or None """
    def year_from_text(txt):
        """ get year from text """
        result = None
        item = re.compile('\d+')
        dgs = item.findall(txt)
        if dgs and len(dgs):
            result = int(dgs[0])
            if result < 1000:
                result = 1900
        return result

    dmonths = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12,
    }
    result = None
    if nonempty_cell(cell):
        parts = cell.split()
        print(cell, parts)
        if len(parts) > 2:
            year = year_from_text(parts[2])
            if year:
                try:
                    result = datetime(year, dmonths[parts[1]], int(parts[0]))
                except ValueError:
                    result = None
    return result

def date_or_none(cell):
    """ get date or None """
    result = None
    if nonempty_cell(cell):
        parts = cell.split('.')
        if len(parts) > 2:
            try:
                result = datetime(int(parts[2][:4]), int(parts[1]), int(parts[0]))
            except ValueError:
                result = None
    return result

def sex_or_none(cell):
    """ get sex or None """
    result = None
    if nonempty_cell(cell):
        result = unicode(cell, 'utf8')[0]
    return result

def int_or_none(cell):
    """ get int or None """
    result = None
    if nonempty_cell(cell):
        result = int(cell)
    return result

def float_or_none(cell):
    """ get float or None """
    result = None
    if nonempty_cell(cell):
        try:
            result = float(cell)
        except:
            result = None
    return result

def nottag(txt):
    """ does txt have any tag ? """
    if not txt:
        return True
    tags = re.compile('\<.+\>')
    items = tags.findall(txt)

    return len(items) == 0

def check_cach(cach):
    """ check cache """
    def get_coordinates(cell):
        """ get coordinates """
        coordinates = cell.text
        parts = tmpl2.findall(coordinates)[0]
        if len(parts) == 4:
            ns_degree, ns_minute, ew_degree, ew_minute = parts
        parts = tmpl3.findall(coordinates)
        n_s = parts[0]
        parts = tmpl4.findall(coordinates)
        e_w = parts[0]

        return ns_degree, ns_minute, ew_degree, ew_minute, n_s, e_w

    def get_type(cell):
        """ get type """
        return cell.text

    def get_class(cell):
        """ get class """
        class_ = None
        if cell:
            parts = cell.contents
            items = []
            for part in parts:
                txt = part.string
                if txt and nottag(txt):
                    items.append(txt)
            class_ = ';'.join(items)
        return class_

    def get_mestnost(cell):
        """ get mestnost """
        oblast = country = None
        parts = cell.contents
        if len(parts):
            country = parts[0]
        if len(parts) > 2:
            oblast = parts[2]
        return country, oblast

    def get_dostupnost(cell):
        """ get dostupnost """
        parts = cell.contents
        dostupnost = parts[0].split(':')[1].strip()
        mestnost = parts[2].split(':')[1].strip()
        return dostupnost, mestnost

    def get_town(cell):
        """ get town """
        return cell.text

    def get_grade(cell):
        """ get grade """
        grade = None
        if cell.img:
            grade = cell.img.get('title')
        return grade

    def get_attributes(element):
        """ get attributes """
        attr = None
        items = []
        imgs =  element.findAll('img')
        for img in imgs:
            if 'images/attrib/' in img.get('src'):
                items.append(img.get('title'))
            attr = ';'.join(items)
        return attr

    url = f'http://www.geocaching.su/?pn=101&cid={int(cach.pid)}'
    try:
        yplib.get(url)
    except:
        print('exception')
        return False
    soup=yplib.soup()

    header = soup.find('h1', {'class': 'hdr'})
    tmpl = re.compile('([^\[]+)\[.+\]')
    tmpl1 = re.compile('[^\[]+\[([^\[\]]+\/[^\[\]]+)\]')
    tmpl2 = re.compile('[N,S]\s(\d+)\&\#176\;\s([\d\.]+).+[E,W]\s(\d+)\&\#176\;\s([\d\.]+)')
    tmpl3 = re.compile('([N,S]\s\d+\&\#176\;\s[\d\.]+.)')
    tmpl4 = re.compile('([E,W]\s\d+\&\#176\;\s[\d\.]+.)')
    tmpl5 = re.compile('WinPopup\(\'profile\.php\?pid\=(\d+)')

    name = None
    items = tmpl.findall(header.text)
    if items:
        name = items[0]
    full_code = None
    items = tmpl1.findall(header.text)
    if items:
        full_code = items[0]
        type_code, pid = full_code.split('/')

    tbl = soup.find('table', attrs={'cellpadding':3, 'width':160})
    rows = tbl.findAll('tr')

    ns_degree = ns_minute = ew_degree = ew_minute = n_s = e_w = None
    country = oblast = town = None
    dostupnost = mestnost = None
    cach_type = cach_class = None
    grade = attr = None

    act = None
    for row in rows:
        tds = row.findAll('td')
        ths = row.findAll('th')
        tcell = None
        if tds:
            tcell = tds[0]

        cell = None
        if act:
            if ths:
                cell = ths[0]
            elif tds:
                cell = tds[1]
            if act == 'coord':
                ns_degree, ns_minute, ew_degree, ew_minute, n_s, e_w = get_coordinates(cell)
            if act == 'mestnost':
                country, oblast = get_mestnost(cell)
            if act == 'dostupnost':
                dostupnost, mestnost = get_dostupnost(cell)
            if act == 'town':
                town = get_town(cell)
            if act == 'grade':
                grade = get_grade(cell)
            act = None

        if tcell and tcell.text.startswith('Тип:'):
            cach_type = get_type(tds[1])
            act = None
        if tcell and tcell.text.startswith('Класс:'):
            cach_class = get_class(tds[1])
            act = None
        if tcell and tcell.text.startswith('КООРДИНАТЫ'):
            act = 'coord'
        if tcell and tcell.text.startswith('МЕСТНОСТЬ'):
            act = 'mestnost'
        if tcell and tcell.text.startswith('БЛИЖАЙШИЙ'):
            act = 'town'
        if tcell and tcell.text.startswith('ОЦЕНКИ'):
            act = 'dostupnost'
        if tcell and tcell.text.startswith('РЕЙТИНГ'):
            act = 'grade'
        if tcell and tcell.text.startswith('АТРИБУТЫ'):
            attr = get_attributes(tbl)
            act = None

    created_by = created_date = changed_date = coauthors = None
    div = soup.findAll('div', attrs={'style':'padding: 5px; font-family: Verdana; font-weight: bold;'})[0]
    anchor = div.a
    if anchor:
        onclick = anchor.get('onclick')
        if onclick:
            pid = tmpl5.findall(onclick)
            if pid:
                created_by = int(pid[0])

    parts = div.contents
    for part in parts:
        txt = part.string

        if txt and nottag(txt):
            txt = txt.string.strip()
            if txt.startswith('Создан:'):
                items = txt.split()
                if len(items) == 2:
                    created_date = items[1]
                    if created_date:
                        day, month, year = [int(s) for s in created_date.split('.')]
                    created_date = date(year, month, day)

            if txt.startswith('(отредактирован'):
                txt = txt[1:-1]
                items = txt.split()
                if len(items) == 2:
                    changed_date = items[1]
                    if changed_date:
                        day, month, year = [int(s) for s in changed_date.split('.')]
                    changed_date = date(year, month, day)

            if txt.startswith('Компаньоны:'):
                coauthors = 'yes'

    the_cach = TheCach()
    the_cach.pid = cach.pid
    the_cach.code = f'{type_code}{the_cach.pid}'
    the_cach.type_code = type_code

    the_cach.name = text_or_none(name)
    the_cach.cach_type = text_or_none(cach_type)
    the_cach.cach_class = text_or_none(cach_class)
    the_cach.loc_NS = char_or_none(n_s)
    the_cach.loc_EW = char_or_none(e_w)
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
    cach.__dict__.update(the_cach.__dict__)
    print('save', cach.pid)
    cach.save()

    return True

def dephi_date_to_python_date(item):
    """ convert delphi date into python date """
    days = int(item)
    hours = int(round((item - days) * 24))
    date_ = datetime(1899, 12, 30) + timedelta(days=int(item), hours=hours)
    return date_

def main():
    """ main procedure """
    start = time()

    sql = """
    DELETE location
    FROM location
    LEFT JOIN geothing ON geothing.location_id=location.id
    LEFT JOIN geosite ON geothing.geosite_id = geosite.id
    WHERE geosite.code = 'GC_SU'
    """
    execute_query(sql)

    sql = """
    DELETE geothing
    FROM geothing
    LEFT JOIN geosite ON geothing.geosite_id = geosite.id
    WHERE geosite.code = 'GC_SU'
    """
    execute_query(sql)

    file = '/tmp/geocaching_su.wpt'

    # sanity checking, only work on wpt files
    if file.endswith('.wpt') == 0:
        sys.exit(-1)

    print("Reading file: " + file)

    fhandler = codecs.open(file, 'r', "cp1251")
    wpt = fhandler.readlines()
    fhandler.close()

    wpt_code = 1
    wpt_lat = 2
    wpt_lon = 3
    wpt_title = 10
    wpt_date = 4

    geosite = Geosite.objects.get(code='GC_SU')
    print(geosite)
    print(len(wpt), 'points')
    for point in wpt:
        print
        print(point)
        fields = point.split(',')
        if fields[0].isdigit():
            geothing = Geothing(geosite=geosite)
            print(geothing.geosite.url)
            for field in fields:
                print(field)
            location = Location()
            lat_degree = float(fields[wpt_lat])
            location.NS_degree = int(lat_degree)
            location.NS_minute = (abs(lat_degree) - abs(location.NS_degree)) * 60
            lon_degree = float(fields[wpt_lon])
            location.EW_degree = int(lon_degree)
            location.EW_minute = (abs(lon_degree) - abs(location.EW_degree)) * 60
            location.save()
            geothing.location = location
            item = re.compile('(\D+)(\d+)')
            dgs = item.findall(fields[wpt_code])
            if dgs:
                code_data = dgs[0]
                geothing.code = fields[wpt_code]
                geothing.pid = int(code_data[1])
                geothing.type_code = code_data[0]

            item = re.compile(u'(.+)от(.+)')
            dgs = item.findall(fields[wpt_title])
            if dgs:
                title = dgs[0]
                geothing.name = title[0]
                geothing.author = title[1]

            date = float(fields[wpt_date])
            print(dephi_date_to_python_date(date))
            geothing.created_date = dephi_date_to_python_date(date)
            if geothing.type_code in GEOCACHING_SU_ONMAP_TYPES:
                geothing.save()

    elapsed = time() - start
    print("Elapsed time -->", elapsed)
    return

if __name__ == '__main__':
    main()
