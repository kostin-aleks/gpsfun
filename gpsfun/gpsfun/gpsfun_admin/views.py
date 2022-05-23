"""
gps fun admin views
"""

from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import django_tables2 as tables
from django_tables2.config import RequestConfig

from gpsfun.main.models import LogUpdate, LogCheckData


@login_required
def index(request):
    """
    index view
    """
    return render(
        request,
        'gpsfun_admin/index.html',
        {})


class LogUpdateTable(tables.Table):
    """
    Log Update Table
    """
    update_type = tables.Column()
    update_date = tables.Column()
    message = tables.Column()

    def render_update_date(self, value):
        """ render update date """
        return value.strftime('%Y-%m-%d')

    class Meta:
        template_name = "django_tables2/bootstrap.html"


@login_required
def data_updating_log(request):
    """
    log updating data
    """
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
    """
    last updates
    """
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
        if items:
            data.append(items[0])

    return render(
        request,
        'gpsfun_admin/last_update.html',
        dict(data=data, ))


class CheckDataTable(tables.Table):
    """
    Check Data Table
    """
    checking_date = tables.Column(verbose_name=_(
        "Checked"), accessor='checking_date')
    geocacher_count = tables.Column(verbose_name=_(
        "Geocachers count"), accessor='geocacher_count')
    geocacher_wo_country_count = tables.Column(
        verbose_name=_("Geocachers from an unknown country"),
        accessor='geocacher_wo_country_count')
    geocacher_wo_region_count = tables.Column(
        verbose_name=_("Geocachers from an unknown region"),
        accessor='geocacher_wo_region_count')
    cache_count = tables.Column(verbose_name=_(
        "Caches count"), accessor='cache_count')
    cache_wo_country_count = tables.Column(
        verbose_name=_("Caches from an unknown country"),
        accessor='cache_wo_country_count')
    cache_wo_region_count = tables.Column(
        verbose_name=_("Caches from an unknown region"),
        accessor='cache_wo_region_count')
    cache_wo_author_count = tables.Column(
        verbose_name=_("Caches with an unknown author"),
        accessor='cache_wo_author_count')

    def render_update_date(self, value):
        """ render update date """
        return value.strftime('%Y-%m-%d')

    class Meta:
        template_name = "django_tables2/bootstrap.html"


@login_required
def check_data(request):
    """
    check data
    """
    qs = LogCheckData.objects.all().order_by('-checking_date')
    table = CheckDataTable(qs)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(table)

    return render(
        request,
        'list.html',
        {'table': table,
         'title': "Check Data"})
