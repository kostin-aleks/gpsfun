#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import connection

def get_cursor(sql, sql_args=None):
    cursor = connection.cursor()
    if sql_args:
        cursor.execute(sql, sql_args)
    else:
        cursor.execute(sql)
    return cursor

def main():
    def item_to_str(item):
        if type(item)!=type(u''):
            item = str(item)
        else:
            item = item.encode('cp1251') if item else ''
        
        return item
    
    THE_YEAR = 2010
    filename = "/tmp/geocachers.csv"
    file = open(filename, 'w')
    file.write('ID\tnick\tcreated\tfound\t2010 created\t2010 found\tcountry\tregion\tcountry iso\tregion code\r\n')
    
    sql = """
    SELECT gc.pid, gc.nickname, gc.created_caches, gc.found_caches, 
    (SELECT COUNT(cc.id) FROM log_create_cach cc WHERE cc.author_pid=gc.pid AND YEAR(created_date)=%s) as created_ ,
    (SELECT COUNT(sc.id) FROM log_seek_cach sc WHERE sc.cacher_pid=gc.pid AND YEAR(found_date)=%s) as found_,
    geoc.name, sub.name, gc.country_iso3, gc.admin_code 
    FROM geocacher gc 
    LEFT JOIN geo_country geoc ON gc.country_iso3=geoc.iso3
    LEFT JOIN geo_country_subject sub ON (gc.admin_code=sub.code AND geoc.iso=sub.country_iso)
    HAVING (created_ + found_) > 0
    ORDER BY found_ desc
    """
    cursor = get_cursor(sql, sql_args=[THE_YEAR, THE_YEAR])
    items = []
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        else:
            s = '\t'.join([item_to_str(item) for item in row])
            s = s + '\r\n'
            file.write(s)
    
    file.close()
    
if __name__ == '__main__':
    main()
