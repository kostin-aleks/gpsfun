#!/usr/bin/env python
# -*- coding: utf-8 -*-

import djyptestutils as yplib
from time import time
from datetime import datetime
import re
from _mechanize_dist import BrowserStateError
from gpsfun.main.GeoCachSU.models import Geocacher, \
     LogCreateCach, LogSeekCach, LogRecommendCach, LogPhotoAlbum
from gpsfun.main.models import log

def nonempty_cell(cell):
    r = True
    if not cell or cell=='&nbsp;':
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

def log_error(fh, pid, reason=''):
    if fh:
        fh.write('%s,%s\n' % (pid, reason))

def main():
    #if not switch_off_status_updated():
        #return False

    LOAD_CREATED_CACHE_LOGS = True
    LOAD_SEEK_CACHE_LOGS = True
    LOAD_RECOMMEND_CACHE_LOGS = True
    LOAD_PHOTOALBUM_LOGS = True

    start = time()

    yplib.set_up()
    yplib.set_debugging(False)

    r = yplib.post2('http://www.geocaching.su/?pn=108',
            (('Log_In','Log_In'), ('email', 'galdor@ukr.net'), ('passwd','zaebalixakeryvas'), ('longterm', '1')))

    soup=yplib.soup()

    a = soup.find('a', attrs={'class':"profilelink"}, text='galdor')
    if not a:
        print 'Authorization failed'
        return False
    print
    print 'BEGIN'
    fh = open('cant_open_user_profile.txt', 'w')
    if LOAD_CREATED_CACHE_LOGS:
        LogCreateCach.objects.all().update(updated=False)
        print 'updating of creating logs'
        cachers = Geocacher.objects.all().values_list('pid', 'uid')
        t = re.compile('\?pn\=101\&cid=(\d+)')
        t1 = re.compile(u'создан\s+(\d\d\.\d\d\.\d\d\d\d)')
        for cacher in cachers:
            if cacher[1]:
                url = 'http://www.geocaching.su/site/popup/userstat.php?s=1&uid=%s'%cacher[1]
                try:
                    yplib.get(url)
                except BrowserStateError:
                    log_error(fh, cacher[1], 'bse')
                    continue
                soup=yplib.soup()
                tbl = soup.find('table', attrs={'class':'pages'})
                if tbl:
                    rows = tbl.findAll('tr')
                    for row in rows:
                        cach_pid = created_date = None
                        coauthor = False
                        cell = row.find('td')
                        if cell:
                            a_list = cell.findAll('a')
                            for a in a_list:
                                cach_pid=None
                                parts = t.findall(a['href'])
                                if len(parts):
                                    cach_pid = int(parts[0])

                            txt = cell.text
                            if u'(соавтор)' in txt:
                                coauthor = True
                            found = t1.findall(txt)
                            if found:
                                created_date = found[0]
                                created_date = date_or_none(created_date)
                            if cach_pid:
                                print cacher[0], cach_pid, txt.encode('utf8')
                                the_log, created = LogCreateCach.objects.\
                                    get_or_create(
                                        author_pid=cacher[0],
                                        cach_pid=cach_pid)
                                the_log.created_date = created_date
                                the_log.coauthor = coauthor
                                the_log.updated = True
                                the_log.save()
                else:
                    log_error(fh, cacher[1], 'npc')
        LogCreateCach.objects.filter(updated=False).delete()

    if LOAD_SEEK_CACHE_LOGS:
        LogSeekCach.objects.all().update(updated=False)
        cachers = Geocacher.objects.all().values_list('pid', 'uid')#.filter(pid=18849)
        t = re.compile('\?pn\=101\&cid=(\d+)')
        t1 = re.compile(u'создан\s+(\d\d\.\d\d\.\d\d\d\d)')
        t2 = re.compile(u'найден\s+(\d\d\.\d\d\.\d\d\d\d)')
        t3 = re.compile(u'оценен\s+на\s+(\d)')

        for cacher in cachers:
            if cacher[1]:
                url = 'http://www.geocaching.su/site/popup/userstat.php?s=2&uid=%s'%cacher[1]
                try:
                    yplib.get(url)
                    soup=yplib.soup()
                except BrowserStateError:
                    log_error(fh, cacher[1], 'bse')
                    continue

                tbl = soup.find('table', attrs={'class':'pages'})
                if tbl:
                    rows = tbl.findAll('tr')
                    for row in rows:
                        cach_pid = found_date = grade = None
                        cell = row.find('td')
                        if cell:
                            a_list = cell.findAll('a')
                            for a in a_list:
                                cach_pid=None
                                parts = t.findall(a['href'])
                                if len(parts):
                                    cach_pid = int(parts[0])

                            txt = cell.text
                            found = t3.findall(txt)
                            if found:
                                g = found[0]
                                grade = int_or_none(g)
                            found = t2.findall(txt)
                            if found:
                                found_date = found[0]
                                found_date = date_or_none(found_date)
                            if cach_pid:
                                print cacher[0], cach_pid, txt.encode('utf8')
                                the_log, created = LogSeekCach.objects.\
                                    get_or_create(
                                        cacher_pid=cacher[0],
                                        cach_pid=cach_pid, )
                                the_log.found_date = found_date
                                the_log.grade = grade
                                the_log.updated = True
                                the_log.save()
                else:
                    log_error(fh, cacher[1], 'npf')
        LogSeekCach.objects.filter(updated=False).delete()

    if LOAD_RECOMMEND_CACHE_LOGS:
        LogRecommendCach.objects.all().update(updated=False)
        cachers = Geocacher.objects.all().values_list('pid', 'uid')
        t = re.compile('\?pn\=101\&cid=(\d+)')
        for cacher in cachers:
            if cacher[1]:
                url = 'http://www.geocaching.su/site/popup/userstat.php?s=3&uid=%s'%cacher[1]
                try:
                    yplib.get(url)
                    soup=yplib.soup()
                except BrowserStateError:
                    log_error(fh, cacher[1], 'bse')
                    continue
                tbl = soup.find('table', attrs={'class':'pages'})
                if tbl:
                    rows = tbl.findAll('tr')
                    for row in rows:
                        cach_pid = found_date = grade = None
                        cell = row.find('td')
                        if cell:
                            a_list = cell.findAll('a')
                            for a in a_list:
                                cach_pid=None
                                parts = t.findall(a['href'])
                                if len(parts):
                                    cach_pid = int(parts[0])

                            txt = cell.text
                            if cach_pid:
                                print cacher[0], cach_pid, txt.encode('utf8')
                                the_log, created = LogRecommendCach.\
                                    objects.get_or_create(
                                        cacher_pid=cacher[0],
                                        cach_pid=cach_pid)
                                the_log.updated = True
                                the_log.save()
                else:
                    log_error(fh, cacher[1], 'npr')
        LogRecommendCach.objects.filter(updated=False).delete()

    if LOAD_PHOTOALBUM_LOGS:
        LogPhotoAlbum.objects.all().update(updated=False)
        cachers = Geocacher.objects.all().values_list('pid', 'uid')
        t = re.compile('showmemphotos\.php\?cid=(\d+)')

        for cacher in cachers:
            if cacher[1]:
                url = 'http://www.geocaching.su/site/popup/userstat.php?s=4&uid=%s'%cacher[1]
                try:
                    yplib.get(url)
                    soup=yplib.soup()
                except BrowserStateError:
                    log_error(fh, cacher[1], 'bse')
                    continue
                tbl = soup.find('table', attrs={'class':'pages'})
                if tbl:
                    rows = tbl.findAll('tr')
                    for row in rows:
                        cach_pid = found_date = grade = None
                        cell = row.find('td')
                        if cell:
                            a_list = cell.findAll('a')
                            for a in a_list:
                                cach_pid=None
                                parts = t.findall(a['href'])
                                if len(parts):
                                    cach_pid = int(parts[0])

                            txt = cell.text
                            if cach_pid:
                                print cacher[0], cach_pid, txt.encode('utf8')
                                the_log, created = LogPhotoAlbum.\
                                    objects.get_or_create(
                                        cacher_pid=cacher[0],
                                        cach_pid=cach_pid)
                                the_log.updated = True
                                the_log.save()
                else:
                    log_error(fh, cacher[1], 'npp')
        LogPhotoAlbum.objects.filter(updated=False).delete()

    elapsed = time() - start
    print "Elapsed time -->", elapsed
    #switch_on_status_updated()
    log('gcsu_logs', 'OK')
    fh.close()

if __name__ == '__main__':
    main()
