#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time
from gpsfun.main.db_utils import execute_query
from django.conf import settings
from gpsfun.main.models import switch_off_status_updated, switch_on_status_updated, log

def patch_it(name):
    folder = settings.SCRIPTS_ROOT
    f = open(folder+name, 'r')
    text = f.read()
    queries = text.split(';')
    for sql in queries:
        sql = sql.strip()
        if not sql.startswith('SELECT') and not sql.startswith('select') and len(sql):
            print
            print sql
            execute_query(sql)
    
def main():
    #if not switch_off_status_updated():
        #return False
    
    start = time() 
   
    sql_batches = ('set_cach_country_code.sql', 'set_cach_oblast_code.sql', 'set_country_iso_for_geocachers.sql', 
                   'set_admin_code_to_geocacher.sql', 'set_geonames_to_cach.sql', 'set_cache_country_subject.sql',
                   'crimea.sql')

    for name in sql_batches:
        patch_it('sql/'+name)
        print name, ' processed'
        
    elapsed = time() - start
    print "Elapsed time -->", elapsed
    #switch_on_status_updated()
    log('gcsu_patch', 'OK')
    
if __name__ == '__main__':
    main()
