#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

def only_ascii(s):
    return ''.join([ch for ch in s if ord(ch) < 128])

def main():
    if len(sys.argv) < 2:
        return
    for file_name in sys.argv[1:]:
        
        fi = open(file_name, "r+")
        data = fi.read();
        fi.close()
        
        fo = open(file_name+'.wpt', 'w')
        
        points = data.split('\n')
        for point in points:
            print
            print point
            fields = point.split(',')
            if len(fields) < 10:
                fo.write(point)
                continue
            print fields
            fields[-3] = ''
            fields[10] = only_ascii(fields[10])
            fields[1] = '%s-%s' % (fields[1], fields[10].strip())
            print fields
            fo.write(','.join(fields))
        fo.close()
if __name__ == '__main__':
    main()
