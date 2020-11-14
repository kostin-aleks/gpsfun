#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import connection
import unittest
import djyptestutils as yplib
from time import time
from datetime import datetime
import re
from gpsfun.DjHDGutils.misc import atoi
from bs4 import BeautifulSoup
from gpsfun.main.GeoCachSU.models import Geocacher, Cach
from gpsfun.main.models import switch_off_status_updated, switch_on_status_updated, log
#from _mechanize_dist import BrowserStateError
import django
django.setup()


class Cacher:
    pid = None
    uid = None
    nickname = None
    name = None
    birstday = None
    sex = None
    email = None
    country = None
    town = None
    oblast = None
    phone = None
    icq = None
    web = None
    gps = None
    created_caches = None
    found_caches = None
    photo_albums = None
    register_date = None
    last_login = None
    forum_posts = None

    def __eq__(self, other) :
        r = self.__dict__ == other.__dict__
        if not r:
            print(self.__dict__)
            print(other.__dict__)
        return r

def equal(f, s):
    return f.pid == s.pid and\
        f.nickname == s.nickname and\
        f.name == s.name and\
        f.birstday == s.birstday and\
        f.sex == s.sex and\
        f.country == s.country and\
        f.town == s.town and\
        f.oblast == s.oblast and\
        f.phone == s.phone and\
        f.icq == s.icq and\
        f.web == s.web and\
        f.gps == s.gps and\
        f.created_caches == s.created_caches and\
        f.found_caches == s.found_caches and\
        f.photo_albums == s.photo_albums and\
        f.register_date == s.register_date and\
        f.last_login == s.last_login and\
        f.forum_posts == s.forum_posts


def check_id_list(user_list):
    sql = """
    INSERT INTO geocacher
    (pid, uid, nickname, name, birstday, sex,
    country, oblast, town, phone,
    created_caches, found_caches,
    photo_albums, register_date, last_login, forum_posts
    )
    VALUES

    """
    values = []
    for user in user_list:
        sql_values = geocacher_format_insert_string(user.get('id'))
        #geocacher, ok = Geocacher.objects.get_or_create(pid=user['id'])
        #check_user_profile(geocacher)
        #print sql_values
        if sql_values and len(sql_values) > 2:
            values.append(sql_values)
    if len(values):
        sql += ',\n'.join(values)
        #print
        #print sql
        #print

        cursor = connection.cursor()
        cursor.execute(sql)

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

def text_field(cell):
    cell = text_or_none(cell)
    if cell:
        cell = re.escape(cell)
        return "'{}'".format(cell.encode('utf-8'))
    else:
        return 'NULL'

def date_field(cell):
    if type(cell) in (type(u''), type('')):
        cell = strdate_or_none(cell)
        if cell:
            return "'{}-{}-{}'".format(cell.year, cell.month, cell.day)
    return 'NULL'

def int_field(cell):
    cell = atoi(cell)
    if cell:
        return str(cell)
    else:
        return 'NULL'

def sex_field(cell):
    cell = sex_or_none(cell)
    if cell:
        return "'{}'".format(cell)
    else:
        return 'NULL'

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
        parts = cell.split('.')
        if len(parts) > 2:
            year = parts[2]
            if year:
                try:
                    r = datetime(int(year), int(parts[1]), int(parts[0]))
                except ValueError:
                    r = None
        else:
            parts = cell.split()
            if len(parts) == 3:
                year = year_from_text(parts[2])
                if year:
                    try:
                        r = datetime(int(year), dmonths[parts[1]], int(parts[0]))
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
        if r == u'м':
            r = 'M'
        else:
            r = 'F'
    return r

def int_or_none(cell):
    r = None
    if nonempty_cell(cell):
        r = int(cell)
    return r

def get_uid(tbl):
    uid = None
    a_list = tbl.findAll('a')
    for a in a_list:
        href = a['href']
        if href.startswith('javascript:indstat('):
            p = re.compile('javascript:indstat\((\d+)\,\d+\)')
            dgs = p.findall(href)
            if len(dgs):
                uid = int(dgs[0])
                break
    return uid

def geocacher_format_insert_string(pid):
    # try open profile
    fields = str(pid)
    url = 'http://www.geocaching.su/profile.php?pid={}'.format(pid)
    loaded = False
    cnter = 0
    fh = open('cant_open_profile.txt', 'w')

    while not loaded and cnter < 100:
        try:
            yplib.get(url)
            loaded = True
        except BrowserStateError:
            cnter += 1

    if not loaded:
        print('cannot go to %s' % url)
        fh.write(url)
        return False

    fh.close()

    # processing profile
    soup=yplib.soup()
    tbl = soup.find('table', {'class':'pages'})
    rows = tbl.findAll('tr')
    all_cells = []
    theuser = {}
    for row in rows:
        cells = row.findAll('th')
        for cell in cells:
            all_cells.append(cell.text.encode('utf8'))
        title_cells = row.findAll('td')
        data_cells = row.findAll('th')
        if len(title_cells) == 1:
            title_cell = title_cells[0]
            title = title_cell.text
            data = ''
            if len(data_cells):
                data_cell = data_cells[-1]
                data = data_cell.text
            if title.startswith(u'Псевдоним:'):
                theuser['nickname'] = data
                continue
            if title.startswith(u'Страна:'):
                theuser['country'] = data
                continue
            if title.startswith(u'Область:'):
                theuser['oblast'] = data
                continue
            if title.startswith(u'Нас.пункт'):
                theuser['town'] = data
                continue
            if title.startswith(u'Создал тайников:'):
                theuser['created'] = data
                continue
            if title.startswith(u'Нашел тайников:'):
                theuser['found'] = data
                continue
            if title.startswith(u'Рекомендовал тайников:'):
                theuser['recommended'] = data
                continue
            if title.startswith(u'Фотоальбомы:'):
                theuser['photo_albums'] = data
                continue
            if title.startswith(u'Был на сайте'):
                theuser['last_visited'] = data
                continue
            if title.startswith(u'Дата регистрации:'):
                theuser['registered'] = data
                continue
            if title.startswith(u'Сообщений в форумах:'):
                theuser['forum_posts'] = data

    #print theuser

    uid = get_uid(tbl)
    fields += ',{}'.format(int_field(uid))  #uid
    # pid uid nickname name birstday sex country oblast town phone icq web created_caches found_caches photo_albums register_date last_login forum_posts
    fields += ',{}'.format(text_field(theuser.get('nickname') or ''))  #nickname
    fields += ',{}'.format(text_field(all_cells[2]))  #name
    fields += ',{}'.format(date_field(all_cells[3]))  #birstday
    fields += ',{}'.format(sex_field(all_cells[4]))   #sex
    fields += ',{}'.format(text_field(theuser.get('country') or ''))  #country
    fields += ',{}'.format(text_field(theuser.get('oblast') or ''))  #oblast

    fields += ',{}'.format(text_field(theuser.get('town') or ''))  #town
    fields += ',{}'.format(text_field(all_cells[9]))  #phone

    fields += ',{}'.format(int_field(theuser.get('created') or 0))  #created_caches
    fields += ',{}'.format(int_field(theuser.get('found') or 0))  #found_caches
    fields += ',{}'.format(int_field(theuser.get('photo_albums') or 0))  #photo_albums
    #register_date = None
    #last_login = None
    #forum_posts = None
    #if len(all_cells) > 23:
        #register_date = date_or_none(all_cells[-3])
        #if register_date is None:
            #register_date = date_or_none(all_cells[-2])
        #last_login = date_or_none(all_cells[-2])
        #forum_posts = int_or_none(all_cells[-1])
    #import pdb; pdb.set_trace()
    fields += ',{}'.format(date_field(theuser.get('registered') or ''))  #register_date
    fields += ',{}'.format(date_field(theuser.get('last_visited') or ''))     #last_login
    fields += ',{}'.format(int_field(theuser.get('forum_posts') or 0))     #forum_posts

    return "({})".format(fields).replace('%', '%%')

def check_user_profile(geocacher):
    url = 'http://www.geocaching.su/profile.php?pid=%s'%geocacher.pid
    loaded = False
    cnter = 0
    fh = open('cant_open_profile.txt', 'w')
    while not loaded and cnter < 100:
        try:
            yplib.get(url)
            loaded = True
        except BrowserStateError:
            cnter += 1

    fh.close()
    if not loaded:
        print('cannot go to %s' % url)
        fh.write(url)
        return False

    soup=yplib.soup()
    tbl = soup.find('table', {'class':'pages'})
    rows = tbl.findAll('tr')
    all_cells = []
    for row in rows:
        cells = row.findAll('th')
        for cell in cells:
            all_cells.append(cell.text.encode('utf8'))

    user = Cacher()
    user.pid = geocacher.pid
    user.uid = get_uid(tbl)
    user.nickname = text_or_none(all_cells[1])
    user.name = text_or_none(all_cells[2])
    user.birstday = strdate_or_none(all_cells[3])
    user.sex = sex_or_none(all_cells[4])
    user.country = text_or_none(all_cells[5])
    user.oblast = text_or_none(all_cells[6])
    user.town = text_or_none(all_cells[7])
    user.phone = text_or_none(all_cells[9])
    user.icq = text_or_none(all_cells[10])
    if user.icq and not user.icq.isdigit():
        user.icq = None
    user.web = text_or_none(all_cells[11])
    gps = text_or_none(all_cells[15])
    user.gps = None#gps[:255].encode if gps else None
    user.created_caches = int_or_none(all_cells[18])
    user.found_caches = int_or_none(all_cells[19])
    user.photo_albums = int_or_none(all_cells[21])
    if len(all_cells) > 23:
        user.register_date = date_or_none(all_cells[-3])
        if user.register_date is None:
            user.register_date = date_or_none(all_cells[-2])
        user.last_login = date_or_none(all_cells[-2])
        user.forum_posts = int_or_none(all_cells[-1])


    geocacher.__dict__.update(user.__dict__)
    print('save', geocacher.pid)
    geocacher.save()

    return True


def main():
    if not switch_off_status_updated():
        return False

    LOAD_GEOCACHERS = False
    LOAD_ABSENT_GEOCACHERS = False

    start = time()

    cursor = connection.cursor()

    cursor.execute('select * from geocacher')

    yplib.setUp()
    yplib.set_debugging(False)


    r = yplib.post2('http://www.geocaching.su/?pn=108',
            (('Log_In','Log_In'), ('email', 'galdor@ukr.net'), ('passwd','zaebalixakeryvas'), ('longterm', '1')))

    soup=yplib.soup()

    a = soup.find('a', attrs={'class':"profilelink"}, text='galdor')
    if not a:
        print('Authorization failed')
        return False

    if LOAD_GEOCACHERS:
        Geocacher.objects.all().delete()
        cntr_list = []
        all_id = []
        for p in range(2500):
            print('page', p + 1)
            #if p < 0:
                #continue

            user_list = []
            r = yplib.post2('http://www.geocaching.su/?pn=108',
                (('sort','1'), ('page', str(p)),
                 ('in_page','100'), ('updown', '1')))
            soup=yplib.soup()
            a_list = soup.findAll('a', {'class':"profilelink"})
            t = re.compile('\?pid=(\d+)')
            for a in a_list[:-1]:
                if a.get('onclick'):
                    #print p.findall(a['onclick']), a.text.encode('utf8')
                    user_id = t.findall(a['onclick'])[0]
                    login = a.text.encode('utf8')
                    if not (user_id in all_id):
                        user_list.append({'id': user_id, 'login': login})
                        all_id.append(user_id)
            #user_list = user_list[:-1]
            if user_list == cntr_list:
                break
            else:
                cntr_list = user_list
                #print len(user_list)
                #return
                check_id_list(user_list)
                #break
                #check_id_list([{'id': 15957, 'login': u'Кривич'}])
            #break

    if LOAD_ABSENT_GEOCACHERS:
        pid_list = (469, 406, 1224, 4400, 11910,  4456, 13439,  7707, 8887, 3156, 8094)
        user_list = [{'id': pid, 'login': u''} for pid in pid_list]

        check_id_list(user_list)

    elapsed = time() - start
    print("Elapsed time -->", elapsed)
    switch_on_status_updated()
    log('gcsu_geocachers', 'OK')

if __name__ == '__main__':
    main()
