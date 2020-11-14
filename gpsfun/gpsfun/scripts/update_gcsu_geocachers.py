#!/usr/bin/env python
# -*- coding: utf-8 -*-

import djyptestutils as yplib
from time import time
from datetime import datetime
import re
from DjHDGutils.misc import atoi
from gpsfun.main.GeoCachSU.models import Geocacher, Cacher
from gpsfun.main.models import log
from _mechanize_dist import BrowserStateError
from DjHDGutils.dbutils import get_object_or_none
from gpsfun.main.utils import get_uid, text_or_none, nonempty_cell,\
     strdate_or_none, sex_or_none


def check_id_list(user_list):
    for pid in user_list:
        check_geocacher(pid)


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


def int_or_none(cell):
    r = None
    if nonempty_cell(cell):
        r = int(cell)
    return r


def add_geocacher(pid):
    url = 'http://www.geocaching.su/profile.php?pid=%s' % pid
    print url
    try:
        yplib.get(url)
    except BrowserStateError:
        pass

    try:
        soup = yplib.soup()
    except UnicodeDecodeError:
        print 'exception, pid=%s' % pid
        return
    tbl = soup.find('table', {'class': 'pages'})
    rows = tbl.findAll('tr')
    all_cells = []
    for row in rows:
        cells = row.findAll('th')
        for cell in cells:
            all_cells.append(cell.text.encode('utf8'))

    user = Cacher()
    user.pid = pid
    user.uid = get_uid(tbl)
    user.nickname = text_or_none(all_cells[1])
    if user.nickname:
        print user.nickname
    if user.nickname:
        user.nickname = user.nickname[:64]
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
    if user.web:
        user.web = user.web[:128]
    user.gps = None  #gps[:255].encode if gps else None
    user.created_caches = int_or_none(all_cells[18])
    user.found_caches = int_or_none(all_cells[19])
    user.photo_albums = int_or_none(all_cells[21])
    if len(all_cells) > 23:
        user.register_date = date_or_none(all_cells[-3])
        if user.register_date is None:
            user.register_date = date_or_none(all_cells[-2])
        user.last_login = date_or_none(all_cells[-2])
        user.forum_posts = int_or_none(all_cells[-1])

    geocacher = Geocacher.objects.create(pid=pid)
    geocacher.__dict__.update(user.__dict__)
    print 'save', geocacher.pid
    if user.web:
        print user.web
    geocacher.save()

    return True


def check_geocacher(pid):
    def geocacher_exists(pid):
        return get_object_or_none(Geocacher, pid=pid)

    if geocacher_exists(pid):
        return True
    add_geocacher(pid)


def main():
    start = time()

    yplib.setUp()
    yplib.set_debugging(False)

    r = yplib.post2('http://www.geocaching.su/?pn=108',
            (('Log_In', 'Log_In'), ('email', 'galdor@ukr.net'),
            ('passwd', 'zaebalixakeryvas'), ('longterm', '1')))

    soup = yplib.soup()

    a = soup.find('a', attrs={'class': "profilelink"}, text='galdor')
    if not a:
        print 'Authorization failed'
        return False

    excluded_id = [118575, 111821, 109578, 96417]

    all_id = []
    for k in range(10):
        r = yplib.post2('http://www.geocaching.su/?pn=108',
            (('sort', '2'), ('page', str(k)),
            ('in_page', '1000'), ('updown', '2')))
        soup = yplib.soup()
        a_list = soup.findAll('a', {'class': "profilelink"})
        t = re.compile('\?pid=(\d+)')
        for a in a_list[:-1]:
            if a.get('onclick'):
                user_id = t.findall(a['onclick'])[0]
                #login = a.text.encode('utf8')
                if not (user_id in all_id) and not (user_id in excluded_id):
                    all_id.append(user_id)
        check_id_list(all_id)

    elapsed = time() - start
    print "Elapsed time -->", elapsed
    log('upd_gcsu_cachers', 'OK')

if __name__ == '__main__':
    main()
