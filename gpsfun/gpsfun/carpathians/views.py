"""
views related to carpathians
"""

import django_filters
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
from django.urls import reverse
import django_tables2 as tables
from django_tables2.config import RequestConfig

from gpsfun.main.Carpathians.models import Ridge, Peak, Route


class PeakFilter(django_filters.FilterSet):
    """
    Filter Set to filter by peak
    """
    class Meta:
        model = Peak
        fields = []


class PeakTable(tables.Table):
    """
    Table for peaks
    """
    slug = tables.Column(accessor='slug', verbose_name="")
    name = tables.Column(accessor='name', verbose_name="Название")
    height = tables.Column(accessor='height', verbose_name="Высота, м")
    ridge = tables.Column(accessor='ridge__name', verbose_name="Район")

    def render_slug(self, value):
        """render slug"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('peak', args=[value]),
            value)

    def render_ridge(self, value, record):
        """render field ridge"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('ridge', args=[record.ridge.slug]),
            value)

    class Meta:
        attrs = {'class': 'table'}


class RidgeFilter(django_filters.FilterSet):
    """
    Filter Set to filter by ridge
    """
    class Meta:
        model = Ridge
        fields = []


class RidgeTable(tables.Table):
    """
    Table for ridges
    """
    slug = tables.Column(accessor='slug', verbose_name="")
    name = tables.Column(accessor='name', verbose_name="")

    def render_slug(self, value):
        """render field slug"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('ridge', args=[value]),
            value)

    class Meta:
        attrs = {'class': 'table'}


class RouteFilter(django_filters.FilterSet):
    """
    Filter Set to filter by route
    """
    class Meta:
        model = Route
        fields = []


class RouteTable(tables.Table):
    """
    Table for routes
    """
    route_id = tables.Column(accessor='id', verbose_name="route_id")
    number = tables.Column(accessor='number', verbose_name="#")
    name = tables.Column(accessor='name', verbose_name="Название")
    difficulty = tables.Column(accessor='difficulty', verbose_name="КТ")
    peak = tables.Column(accessor='peak__name', verbose_name="Вершина")
    height = tables.Column(accessor='peak__height', verbose_name="Высота")
    author = tables.Column(accessor='author', verbose_name="Автор")
    year = tables.Column(accessor='year', verbose_name="Год")

    def render_route_id(self, value):
        """render field route_id"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('route', args=[value]),
            value)

    def render_peak(self, value, record):
        """render field peak"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('peak', args=[record.peak.slug]),
            value)

    def render_name(self, value, record):
        """render field name"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('route', args=[record.id]),
            value)

    class Meta:
        attrs = {'class': 'table'}


def ridges(request):
    """
    return page with ridges
    """
    order_by = 'name'
    qs = Ridge.objects.all().order_by(order_by)

    f = RidgeFilter(request.GET, queryset=qs)

    ridge_table = RidgeTable(f.qs)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(ridge_table)

    return render(
        request,
        'Routes/ridges.html',
        {'table': ridge_table})


def ridge(request, slug):
    """
    return page with ridge
    """
    the_ridge = get_object_or_404(Ridge, slug=slug)

    return render(
        request,
        'Routes/ridge.html',
        {'ridge': the_ridge})


def peak(request, slug):
    """
    return page for the peak
    """
    the_peak = get_object_or_404(Peak, slug=slug)

    return render(
        request,
        'Routes/peak.html',
        {'peak': the_peak})


def route(request, route_id):
    """
    return page for the route
    """
    the_route = get_object_or_404(Route, pk=route_id)

    return render(
        request,
        'Routes/route.html',
        {'route': the_route})


def routes(request):
    """
    return list of routes
    """
    order_by = 'number'
    qs = Route.objects.all().order_by(order_by)

    f = RouteFilter(request.GET, queryset=qs)

    routes_table = RouteTable(f.qs)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(routes_table)

    return render(
        request,
        'Routes/routes.html',
        {'table': routes_table})


def peaks(request):
    """
    return list of peaks
    """
    order_by = 'name'
    qs = Peak.objects.all().order_by(order_by)

    f = PeakFilter(request.GET, queryset=qs)

    peaks_table = PeakTable(f.qs)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(peaks_table)

    return render(
        request,
        'Routes/peaks.html',
        {'table': peaks_table})
