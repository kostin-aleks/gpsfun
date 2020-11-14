#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gpsfun.main.models import Variable, log
from DjHDGutils.dbutils import get_object_or_none

def main():
    updated = get_object_or_none(Variable, name='map_updated')
    if not updated:
        return
    updated.value = 'successful'
    updated.save()
    
    log('map', 'success')
    


if __name__ == '__main__':
    main()
