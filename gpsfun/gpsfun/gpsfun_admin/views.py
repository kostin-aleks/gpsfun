# coding: utf-8
from gpsfun.main.models import LogUpdate

from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

import django_tables2 as tables
from django_tables2.config import RequestConfig


@login_required
def index(request):
    return render(
        request,
        'gpsfun_admin/index.html',
        {})

class LogUpdateTable(tables.Table):
    update_type = tables.Column()
    update_date = tables.Column()
    message = tables.Column()

    def render_update_date(self, value):
        return value.strftime('%Y-%m-%d')

    class Meta:
        template_name = "django_tables2/bootstrap.html"


@login_required
def data_updating_log(request):
    items = LogUpdate.objects.all().order_by('-update_date')

    table = LogUpdateTable(items)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(table)

    return render(
        request,
        'list.html',
        {'table': table,
         'title': "Updating Log"})


@login_required
def last_updates(request):
    types = ('map',
             'gcsu',
             'kret',
             'map_gcsu_caches',
             'map_ocpl_caches',
             'map_set_location',
             'gcsu_caches',
             'gcsu_geocachers',
             'gcsu_patch',
             'gcsu_location',
             'gcsu_logs',
             'gcsu_casherstat',
             'gcsu_cashstat',
             'map_occom_caches',
             'map_shukach',
             'upd_gcsu_cachers',
             'upd_gcsu_caches',
             )
    data = []
    for type_ in types:
        items = list(
            LogUpdate.objects.filter(
                update_type=type_).order_by('-update_date')[:1])
        if items and len(items):
            data.append(items[0])

    return render(
        request,
        'gpsfun_admin/last_update.html',
        dict(data=data, ))
