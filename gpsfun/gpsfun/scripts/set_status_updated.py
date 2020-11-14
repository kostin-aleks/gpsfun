#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gpsfun.main.models import Variable, log
from DjHDGutils.dbutils import get_object_or_none

def main():
    updated = get_object_or_none(Variable, name='updated')
    if not updated:
        return
    if updated.value != 'successful':
        return
    

    is_updating = get_object_or_none(Variable, name='updating')
    if not is_updating:
        return
    is_updating.value = '0'
    is_updating.save()
    
    log('gcsu', 'succsess')
    


if __name__ == '__main__':
    main()
