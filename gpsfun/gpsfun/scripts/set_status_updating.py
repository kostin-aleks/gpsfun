#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gpsfun.main.models import Variable
from DjHDGutils.dbutils import get_object_or_none

def main():
    is_updating = get_object_or_none(Variable, name='updating')
    if is_updating is None:
        return
    is_updating.value = '1'
    is_updating.save()
    
    updated = get_object_or_none(Variable, name='updated')
    if updated is None:
        return
    updated.value = 'successful'
    updated.save()


if __name__ == '__main__':
    main()
