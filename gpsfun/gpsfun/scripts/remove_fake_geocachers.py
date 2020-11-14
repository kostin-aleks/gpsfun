#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time
from gpsfun.main.GeoCachSU.models import Geocacher

def main():
    start = time()

    n = 0
    fh = open('cant_open_user_profile.txt', 'r')
    for line in fh:
        pid, reason = line.replace('\n','').split(',')
        if reason == 'np':
            n += 1
            print pid
            Geocacher.objects.get(pid=pid).delete()
    fh.close()
    elapsed = time() - start
    print "Elapsed time -->", elapsed
    print "Removed geocachers %d" % n

if __name__ == '__main__':
    main()
