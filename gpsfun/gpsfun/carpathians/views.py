# coding: utf-8
from django.shortcuts import render
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from gpsfun.DjHDGutils.misc import atoi
from django.contrib import messages


def routes(request):
    return render(
        request,
        'Routes/routes.html',
        {})


