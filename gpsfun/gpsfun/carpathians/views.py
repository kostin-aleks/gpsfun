# coding: utf-8
import django_filters
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from gpsfun.DjHDGutils.misc import atoi
from django.contrib import messages
import django_tables2 as tables
from django_tables2.config import RequestConfig
from gpsfun.tableview import table, widgets, datasource, controller
from gpsfun.main.Carpathians.models import Ridge, Peak, Route


class PeakFilter(django_filters.FilterSet):
    class Meta:
        model = Peak
        fields = []


class PeakTable(tables.Table):
    slug = tables.Column(accessor='slug', verbose_name="")
    name = tables.Column(accessor='name', verbose_name="Название")
    height = tables.Column(accessor='height', verbose_name="Высота, м")
    ridge = tables.Column(accessor='ridge__name', verbose_name="Район")

    def render_slug(self, value):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('peak', args=[value]),
            value)

    def render_ridge(self, value, record):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('ridge', args=[record.ridge.slug]),
            value)

    class Meta:
        attrs = {'class': 'table'}


class RidgeFilter(django_filters.FilterSet):
    class Meta:
        model = Ridge
        fields = []


class RidgeTable(tables.Table):
    slug = tables.Column(accessor='slug', verbose_name="")
    name = tables.Column(accessor='name', verbose_name="")

    def render_slug(self, value):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('ridge', args=[value]),
            value)

    class Meta:
        attrs = {'class': 'table'}


class RouteFilter(django_filters.FilterSet):
    class Meta:
        model = Route
        fields = []


class RouteTable(tables.Table):
    id = tables.Column(accessor='id', verbose_name="id")
    number = tables.Column(accessor='number', verbose_name="#")
    name = tables.Column(accessor='name', verbose_name="Название")
    difficulty = tables.Column(accessor='difficulty', verbose_name="КТ")
    peak = tables.Column(accessor='peak__name', verbose_name="Вершина")
    height = tables.Column(accessor='peak__height', verbose_name="Высота")
    author = tables.Column(accessor='author', verbose_name="Автор")
    year = tables.Column(accessor='year', verbose_name="Год")

    def render_id(self, value):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('route', args=[value]),
            value)

    def render_peak(self, value, record):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('peak', args=[record.peak.slug]),
            value)

    def render_name(self, value, record):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('route', args=[record.id]),
            value)

    class Meta:
        attrs = {'class': 'table'}


def ridges(request):
    order_by = 'name'
    qs = Ridge.objects.all().order_by(order_by)

    f = RidgeFilter(request.GET, queryset=qs)

    table = RidgeTable(f.qs)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(table)
    return render(
        request,
        'Routes/ridges.html',
        {'table': table})


def ridge(request, slug):
    ridge = get_object_or_404(Ridge, slug=slug)

    return render(
        request,
        'Routes/ridge.html',
        {'ridge': ridge})


def peak(request, slug):
    peak = get_object_or_404(Peak, slug=slug)

    return render(
        request,
        'Routes/peak.html',
        {'peak': peak})


def route(request, route_id):
    route = get_object_or_404(Route, pk=route_id)

    return render(
        request,
        'Routes/route.html',
        {'route': route})


def routes(request):
    order_by = 'number'
    qs = Route.objects.all().order_by(order_by)

    f = RouteFilter(request.GET, queryset=qs)

    table = RouteTable(f.qs)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(table)
    return render(
        request,
        'Routes/routes.html',
        {'table': table})


def peaks(request):
    order_by = 'name'
    qs = Peak.objects.all().order_by(order_by)

    f = PeakFilter(request.GET, queryset=qs)

    table = PeakTable(f.qs)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(table)
    return render(
        request,
        'Routes/peaks.html',
        {'table': table})
