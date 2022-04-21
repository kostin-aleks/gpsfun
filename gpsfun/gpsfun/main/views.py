"""
views for main
"""
import re
from django.shortcuts import render
from gpsfun.main.models import Variable
from gpsfun.main.db_utils import get_object_or_none


def homepage(request):
    """ homepage """
    return render(request,'index.html', {'title': ''})


def update(request):
    """ update """
    return render(request, 'db_update.html', {})


def updating():
    """ updating """
    is_updating = get_object_or_none(Variable, name='updating')
    if is_updating and is_updating.value == '1':
        return True
    return False


def url2su(ref):
    """ is url to geocaching.su ? """
    pwp = re.compile('.+\/su\/.*')
    if pwp.match(ref):
        return True
    return False
