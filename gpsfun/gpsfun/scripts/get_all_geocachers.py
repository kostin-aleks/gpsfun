#!/usr/bin/env python
"""
Get all geocashers from site geocashing.su
"""

from time import time
from datetime import datetime
import re

import django
from django.db import connection

import djyptestutils as yplib
from gpsfun.DjHDGutils.misc import atoi
from gpsfun.main.GeoCachSU.models import Geocacher, Cach
from gpsfun.main.models import switch_off_status_updated, switch_on_status_updated, log

django.setup()


class Cacher:
    """ Geocasher data and methods """
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
        result = self.__dict__ == other.__dict__
        if not result:
            print(self.__dict__)
            print(other.__dict__)
        return result

def equal(first, second):
    """ are equal two geocachers ? """
    return first.pid == second.pid and\
        first.nickname == second.nickname and\
        first.name == second.name and\
        first.birstday == second.birstday and\
        first.sex == second.sex and\
        first.country == second.country and\
        first.town == second.town and\
        first.oblast == second.oblast and\
        first.phone == second.phone and\
        first.icq == second.icq and\
        first.web == second.web and\
        first.gps == second.gps and\
        first.created_caches == second.created_caches and\
        first.found_caches == second.found_caches and\
        first.photo_albums == second.photo_albums and\
        first.register_date == second.register_date and\
        first.last_login == second.last_login and\
        first.forum_posts == second.forum_posts


def check_id_list(user_list):
    """ check list of id """
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
        if sql_values and len(sql_values) > 2:
            values.append(sql_values)
    if values:
        sql += ',\n'.join(values)

        cursor = connection.cursor()
        cursor.execute(sql)

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
    """ get cell text or None """
    result = None
    if nonempty_cell(cell):
        result = cell.strip()
        if not isinstance(result, str):
            result = unicode(result, 'utf8')
    return result

def text_field(cell):
    """ get text or NULL """
    cell = text_or_none(cell)
    if cell:
        cell = re.escape(cell)
        return f"'{cell.encode('utf-8')}'"
    return 'NULL'

def date_field(cell):
    """ get date or NULL """
    if isinstance(cell, str):
        cell = strdate_or_none(cell)
        if cell:
            return f"'{cell.year}-{cell.month}-{cell.day}'"
    return 'NULL'

def int_field(cell):
    """ get int or NULL """
    cell = atoi(cell)
    if cell:
        return str(cell)
    return 'NULL'

def sex_field(cell):
    """ get sex or NULL """
    cell = sex_or_none(cell)
    if cell:
        return f"'{cell}'"
    return 'NULL'

def strdate_or_none(cell):
    """ get date or NULL """
    def year_from_text(string):
        """ get year """
        year = None
        item = re.compile('\d+')
        dgs = item.findall(string)
        if dgs and len(dgs):
            year = int(dgs[0])
            if year < 1000:
                year = 1900
        return year

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
        parts = cell.split('.')
        if len(parts) > 2:
            year = parts[2]
            if year:
                try:
                    result = datetime(int(year), int(parts[1]), int(parts[0]))
                except ValueError:
                    result = None
        else:
            parts = cell.split()
            if len(parts) == 3:
                year = year_from_text(parts[2])
                if year:
                    try:
                        result = datetime(int(year), dmonths[parts[1]], int(parts[0]))
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
        if result == 'м':
            result = 'M'
        else:
            result = 'F'
    return result

def int_or_none(cell):
    """ get int or None """
    result = None
    if nonempty_cell(cell):
        result = int(cell)
    return result

def get_uid(tbl):
    """ get uid or None """
    uid = None
    a_list = tbl.findAll('a')
    for anchor in a_list:
        href = anchor['href']
        if href.startswith('javascript:indstat('):
            item = re.compile('javascript:indstat\((\d+)\,\d+\)')
            dgs = item.findall(href)
            if len(dgs):
                uid = int(dgs[0])
                break
    return uid

def geocacher_format_insert_string(pid):
    """ geocacher format insert string """
    # try open profile
    fields = str(pid)
    url = f'http://www.geocaching.su/profile.php?pid={pid}'
    loaded = False
    cnter = 0
    fhandler = open('cant_open_profile.txt', 'w')

    while not loaded and cnter < 100:
        try:
            yplib.get(url)
            loaded = True
        except BrowserStateError:
            cnter += 1

    if not loaded:
        print(f'cannot go to {url}')
        fhandler.write(url)
        return False

    fhandler.close()

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
            if title.startswith('Псевдоним:'):
                theuser['nickname'] = data
                continue
            if title.startswith('Страна:'):
                theuser['country'] = data
                continue
            if title.startswith('Область:'):
                theuser['oblast'] = data
                continue
            if title.startswith('Нас.пункт'):
                theuser['town'] = data
                continue
            if title.startswith('Создал тайников:'):
                theuser['created'] = data
                continue
            if title.startswith('Нашел тайников:'):
                theuser['found'] = data
                continue
            if title.startswith('Рекомендовал тайников:'):
                theuser['recommended'] = data
                continue
            if title.startswith('Фотоальбомы:'):
                theuser['photo_albums'] = data
                continue
            if title.startswith('Был на сайте'):
                theuser['last_visited'] = data
                continue
            if title.startswith('Дата регистрации:'):
                theuser['registered'] = data
                continue
            if title.startswith('Сообщений в форумах:'):
                theuser['forum_posts'] = data

    uid = get_uid(tbl)
    fields += f',{int_field(uid)}'
    # pid uid nickname name birstday sex country oblast town phone icq web created_caches
    # found_caches photo_albums register_date last_login forum_posts
    fields += f",{text_field(theuser.get('nickname') or '')}"  # nickname
    fields += f",{text_field(all_cells[2])}"  # name
    fields += f',{date_field(all_cells[3])}'  # birstday
    fields += f',{sex_field(all_cells[4])}'  # sex
    fields += f",{text_field(theuser.get('country') or '')}"  # country
    fields += f",{text_field(theuser.get('oblast') or '')}"  # oblast

    fields += f",{text_field(theuser.get('town') or '')}"  # town
    fields += f",{text_field(all_cells[9])}"  # phone

    fields += f",{int_field(theuser.get('created') or 0)}"  # created_caches
    fields += f",{int_field(theuser.get('found') or 0)}"  # found_caches
    fields += f",{int_field(theuser.get('photo_albums') or 0)}"  # photo_albums

    fields += f",{date_field(theuser.get('registered') or '')}"  # register_date
    fields += f",{date_field(theuser.get('last_visited') or '')}"  # last_login
    fields += f",{int_field(theuser.get('forum_posts') or 0)}"  # forum_posts

    return f"({fields})".replace('%', '%%')

def check_user_profile(geocacher):
    """ check user profile """
    url = f'http://www.geocaching.su/profile.php?pid={geocacher.pid}'
    loaded = False
    cnter = 0
    fhandler = open('cant_open_profile.txt', 'w')
    while not loaded and cnter < 100:
        try:
            yplib.get(url)
            loaded = True
        except BrowserStateError:
            cnter += 1

    fhandler.close()
    if not loaded:
        print(f'cannot go to {url}')
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
    user.gps = None
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
    """ main procedure """
    load_geocachers = False
    load_absent_geocachers = False

    if not switch_off_status_updated():
        return False

    start = time()

    cursor = connection.cursor()

    cursor.execute('select * from geocacher')

    yplib.set_up()
    yplib.set_debugging(False)


    yplib.post2('http://www.geocaching.su/?pn=108',
            (('Log_In', 'Log_In'), ('email', 'galdor@ukr.net'), ('passwd', 'zaebalixakeryvas'), ('longterm', '1')))

    soup=yplib.soup()

    anchor = soup.find('a', attrs={'class': "profilelink"}, text='galdor')
    if not anchor:
        print('Authorization failed')
        return False

    if load_geocachers:
        Geocacher.objects.all().delete()
        cntr_list = []
        all_id = []
        for page in range(2500):
            print('page', page + 1)

            user_list = []
            yplib.post2('http://www.geocaching.su/?pn=108',
                (('sort', '1'), ('page', str(page)),
                 ('in_page', '100'), ('updown', '1')))
            soup=yplib.soup()
            a_list = soup.findAll('a', {'class':"profilelink"})
            tag = re.compile('\?pid=(\d+)')
            for anchor in a_list[:-1]:
                if anchor.get('onclick'):
                    user_id = tag.findall(anchor['onclick'])[0]
                    login = anchor.text.encode('utf8')
                    if user_id not in all_id:
                        user_list.append({'id': user_id, 'login': login})
                        all_id.append(user_id)

            if user_list == cntr_list:
                break

            cntr_list = user_list
            check_id_list(user_list)


    if load_absent_geocachers:
        pid_list = (469, 406, 1224, 4400, 11910,  4456, 13439,  7707, 8887, 3156, 8094)
        user_list = [{'id': pid, 'login': u''} for pid in pid_list]

        check_id_list(user_list)

    elapsed = time() - start
    print("Elapsed time -->", elapsed)
    switch_on_status_updated()
    log('gcsu_geocachers', 'OK')
    return True

if __name__ == '__main__':
    main()
