#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import connection
import unittest
import djyptestutils as yplib
from time import time
from datetime import datetime, date
import re
from BeautifulSoup import BeautifulSoup
from gpsfun.main.GeoCachSU.models import Geocacher, Cach
from gpsfun.main.models import switch_off_status_updated, switch_on_status_updated, log

class TheCach:
    pid = None
    code = None
    name = None
    created_date = None
    changed_date = None
    created_by = None
    country = None
    town = None
    oblast = None
    coauthors = None
    cach_type = None
    cach_class = None
    cach_attr = None
    loc_NS = None
    loc_EW = None
    loc_NS_degree = None
    loc_EW_degree = None
    loc_NS_minute = None
    loc_EW_minute = None
    dostupnost = None
    mestnost = None
    grade = None

def check_cach_list(item_list):
    for item in item_list:
        cach, ok = Cach.objects.get_or_create(pid=item['id'], code=item['code'])
        check_cach(cach)
        

def nonempty_cell(cell):
    r = True
    if not cell or cell=='&nbsp;':
        r = False
    return r
    
def text_or_none(cell):
    r = None
    if nonempty_cell(cell):
        r = cell.strip()
        if type(r) != type(u' '):
            r = unicode(r, 'utf8')
    return r

def char_or_none(cell):
    r = None
    if nonempty_cell(cell):
        r = cell.strip()
        if type(r) != type(u' '):
            r = unicode(r, 'utf8')
        r = r[:1]
    return r

def strdate_or_none(cell):
    def year_from_text(s):
        r = None
        p = re.compile('\d+')
        dgs = p.findall(s)
        if dgs and len(dgs):
            r = int(dgs[0])
            if r < 1000:
                r = 1900
        return r
    
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
    r = None
    if nonempty_cell(cell):
        parts = cell.split()
        print cell, parts
        if len(parts) > 2:
            year = year_from_text(parts[2])
            if year:
                try:
                    r = datetime(year, dmonths[parts[1]], int(parts[0]))
                except ValueError:
                    r = None
    return r

def date_or_none(cell):
    r = None
    if nonempty_cell(cell):
        parts = cell.split('.')
        if len(parts) > 2:
            try:
                r = datetime(int(parts[2][:4]), int(parts[1]), int(parts[0]))
            except ValueError:
                r = None
    return r

def sex_or_none(cell):
    r = None
    if nonempty_cell(cell):
        r = unicode(cell, 'utf8')[0]
    return r

def int_or_none(cell):
    r = None
    if nonempty_cell(cell):
        r = int(cell)
    return r

def float_or_none(cell):
    r = None
    if nonempty_cell(cell):
        try:
            r = float(cell)
        except:
            r = None
    return r

def nottag(txt):
    if not txt:
        return True
    t = re.compile('\<.+\>')
    items = t.findall(txt)

    return len(items) == 0

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
        print 'exception'
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
        #if txt:
            #print txt.encode('utf8'), type(txt)
            
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
    the_cach.type_code = type_code
    #print    
    #print cach.pid
    #print '|%s|'%the_cach.code.encode('utf8')
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
    
    print the_cach.name.encode('utf8')
    if True:
        cach.__dict__.update(the_cach.__dict__)
        print 'save', cach.pid
        cach.save()
    
    return True

def main():
    #if not switch_off_status_updated():
        #return False
    
    LOAD_CACHES = True
    LOAD_GEO_LOCATION = False
    
    start = time() 
    
    yplib.setUp()
    yplib.set_debugging(False)
    
    
    r = yplib.post2('http://www.geocaching.su/?pn=108',
            (('Log_In','Log_In'), ('email', 'galdor@ukr.net'), ('passwd','zaebalixakeryvas'), ('longterm', '1')))
    
    soup=yplib.soup()

    a = soup.find('a', attrs={'class':"profilelink"}, text='galdor')
    if not a:
        print 'Authorization failed'
        return False
    print 'OK'
    
    

    if LOAD_CACHES:
        
        r = yplib.get('http://www.geocaching.su/site/popup/selex.php')
        soup=yplib.soup()
        #print soup
        #html = yplib.show()
        
        
        chbox_list = soup.findAll('input', type='checkbox')
        regions = []
        #print chbox_list
        print
        for chbox in chbox_list:
            #print chbox.get('value')
            v = chbox.get('value')
            if v and chbox.get('name','') == 'point[]':
                regions.append(v)
        print
        print regions
        data = [('translit','0'), ('fmt','wpt'), ('code_to_name','1'), ('finded','2'),]
        for r in regions:
            data.append(('point[]',r))
        print
        print data
        print
        r = yplib.post2('http://www.geocaching.su/site/popup/export.php',  data)
        soup=yplib.soup()
        txt = soup.text
        print txt
        return

        Cach.objects.all().delete()
        cntr_list = []
        t = re.compile('\<td\>(\w\w\d+)\<\/td\>')
        for p in range(100):
            item_list = []
            r = yplib.post2('http://www.geocaching.su/?pn=101',
                (('sort','1'), ('page', str(p)), ('in_page','100'), ('finded','1'), ('y','0'), ('x','0'), ('updown', '1')))
            html = yplib.show()
            code_list = t.findall(html)
            for code in code_list:
                pid = code[2:]
                item_list.append({'id': pid, 'code': code})
            

            if item_list == cntr_list:
                break
            else:
                cntr_list = item_list
                check_cach_list(item_list)
                #check_cach_list([{'id': 2746, 'code': 'EX2746'}])
            #break
    if LOAD_GEO_LOCATION:
        #.filter(pid=5408)
        for cach in Cach.objects.all():
            lat = cach.latitude_degree
            lng = cach.longitude_degree
            
            if lat is not None and lng is not None:
                url = 'http://ws.geonames.org/countrySubdivision?lat=%s&lng=%s&lang=ru' % (lat, lng)
                print
                print cach.pid, url
                yplib.get(url)
                try:
                    soup=yplib.soup()
                except:
                    url = 'http://ws.geonames.org/countrySubdivision?lat=%s&lng=%s&lang=en' % (lat, lng)
                    yplib.get(url)
                    soup=yplib.soup()
                item = soup.find('countrycode')
                if item:
                    cach.country_code = item.text.encode('utf8')
                
                if soup.admincode1:
                    cach.admin_code = soup.admincode1.text
                item = soup.find('code', {'type':'FIPS10-4'})
                if item:
                    cach.code_fips10_4 = item.text
                item = soup.find('code', {'type':'ISO3166-2'})
                if item:
                    cach.code_iso3166_2 = item.text
                item = soup.find('countryname')
                if item:
                    cach.country_name = item.text.encode('cp1251')
                if soup.adminname1:
                    cach.oblast_name = soup.adminname1.text.encode('cp1251')
                print cach.pid, cach.country_name, cach.oblast_name          
                #print soup
                #print
                #print cach.pid
                cach.save()
            else:
                print cach.pid, lat, lng, cach.loc_NS, cach.loc_NS_degree, cach.loc_NS_minute, cach.loc_EW, cach.loc_EW_degree, cach.loc_EW_minute
            
            switch_on_status_updated()
            log('gcsu_caches', 'OK')
            
    elapsed = time() - start
    print "Elapsed time -->", elapsed

if __name__ == '__main__':
    main()
