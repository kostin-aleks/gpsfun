#!/usr/bin/env python
# -*- coding: utf-8 -*-

import djyptestutils as yplib
from time import time
from datetime import datetime
import re
from _mechanize_dist import BrowserStateError
from gpsfun.main.GeoCachSU.models import Geocacher, \
     LogCreateCach, LogSeekCach, LogRecommendCach, LogPhotoAlbum
from gpsfun.main.models import switch_off_status_updated, switch_on_status_updated, log
#import django
# django.setup()


def nonempty_cell(cell):
    r = True
    if not cell or cell == '&nbsp;':
        r = False
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


def int_or_none(cell):
    r = None
    if nonempty_cell(cell):
        r = int(cell)
    return r


def main():
    if not switch_off_status_updated():
        return False

    LOAD_CREATED_CACHE_LOGS = False
    LOAD_SEEK_CACHE_LOGS = False
    LOAD_RECOMMEND_CACHE_LOGS = False
    LOAD_PHOTOALBUM_LOGS = False

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
    print
    print 'BEGIN'
    if LOAD_CREATED_CACHE_LOGS:
        LogCreateCach.objects.all().delete()
        print 'delete create logs'
        cachers = Geocacher.objects.all()
        print cachers.count()
        t = re.compile('\?pn\=101\&cid=(\d+)')
        t1 = re.compile(u'создан\s+(\d\d\.\d\d\.\d\d\d\d)')
        for cacher in cachers:
            if cacher.uid:
                print cacher.pid, cacher.uid
                url = 'http://www.geocaching.su/site/popup/userstat.php?s=1&uid=%s' % cacher.uid
                try:
                    yplib.get(url)
                except BrowserStateError:
                    continue
                soup = yplib.soup()
                tbl = soup.find('table', attrs={'class': 'pages'})
                if tbl:
                    #print tbl
                    rows = tbl.findAll('tr')
                    #print len(rows)
                    for row in rows:
                        cach_pid = created_date = None
                        coauthor = False
                        cell = row.find('td')
                        if cell:
                            #print cell
                            a_list = cell.findAll('a')
                            for a in a_list:
                                cach_pid = None
                                parts = t.findall(a['href'])
                                if len(parts):
                                    cach_pid = int(parts[0])

                            txt = cell.text
                            print cacher.pid, cach_pid, txt.encode('utf8')
                            if u'(соавтор)' in txt:
                                coauthor = True
                            found = t1.findall(txt)
                            if found:
                                created_date = found[0]
                                created_date = date_or_none(created_date)
                            if cach_pid:
                                the_log = LogCreateCach(
                                    author_pid=cacher.pid,
                                    cach_pid=cach_pid)
                                the_log.created_date = created_date
                                the_log.coauthor = coauthor
                                the_log.save()
                                print 'saved'

    if LOAD_SEEK_CACHE_LOGS:
        LogSeekCach.objects.all().delete()
        cachers = Geocacher.objects.all()
        t = re.compile('\?pn\=101\&cid=(\d+)')
        t1 = re.compile(u'создан\s+(\d\d\.\d\d\.\d\d\d\d)')
        t2 = re.compile(u'найден\s+(\d\d\.\d\d\.\d\d\d\d)')
        t3 = re.compile(u'оценен\s+на\s+(\d)')

        fh = open('cant_open_userstat.txt', 'w')
        for cacher in cachers:
            if cacher.uid:
                print cacher.pid, cacher.uid
                url = 'http://www.geocaching.su/site/popup/userstat.php?s=2&uid=%s' % cacher.uid

                loaded = False
                cnter = 0

                while not loaded and cnter < 100:
                    try:
                        yplib.get(url)
                        soup = yplib.soup()
                        loaded = True
                    except BrowserStateError:
                        cnter += 1
                if not loaded:
                    print 'cannot go to %s' % url
                    fh.write(url)

                tbl = soup.find('table', attrs={'class': 'pages'})
                if tbl:
                    rows = tbl.findAll('tr')
                    for row in rows:
                        cach_pid = found_date = grade = None
                        cell = row.find('td')
                        if cell:
                            a_list = cell.findAll('a')
                            for a in a_list:
                                cach_pid = None
                                parts = t.findall(a['href'])
                                if len(parts):
                                    cach_pid = int(parts[0])

                            txt = cell.text
                            found = t3.findall(txt)
                            if found:
                                g = found[0]
                                grade = int_or_none(g)
                            print cacher.pid, cach_pid, txt.encode('utf8')
                            found = t2.findall(txt)
                            if found:
                                found_date = found[0]
                                found_date = date_or_none(found_date)
                            if cach_pid:
                                the_log = LogSeekCach(
                                    cacher_pid=cacher.pid,
                                    cach_pid=cach_pid)
                                the_log.found_date = found_date
                                the_log.grade = grade
                                the_log.save()
                                print 'saved'
        fh.close()

    if LOAD_RECOMMEND_CACHE_LOGS:
        LogRecommendCach.objects.all().delete()
        cachers = Geocacher.objects.all()
        t = re.compile('\?pn\=101\&cid=(\d+)')

        for cacher in cachers:
            if cacher.uid:
                print cacher.pid, cacher.uid
                url = 'http://www.geocaching.su/site/popup/userstat.php?s=3&uid=%s' % cacher.uid
                yplib.get(url)
                soup = yplib.soup()
                tbl = soup.find('table', attrs={'class': 'pages'})
                if tbl:
                    rows = tbl.findAll('tr')
                    for row in rows:
                        cach_pid = found_date = grade = None
                        cell = row.find('td')
                        if cell:
                            a_list = cell.findAll('a')
                            for a in a_list:
                                cach_pid = None
                                parts = t.findall(a['href'])
                                if len(parts):
                                    cach_pid = int(parts[0])

                            txt = cell.text
                            print cacher.pid, cach_pid, txt.encode('utf8')
                            if cach_pid:
                                the_log = LogRecommendCach(
                                    cacher_pid=cacher.pid,
                                    cach_pid=cach_pid)
                                the_log.save()
                                print 'saved'

    if LOAD_PHOTOALBUM_LOGS:
        LogPhotoAlbum.objects.all().delete()
        cachers = Geocacher.objects.all()
        t = re.compile('showmemphotos\.php\?cid=(\d+)')

        for cacher in cachers:
            if cacher.uid:
                print cacher.pid, cacher.uid
                url = 'http://www.geocaching.su/site/popup/userstat.php?s=4&uid=%s' % cacher.uid
                yplib.get(url)
                soup = yplib.soup()
                tbl = soup.find('table', attrs={'class': 'pages'})
                if tbl:
                    rows = tbl.findAll('tr')
                    for row in rows:
                        cach_pid = found_date = grade = None
                        cell = row.find('td')
                        if cell:
                            a_list = cell.findAll('a')
                            for a in a_list:
                                cach_pid = None
                                parts = t.findall(a['href'])
                                if len(parts):
                                    cach_pid = int(parts[0])

                            txt = cell.text
                            print cacher.pid, cach_pid, txt.encode('utf8')
                            if cach_pid:
                                the_log = LogPhotoAlbum(
                                    cacher_pid=cacher.pid, cach_pid=cach_pid)
                                the_log.save()
                                print 'saved'

    elapsed = time() - start
    print "Elapsed time -->", elapsed
    switch_on_status_updated()
    log('gcsu_logs', 'OK')

if __name__ == '__main__':
    main()
