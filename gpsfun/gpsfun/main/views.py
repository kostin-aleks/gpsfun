from django.template import RequestContext
from django.shortcuts import render
from gpsfun.main.models import Variable
from gpsfun.main.db_utils import get_object_or_none
import re


def homepage(request):
    return render(request,'index.html', {'title': ''})


def update(request):
    return render(request, 'db_update.html', {})


def updating():
    r = False
    is_updating = get_object_or_none(Variable, name='updating')
    if is_updating and is_updating.value == '1':
        r = True
    return r


def url2su(ref):
    r = False
    pwp = re.compile('.+\/su\/.*')
    if pwp.match(ref):
        r = True
    return r


