#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time
#from gpsfun.main.db_utils import execute_query
from gpsfun.main.GeoCachSU.models import Geocacher
from django.conf import settings
from gpsfun.main.models import switch_off_status_updated, switch_on_status_updated, log
    
def main():
    #if not switch_off_status_updated():
        #return False
    
    start = time() 
   
    geocachers = Geocacher.objects.filter(nickname__contains='\_')
    for geocacher in  geocachers:
        geocacher.nickname = geocacher.nickname.replace('\_', '_')
        geocacher.save()

    elapsed = time() - start
    print "Elapsed time -->", elapsed
    #switch_on_status_updated()
    
if __name__ == '__main__':
    main()
