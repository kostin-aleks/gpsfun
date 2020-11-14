# coding: utf-8
import time
import itertools
from datetime import datetime, date
from lxml import etree
from django.urls import reverse
from django import forms
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.models import Max
from django.views.decorators.cache import cache_page
from django.utils.html import format_html

import django_tables2 as tables
from django_tables2.config import RequestConfig

from gpsfun.tableview import table, widgets, datasource, controller
from gpsfun.DjHDGutils.dbutils import iter_sql
from django.utils.translation import ugettext_lazy as _
from gpsfun.DjHDGutils.forms import RequestForm
from gpsfun.DjHDGutils.dbutils import get_object_or_none
from gpsfun.DjHDGutils.ajax import accept_ajax

from gpsfun.main.GeoCachSU.models import Cach, CachStat, Geocacher, \
     GEOCACHING_SU_CACH_TYPES, GEOCACHING_SU_REAL_TYPES, \
     GEOCACHING_SU_UNREAL_TYPES, LogSeekCach, LogCreateCach, \
     GeocacherStat, GEOCACHING_SU_ONMAP_TYPES, GeocacherSearchStat
from gpsfun.main.GeoCachSU.utils import populate_cach_type, \
     populate_country_iso3, populate_subjects, populate_countries_iso3
from gpsfun.main.GeoName.models import GeoCountry, GeoCountryAdminSubject, \
     country_iso_by_iso3, geocountry_by_code
from gpsfun.main.models import LogUpdate
from gpsfun.main.db_utils import sql2list, sql2val
from gpsfun.geocaching_su_stat.decorators import  it_isnt_updating, geocacher_su

from pygooglechart import SimpleLineChart, StackedHorizontalBarChart
from pygooglechart import Axis, PieChart3D
from quickchart import QuickChart

from gpsfun.main.utils import get_degree
from gpsfun.geocaching_su_stat.sql import RAWSQL


MONTH_SHORT_NAMES = [
    _('Jan'), _('Feb'), _('Mar'), _('Apr'), _('May'), _('Jun'),
    _('Jul'), _('Aug'), _('Sep'), _('Oct'), _('Nov'), _('Dec')
]


def geocaching_su_cach_url(pid):
    return "http://www.geocaching.su/?pn=101&cid=%s" % pid


def geocaching_su_geocacher_url(pid):
    return "http://www.geocaching.su/profile.php?pid=%s" % pid


class GPSFunTableController(controller.TableController):
    kind = None

    def filter_description(self):
        def valid_keys(afilter, kind):
            r = False
            if kind == 'geocacher_rate':
                if 'country' in afilter and 'subject' in afilter:
                    r = True
            if kind == 'cache_rate':
                if 'country' in afilter and 'cach_type' in afilter:
                    r = True
            return r

        def country_description(country):
            by_country = {'title': _('Country'), 'value': _("All")}
            if country and country != 'ALL':
                geocountry = geocountry_by_code(country)
                if geocountry:
                    by_country['value'] = _(geocountry.name)
                else:
                    by_country['value'] = country
            return by_country

        def subject_description(admin_subject, country):
            by_subject = {'title': _('Admin Subject'), 'value': _("All")}
            if admin_subject and admin_subject != 'ALL':
                geoadmin_subject = get_object_or_none(
                    GeoCountryAdminSubject,
                    country_iso=country_iso_by_iso3(country),
                    code=admin_subject)
                if geoadmin_subject:
                    by_subject['value'] = _(geoadmin_subject.name)
                else:
                    by_subject['value'] = admin_subject
            return by_subject

        if not self.filter.keys():
            return None
        if not valid_keys(self.filter, self.kind):
            return None

        d = []
        if self.kind == 'cache_rate':
            selected_values = self.filter.get('cach_type')
            if selected_values == ['']:
                selected_values = []

            if not selected_values or ('ALL' in selected_values) or \
               ('REAL' in selected_values and 'UNREAL' in selected_values):
                selected_values = []
            if selected_values:
                selected_values = distinct_types_list(selected_values)

            types = [GEOCACHING_SU_CACH_TYPES.get(type_) \
                     for type_ in selected_values \
                     if GEOCACHING_SU_CACH_TYPES.get(type_) is not None]

            if len(types) == 0:
                types = [_("Any")]
            if types:
                d.append({
                    'title': _('Cach Type'),
                    'value': types,
                    'type': 'list'})
            country = self.filter.get('country')
            d.append(country_description(country))
            d.append(subject_description(self.filter.get('subject'), country))

        if self.kind == 'geocacher_rate':
            country = self.filter.get('country')
            d.append(country_description(country))
            d.append(subject_description(self.filter.get('subject'), country))

        return d


class RankingFilter(RequestForm):
    cach_type = forms.MultipleChoiceField(
        required=False,
        label=_('Cach Type'),
        widget=forms.SelectMultiple(attrs={'size': '6'}))
    country = forms.ChoiceField(
        required=False,
        label=_('Country'),
        widget=forms.Select(
            attrs={'onchange': 'RateFilter.reload_subjects(this);'}))
    subject = forms.ChoiceField(
        required=False,
        label=_('Admin Subject'),
        widget=forms.Select(attrs={'id': 'ratefilter_subjects'}))

    def init(self):
        self._country = self.initial.get('country')
        if self._country is None:
            self._country = self.data.get('country')

        populate_cach_type(
            self.fields['cach_type'], self._request, add_empty=True)

        populate_countries_iso3(self.fields['country'],
                              self._request, add_empty=True)
        populate_subjects(self.fields['subject'],
                          self._request,
                          add_empty=True,
                          selected_country_iso=self._country)


class RateFilter(RequestForm):
    country = forms.ChoiceField(
        required=False,
        label=_('Country'),
        widget=forms.Select(
            attrs={'onchange': 'RateFilter.reload_subjects(this);'}))
    subject = forms.ChoiceField(
        required=False,
        label=_('Admin Subject'),
        widget=forms.Select(attrs={'id': 'ratefilter_subjects'}))

    def init(self):
        self._country = self.initial.get('country')
        if self._country is None:
            self._country = self.data.get('country')

        populate_country_iso3(self.fields['country'],
                              self._request, add_empty=True)
        populate_subjects(self.fields['subject'],
                          self._request,
                          add_empty=True,
                          selected_country_iso=self._country)

    def set_country(self, country):
        self._country = country
        populate_subjects(self.fields['subject'],
                          self._request,
                          selected_country_iso=self._country)


class BaseRankTable(table.TableView):
    _filter = None

    def apply_filter(self, filter, qs):
        self._filter = {}
        for k, v in filter.iteritems():
            self._filter[k] = v
        selected_values = filter.get('cach_type') or []
        if selected_values and ('REAL' in selected_values) \
           and ('UNREAL' in selected_values):
            pass
        elif selected_values and ('ALL' in selected_values):
            pass
        else:
            selected_values = distinct_types_list(selected_values)
            if len(selected_values):
                qs.filter(cach__type_code__in=selected_values)

        country = filter.get('country')
        if country and country != 'ALL':
            country = get_iso_by_iso3(country)
            qs.filter(cach__country_code=country)
            self._filter = filter

        subject = filter.get('subject', '')
        if subject and subject != 'ALL':
            if subject == '777':
                qs.filter(cach__country_code=country,
                          cach__admin_code__isnull=True)
            else:
                qs.filter(cach__country_code=country,
                          cach__admin_code=subject)

    def filtered(self):
        r = False
        if hasattr(self, '_filter'):
            r = self._filter is not None
        return r


class RankByList(BaseRankTable):
    pid = widgets.HrefWidget('ID',
                             width="55px",
                             refname='cach__code',
                             reverse='geocaching-su-cach-view',
                             reverse_column='cach_pid')
    cach_name = widgets.LabelWidget(_('Cach'), refname='cach__name')
    created = widgets.LabelWidget(_('Created'), refname='cach__created_date')
    author = widgets.HrefWidget(_('Author'),
                                refname='geocacher__nickname',
                                reverse='geocaching-su-geocacher-view',
                                reverse_column='geocacher__pid')
    recommend_count = widgets.LabelWidget(_('Recommendations'),
                                          refname='recommend_count')
    grade = widgets.LabelWidget(_('Grade'), refname='cach__grade')


class RankByComputedList(RankByList):
    found_count = widgets.LabelWidget(_('Found'), refname='found_count')
    rank = widgets.LabelWidget(_('Rank'), refname='rank')

    class Meta:
        use_keyboard = True
        global_profile = True
        permanent = ('pid', 'cach_name', 'author', 'created',
                     'recommend_count', 'found_count', 'rank', 'grade')
        search = ('cach__name', 'geocacher__nickname', 'cach__code')
        filter_form = RankingFilter

    def render_rank(self, table, row_index, row, value):
        return '%.0f' % value if value else ''

    def render_grade(self, table, row_index, row, value):
        return '%.2f' % value if value else None

    def render_created(self, table, row_index, row, value):
        return value.strftime("%d.%m.%Y") if value else ''


class RankByFoundList(RankByList):
    found_count = widgets.LabelWidget(_('Found'), refname='found_count')
    points = widgets.LabelWidget(_('Points'), refname='points')

    class Meta:
        use_keyboard = True
        global_profile = True
        permanent = ('pid', 'cach_name', 'author', 'created',
                     'recommend_count', 'found_count', 'grade', 'points')
        search = ('cach__name', 'geocacher__nickname', 'cach__code')
        filter_form = RankingFilter

    def render_created(self, table, row_index, row, value):
        return value.strftime("%d.%m.%Y") if value else ''

    def render_points(self, table, row_index, row, value):
        return round(value, 1) if value else 0


class RankByRecommendedList(RankByList):

    class Meta:
        use_keyboard = True
        global_profile = True
        permanent = ('pid', 'cach_name', 'author', 'created',
                     'recommend_count', 'grade')
        search = ('cach__name', 'geocacher__nickname', 'cach__code')
        filter_form = RankingFilter

    def render_grade(self, table, row_index, row, value):
        return '%.2f' % (value or 0)

    def render_created(self, table, row_index, row, value):
        return value.strftime("%d.%m.%Y") if value else ''


class GeocacherRateList(table.TableView):
    nickname = widgets.HrefWidget(_('Nickname'),
                                  refname='geocacher__nickname',
                                  reverse='geocaching-su-geocacher-view',
                                  reverse_column='geocacher__pid')
    country = widgets.LabelWidget(_('Country'), refname='country')
    region = widgets.LabelWidget(_('Region'), refname='region')
    registered = widgets.LabelWidget(_('Registered'),
                                     refname='geocacher__register_date')
    created_count = widgets.LabelWidget(_('Created by'), refname='created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='found_count')
    av_grade = widgets.LabelWidget(_('Average grade'), refname='av_grade')
    av_his_cach_grade = widgets.LabelWidget(_('Av. grade of his caches'),
                                            refname='av_his_cach_grade')

    class Meta:
        use_keyboard = True
        global_profile = True
        permanent = ('nickname', 'country', 'region', 'registered',
                     'created_count', 'found_count', 'av_grade',
                     'av_his_cach_grade')
        search = ('geocacher__nickname',)
        sortable = ('created_count', 'found_count')
        filter_form = RateFilter

    def apply_filter(self, filter, qs):
        self._filter = {}
        for k, v in filter.iteritems():
            self._filter[k] = v

        country = filter.get('country', '')
        if country and country != "ALL":
            qs.filter(geocacher__country_iso3=country)

        subject = filter.get('subject','')
        if subject and subject != 'ALL':
            if subject == '777':
                qs.filter(geocacher__country_iso3=country,
                          geocacher__admin_code__isnull=True)
            else:
                qs.filter(geocacher__country_iso3=country,
                          geocacher__admin_code=subject)

    def filtered(self):
        r = False
        if '_filter' in self:
            r = self._filter is not None
        return r

    def render_av_grade(self, table, row_index, row, value):
        return '%.1f' % (value or 0)

    def render_av_his_cach_grade(self, table, row_index, row, value):
        return '%.1f' % (value or 0)

    def render_registered(self, table, row_index, row, value):
        return value.strftime("%Y") if value else ''

    def render_country(self, table, row_index, row, value):
        return _(value) if value else ''

    def render_region(self, table, row_index, row, value):
        return _(value) if value else ''


class GeocacherRankListBase(table.TableView):
    nickname = widgets.HrefWidget(_('Nickname'),
                                  refname='geocacher__nickname',
                                  reverse='geocaching-su-geocacher-view',
                                  reverse_column='geocacher__pid')
    country = widgets.LabelWidget(_('Country'), refname='country')
    region = widgets.LabelWidget(_('Region'), refname='region')
    registered = widgets.LabelWidget(_('Registered'),
                                     refname='geocacher__register_date')
    created_count = None
    found_count = None

    class Meta:
        use_keyboard = True
        global_profile = True
        permanent = ('nickname', 'country', 'region', 'registered',
                     'created_count', 'found_count')
        search = ('geocacher__nickname',)
        sortable = ('created_count', 'found_count')
        filter_form = RateFilter

    def apply_filter(self, filter, qs):
        self._filter = None

        country = filter.get('country')
        if country and country != 'ALL':
            qs.filter(geocacher__country_iso3=country)
            self._filter = filter

        subject = filter.get('subject', '')
        if subject and subject != 'ALL':
            if subject == '777':
                qs.filter(geocacher__country_iso3=country,
                          geocacher__admin_code__isnull=True)
            else:
                qs.filter(geocacher__country_iso3=country,
                          geocacher__admin_code=subject)
            self._filter = filter

    def filtered(self):
        r = False
        if '_filter' in self:
            r = self._filter is not None
        return r

    def render_registered(self, table, row_index, row, value):
        return value.strftime("%Y") if value else ''

    def render_country(self, table, row_index, row, value):
        return _(value) if value else ''

    def render_region(self, table, row_index, row, value):
        return _(value) if value else ''


class GeocacherVirtRankList(GeocacherRankListBase):
    created_count = widgets.LabelWidget(_('Created by'),
                                        refname='vi_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='vi_found_count')


class GeocacherTradRankList(GeocacherRankListBase):
    created_count = widgets.LabelWidget(_('Created by'),
                                        refname='tr_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='tr_found_count')


class GeocacherCurrYearRateList(GeocacherRankListBase):
    created_count = widgets.LabelWidget(_('Created by'),
                                        refname='curr_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='curr_found_count')


class GeocacherCurrYearVirtRankList(GeocacherRankListBase):
    created_count = widgets.LabelWidget(_('Created by'),
                                        refname='vi_curr_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='vi_curr_found_count')


class GeocacherCurrYearTradRankList(GeocacherRankListBase):
    created_count = widgets.LabelWidget(_('Created by'),
                                        refname='tr_curr_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='tr_curr_found_count')


class GeocacherLastYearRateList(GeocacherRankListBase):
    created_count = widgets.LabelWidget(_('Created by'),
                                        refname='last_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='last_found_count')


class GeocacherLastYearVirtRankList(GeocacherRankListBase):
    created_count = widgets.LabelWidget(_('Created by'),
                                        refname='vi_last_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='vi_last_found_count')


class GeocacherLastYearTradRankList(GeocacherRankListBase):
    created_count = widgets.LabelWidget(_('Created by'),
                                        refname='tr_last_created_count')
    found_count = widgets.LabelWidget(_('Found'),
                                      refname='tr_last_found_count')


class GeocacherSearchRankListBase(table.TableView):
    nickname = widgets.HrefWidget(_('Nickname'),
                                  refname='geocacher__nickname',
                                  reverse='geocaching-su-geocacher-view',
                                  reverse_column='geocacher__pid')
    country = widgets.LabelWidget(_('Country'), refname='country')
    region = widgets.LabelWidget(_('Region'), refname='region')
    points = widgets.LabelWidget(_('Points'), refname='points')

    class Meta:
        use_keyboard = True
        global_profile = True
        permanent = ('nickname', 'country', 'region', 'points')
        search = ('geocacher__nickname',)
        filter_form = RateFilter

    def apply_filter(self, filter, qs):
        self._filter = None

        country = filter.get('country')
        if country and country != 'ALL':
            qs.filter(geocacher__country_iso3=country)
            self._filter = filter

        subject = filter.get('subject', '')
        if subject and subject != 'ALL':
            if subject == '777':
                qs.filter(geocacher__country_iso3=country,
                          geocacher__admin_code__isnull=True)
            else:
                qs.filter(geocacher__country_iso3=country,
                          geocacher__admin_code=subject)
            self._filter = filter

    def filtered(self):
        r = False
        if '_filter' in self:
            r = self._filter is not None
        return r

    def render_country(self, table, row_index, row, value):
        return _(value) if value else ''

    def render_region(self, table, row_index, row, value):
        return _(value) if value else ''


class GeocacherSearchRankListYear(table.TableView):
    nickname = widgets.HrefWidget(_('Nickname'),
                                  refname='geocacher__nickname',
                                  reverse='geocaching-su-geocacher-view',
                                  reverse_column='geocacher__pid')
    country = widgets.LabelWidget(_('Country'), refname='country')
    region = widgets.LabelWidget(_('Region'), refname='region')
    points = widgets.LabelWidget(_('Points'), refname='year_points')

    class Meta:
        use_keyboard = True
        global_profile = True
        permanent = ('nickname', 'country', 'region', 'points')
        search = ('geocacher__nickname',)
        filter_form = RateFilter

    def apply_filter(self, filter, qs):
        self._filter = None

        country = filter.get('country')
        if country and country != 'ALL':
            qs.filter(geocacher__country_iso3=country)
            self._filter = filter

        subject = filter.get('subject', '')
        if subject and subject != 'ALL':
            if subject == '777':
                qs.filter(geocacher__country_iso3=country,
                          geocacher__admin_code__isnull=True)
            else:
                qs.filter(geocacher__country_iso3=country,
                          geocacher__admin_code=subject)
            self._filter = filter

    def filtered(self):
        r = False
        if '_filter' in self:
            r = self._filter is not None
        return r

    def render_country(self, table, row_index, row, value):
        return _(value) if value else ''

    def render_region(self, table, row_index, row, value):
        return _(value) if value else ''


def get_base_count(request):
    page = int(request.GET.get('page') or 0)
    if page:
        return (page - 1) * settings.ROW_PER_PAGE
    return 0


class CacheTable(tables.Table):
    counter = tables.Column(verbose_name="#", empty_values=(), orderable=False)
    pid = tables.Column(accessor='cach_pid')
    cache = tables.Column(accessor='cach__name')
    created = tables.Column(accessor='cach__created_date')
    geocacher = tables.Column(accessor='geocacher__nickname')
    grade = tables.Column(accessor='cach__grade')

    class Meta:
        attrs = {'class': 'table'}

    def render_created(self, value):
        return value.strftime('%Y-%m-%d')

    def render_counter(self):
        self.row_counter = getattr(
            self, 'row_counter', itertools.count(self.page.start_index()))
        return next(self.row_counter)

    def render_grade(self, value):
        return '{0:.1f}'.format(value)

    def render_pid(self, value):
        return format_html(
            '<a href="{}">{}</a>',
            'https://geocaching.su/?pn=101&cid={}'.format(value), value)


class CacheRecommendsTable(CacheTable):
    recommend_count = tables.Column()


class CacheFoundTable(CacheTable):
    found_count = tables.Column()


class CacheIndexTable(CacheTable):
    found_count = tables.Column()
    recommend_count = tables.Column()
    rank = tables.Column()

    def render_rank(self, value):
        return '{0:.1f}'.format(value)


@it_isnt_updating
def cach_rate_by_recommend(request):
    order_by = '-recommend_count'
    qs = CachStat.objects.all().order_by(order_by)

    table = CacheRecommendsTable(qs)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(table)
    return render(
        request,
        'Geocaching_su/dt2-cach_rank_by_recommend.html',
        {'table': table})


@it_isnt_updating
def cach_rate_by_found(request):
    order_by = '-found_count'
    qs = CachStat.objects.all().order_by(order_by)

    table = CacheFoundTable(qs)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(table)
    return render(
        request,
        'Geocaching_su/dt2-cach_rank_by_found.html',
        {'table': table})


@it_isnt_updating
def cach_rate_by_index(request):
    order_by = '-rank'
    qs = CachStat.objects.all().order_by(order_by)

    table = CacheIndexTable(qs)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(table)
    return render(
        request,
        'Geocaching_su/dt2-cache_rank_by_index.html',
        {'table': table})


@it_isnt_updating
def activity_table(request, qs, TableClass, title, table_slug, additional_meta=True):
    source = datasource.QSDataSource(qs)

    table = TableClass(table_slug)
    if additional_meta:
        table.use_keyboard = True
        table.global_profile = True
        table.permanent = ('nickname', 'country', 'region', 'registered',
                           'created_count', 'found_count')
        table.search = ('geocacher__nickname',)
        table.sortable = ('created_count', 'found_count')
        table.filter_form = RateFilter

    cnt = get_controller(table, source, request, settings.ROW_PER_PAGE)

    rc = cnt.process_request()
    if rc:
        return rc

    return render(
        request,
        'Geocaching_su/geocacher_list.html',
        {'table': cnt,
         'title': title,
         'curr_year': datetime.now().year,
         'last_year': datetime.now().year - 1})


class GeocacherTable(tables.Table):
    counter = tables.Column(verbose_name="#", empty_values=(), orderable=False)
    nickname = tables.Column(accessor='geocacher__nickname')
    country = tables.Column(accessor='country')
    region = tables.Column(accessor='region')
    registered = tables.Column(accessor='geocacher__register_date')

    def render_registered(self, value):
        return value.strftime('%Y')

    def render_counter(self):
        self.row_counter = getattr(
            self, 'row_counter', itertools.count(self.page.start_index()))
        return next(self.row_counter)

    def render_country(self, value):
        return _(value) if value else ''

    def render_region(self, value):
        return _(value) if value else ''

    def render_nickname(self, value):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('gcsu-profile', args=[value]), value)

    class Meta:
        template_name = "django_tables2/bootstrap.html"


class GeocacherRateTable(GeocacherTable):
    found_count = tables.Column()
    created_count = tables.Column()
    av_grade = tables.Column(verbose_name='Average grade')
    av_his_cach_grade = tables.Column(
        verbose_name='Av. grade of his caches')

    def render_av_grade(self, value):
        return '%.1f' % (value or 0)

    def render_av_his_cach_grade(self, value):
        return '%.1f' % (value or 0)


class GeocacherRateCurrYearTable(GeocacherTable):
    curr_found_count = tables.Column(verbose_name='Found')
    curr_created_count = tables.Column(verbose_name='Created')


class GeocacherRateLastYearTable(GeocacherTable):
    last_found_count = tables.Column(verbose_name='Found')
    last_created_count = tables.Column(verbose_name='Created')


class GeocacherRateUnrealTable(GeocacherTable):
    vi_found_count = tables.Column(verbose_name='Found')
    vi_created_count = tables.Column(verbose_name='Created')


class GeocacherRateUnrealCurrYearTable(GeocacherTable):
    vi_curr_found_count = tables.Column(verbose_name='Found')
    vi_curr_created_count = tables.Column(verbose_name='Created')


class GeocacherRateUnrealLastYearTable(GeocacherTable):
    vi_last_found_count = tables.Column(verbose_name='Found')
    vi_last_created_count = tables.Column(verbose_name='Created')


class GeocacherRateRealTable(GeocacherTable):
    tr_found_count = tables.Column(verbose_name='Found')
    tr_created_count = tables.Column(verbose_name='Created')


class GeocacherRateRealCurrYearTable(GeocacherTable):
    tr_curr_found_count = tables.Column(verbose_name='Found')
    tr_curr_created_count = tables.Column(verbose_name='Created')


class GeocacherRateRealLastYearTable(GeocacherTable):
    tr_last_found_count = tables.Column(verbose_name='Found')
    tr_last_created_count = tables.Column(verbose_name='Created')


class GeocacherSearchTable(tables.Table):
    counter = tables.Column(verbose_name="#", empty_values=(), orderable=False)
    nickname = tables.Column(accessor='geocacher__nickname')
    country = tables.Column(accessor='country')
    region = tables.Column(accessor='region')
    registered = tables.Column(accessor='geocacher__register_date')
    points = tables.Column(accessor='points')

    def render_registered(self, value):
        return value.strftime('%Y')

    def render_counter(self):
        self.row_counter = getattr(
            self, 'row_counter', itertools.count(self.page.start_index()))
        return next(self.row_counter)

    def render_country(self, value):
        return _(value) if value else ''

    def render_region(self, value):
        return _(value) if value else ''

    class Meta:
        template_name = "django_tables2/bootstrap.html"


class GeocacherSearchYearTable(GeocacherSearchTable):
    points = tables.Column(verbose_name='Points', accessor='year_points')


@it_isnt_updating
def geocacher_rate(request):
    qs = GeocacherStat.objects.all().order_by('-created_count', '-found_count')

    table = GeocacherRateTable(qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {'table': table,
        'title': _("All caches"),
        'curr_year': datetime.now().year,
        'last_year': datetime.now().year - 1})


#@it_isnt_updating
#def geocacher_rate_unreal(request):
    #qs = GeocacherStat.objects.all().order_by('-vi_created_count', '-vi_found_count')

    #return activity_table(
        #request, qs,
        #GeocacherVirtRankList,
        #_("Unreal caches"),
        #'cach_search')

@it_isnt_updating
def geocacher_rate_unreal(request):
    qs = GeocacherStat.objects.all().order_by(
        '-vi_created_count', '-vi_found_count')
    title = _("Unreal caches")

    table = GeocacherRateUnrealTable(qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(table)

    return render(request,
                  'Geocaching_su/dt2-geocacher_list.html',
                  {'table': table,
                   'title': title,
                   'curr_year': datetime.now().year,
                   'last_year': datetime.now().year - 1
                   })


#@it_isnt_updating
#def geocacher_rate_real(request):
    #qs = GeocacherStat.objects.all().order_by('-tr_created_count', '-tr_found_count')

    #return activity_table(request, qs,
                          #GeocacherTradRankList,
                          #_("Real caches"),
                          #'cach_search')

@it_isnt_updating
def geocacher_rate_real(request):
    qs = GeocacherStat.objects.all().order_by(
        '-tr_created_count', '-tr_found_count')
    title = _("Real caches")

    table = GeocacherRateRealTable(qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(table)

    return render(request,
                  'Geocaching_su/dt2-geocacher_list.html',
                  {'table': table,
                   'title': title,
                   'curr_year': datetime.now().year,
                   'last_year': datetime.now().year - 1
                   })


#@it_isnt_updating
#def geocacher_rate_current(request):
    #qs = GeocacherStat.objects.all().order_by('-curr_created_count', '-curr_found_count')
    #title = _("%s. All caches") % datetime.now().year
    #return activity_table(request, qs,
                          #GeocacherCurrYearRateList,
                          #title,
                          #'cach_search')


@it_isnt_updating
def geocacher_rate_current(request):
    qs = GeocacherStat.objects.all().order_by(
        '-curr_created_count', '-curr_found_count')
    title = _("%s. All caches") % datetime.now().year

    table = GeocacherRateCurrYearTable(qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(table)

    return render(request,
                  'Geocaching_su/dt2-geocacher_list.html',
                  {'table': table,
                   'title': title,
                   'curr_year': datetime.now().year,
                   'last_year': datetime.now().year - 1
                   })


@it_isnt_updating
def geocacher_rate_last(request):
    qs = GeocacherStat.objects.all().order_by(
        '-last_created_count', '-last_found_count')
    title = _("%s. All caches") % (datetime.now().year - 1)

    table = GeocacherRateLastYearTable(qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(table)

    return render(request,
                  'Geocaching_su/dt2-geocacher_list.html',
                  {'table': table,
                   'title': title,
                   'curr_year': datetime.now().year,
                   'last_year': datetime.now().year - 1
                   })


#@it_isnt_updating
#def geocacher_rate_unreal_current(request):
    #qs = GeocacherStat.objects.all().order_by('-vi_curr_created_count', '-vi_curr_found_count')
    #title = _("%s. Unreal caches") % datetime.now().year
    #return activity_table(request, qs,
                          #GeocacherCurrYearVirtRankList,
                          #title,
                          #'cach_search')


@it_isnt_updating
def geocacher_rate_unreal_current(request):
    qs = GeocacherStat.objects.all().order_by(
        '-vi_curr_created_count', '-vi_curr_found_count')
    title = _("%s. Unreal caches") % datetime.now().year

    table = GeocacherRateUnrealCurrYearTable(qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(table)

    return render(request,
                  'Geocaching_su/dt2-geocacher_list.html',
                  {'table': table,
                   'title': title,
                   'curr_year': datetime.now().year,
                   'last_year': datetime.now().year - 1
                   })


#@it_isnt_updating
#def geocacher_rate_real_current(request):
    #qs = GeocacherStat.objects.all().order_by('-tr_curr_created_count', '-tr_curr_found_count')
    #title = _("%s. Real caches") % datetime.now().year
    #return activity_table(request, qs,
                          #GeocacherCurrYearTradRankList,
                          #title,
                          #'cach_search')

@it_isnt_updating
def geocacher_rate_real_current(request):
    qs = GeocacherStat.objects.all().order_by(
        '-tr_curr_created_count', '-tr_curr_found_count')
    title = _("%s. Real caches") % datetime.now().year

    table = GeocacherRateRealCurrYearTable(qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(table)

    return render(request,
                  'Geocaching_su/dt2-geocacher_list.html',
                  {'table': table,
                   'title': title,
                   'curr_year': datetime.now().year,
                   'last_year': datetime.now().year - 1
                   })


#@it_isnt_updating
#def geocacher_rate_last(request):
    #qs = GeocacherStat.objects.all().order_by('-last_created_count', '-last_found_count')
    #title = _("%s. All caches") % (datetime.now().year-1)
    #return activity_table(request, qs,
                          #GeocacherLastYearRateList,
                          #title,
                          #'cach_search')


#@it_isnt_updating
#def geocacher_rate_unreal_last(request):
    #qs = GeocacherStat.objects.all().order_by('-vi_last_created_count', '-vi_last_found_count')
    #title =  _("%s. Unreal caches") % (datetime.now().year-1)
    #return activity_table(request, qs,
                          #GeocacherLastYearVirtRankList,
                          #title,

@it_isnt_updating
def geocacher_rate_unreal_last(request):
    qs = GeocacherStat.objects.all().order_by(
        '-vi_last_created_count', '-vi_last_found_count')
    title = _("%s. Unreal caches") % (datetime.now().year - 1)

    table = GeocacherRateUnrealLastYearTable(qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(table)

    return render(request,
                  'Geocaching_su/dt2-geocacher_list.html',
                  {'table': table,
                   'title': title,
                   'curr_year': datetime.now().year,
                   'last_year': datetime.now().year - 1
                   })


#@it_isnt_updating
#def geocacher_rate_real_last(request):
    #qs = GeocacherStat.objects.all().order_by('-tr_last_created_count', '-tr_last_found_count')
    #title =  _("%s. Real caches") % (datetime.now().year-1)
    #return activity_table(request, qs,
                          #GeocacherLastYearTradRankList,
                          #title,
                          #'cach_search')

@it_isnt_updating
def geocacher_rate_real_last(request):
    qs = GeocacherStat.objects.all().order_by(
        '-tr_last_created_count', '-tr_last_found_count')
    title = _("%s. Real caches") % (datetime.now().year - 1)

    table = GeocacherRateRealLastYearTable(qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(table)

    return render(request,
                  'Geocaching_su/dt2-geocacher_list.html',
                  {'table': table,
                   'title': title,
                   'curr_year': datetime.now().year,
                   'last_year': datetime.now().year - 1
                   })


@it_isnt_updating
def cach_view(request, cach_pid):
    url = geocaching_su_cach_url(cach_pid)
    return HttpResponseRedirect(url)


@it_isnt_updating
def geocacher_view(request, geocacher_uid):
    url = geocaching_su_geocacher_url(geocacher_uid)
    return HttpResponseRedirect(url)


@it_isnt_updating
def geocaching_su(request):
    sql = """
    SELECT c.iso,
    POW((SELECT COUNT(gc.id) FROM geocacher gc WHERE gc.country_iso3=c.iso3),1) as geocachers,
    POW((SELECT COUNT(cach.id) FROM cach WHERE cach.country_code=c.iso),1) as caches
    FROM geo_country as c
    HAVING geocachers + caches > 0
    """
    countries = []
    for item in iter_sql(sql):
        geocachers = item[1]
        caches = item[2]
        countries.append({'iso': item[0],
                          'geocachers': geocachers,
                          'caches': caches})

    update_date = LogUpdate.objects.filter(update_type='gcsu_logs')
    update_date = update_date.aggregate(last_date=Max('update_date'))
    return render(
        request,
        'Geocaching_su/geocaching_su_index.html',
        {'countries': countries,
        'update_date': update_date.get("last_date"),
         })


def find_item_by_year(items, year):
    r = None
    for item in items:
        if item.get('year') == year:
            return item
    return r


@it_isnt_updating
def geocaching_su_cach_stat(request):
    cach_count = Cach.objects.all().count()

    sql = """
    SELECT type_code, COUNT(*)
    FROM cach
    GROUP BY type_code
    """
    cach_table = []

    for item in iter_sql(sql):
        cach_table.append({'type': item[0],
                           'description': GEOCACHING_SU_CACH_TYPES.get(item[0], ''),
                           'count': item[1],
                           'percent': float(item[1]) / cach_count*100})

    return render(
        request,
        'Geocaching_su/cache_stat.html',
        {
            'cach_count': cach_count,
            'cach_table': cach_table,
            'cache_per_year': created_caches_per_year()
        })


@it_isnt_updating
def geocaching_su_cache_statistics(request):
    return HttpResponseRedirect(reverse('geocaching-su-cach-stat'))


@it_isnt_updating
def geocaching_su_geocacher_stat_countries(request):
    geocacher_count = Geocacher.objects.all().count()
    active_count = Geocacher.objects.all().filter(found_caches__gt=0).count()

    sql = """
    SELECT gc.name, COUNT(*) as cnt
    FROM geocacher g
    LEFT JOIN geo_country gc ON g.country_iso3=gc.iso3
    GROUP BY gc.name
    ORDER BY cnt desc
    """
    geocacher_table = []

    for item in iter_sql(sql):
        country = item[0] if item[0] else _("Undefined")
        geocacher_table.append({'country': country,
                                'count': item[1],
                                'percent': float(item[1]) / geocacher_count*100})

    sql = """
    SELECT gc.name, COUNT(*) as cnt
    FROM geocacher g
    LEFT JOIN geo_country gc ON g.country_iso3=gc.iso3
    WHERE IFNULL(g.found_caches,0) > 0
    GROUP BY gc.name
    ORDER BY cnt desc
    """
    active_table = []

    for item in iter_sql(sql):
        country = item[0] if item[0] else _("Undefined")
        active_table.append({'country': country,
                             'count': item[1],
                             'percent': float(item[1]) / active_count*100})

    return render(
        request,
        'Geocaching_su/geocacher_stat_countries.html',
        {'geocacher_count': geocacher_count,
        'active_count': active_count,
        'geocacher_table': geocacher_table,
        'active_table': active_table})


@it_isnt_updating
def geocaching_su_geocacher_stat(request):
    return HttpResponseRedirect(reverse('geocacher-activity'))


def activity_per_month(last_years=None):
    return activity_per_month(last_years)


def activity_creating_per_month(last_years=None):
    return activity_per_month(last_years, creation=True)


def caches_per_year():
    def row_by_year(data, year):
        if not data or not year:
            return None

        for item in data:
            if item.get('year') == year:
                return item
        return None

    curr_year = datetime.now().year

    sql = """
    SELECT YEAR(MIN(created_date))
    FROM cach
    WHERE type_code in ('EV', 'VI', 'CT', 'MV', 'LV')"""
    year_ = sql2val(sql)

    sql = """
    SELECT YEAR(MIN(created_date))
    FROM cach
    WHERE type_code in ('TR', 'MS', 'LT')"""
    year2 = sql2val(sql)
    if year2 < year_:
        year_ = year2


    data_table = []
    for y in range(curr_year-year_+1):
                data_table.append({'year': y + year_, 'real': 0, 'unreal': 0})

    sql = """
    SELECT YEAR(created_date), COUNT(*) as cnt
    FROM cach
    WHERE created_date IS NOT NULL AND
          type_code in ('TR', 'MS', 'LT')
    GROUP BY YEAR(created_date)
    """

    for item in iter_sql(sql):
        row = row_by_year(data_table, item[0])
        if row:
            row['real'] = item[1]

    sql = """
    SELECT YEAR(created_date), COUNT(*) as cnt
    FROM cach
    WHERE created_date IS NOT NULL AND
          type_code in ('EV', 'VI', 'CT', 'MV', 'LV')
    GROUP BY YEAR(created_date)
    """
    for item in iter_sql(sql):
        row = row_by_year(data_table, item[0])
        if row:
            row['unreal'] = item[1]

    return data_table


@it_isnt_updating
def geocacher_activity(request):
    all_found = LogSeekCach.objects.all().count()
    all_created = LogCreateCach.objects.all().count()

    data_table = activity_per_month()
    data_table.reverse()

    return render(
        request,
        'Geocaching_su/geocacher_activity.html',
        {'data_table': data_table,
        'all_found': all_found,
        'all_created': all_created})


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_cach_stat_pie(request):
    sql = """
    SELECT type_code, COUNT(*) as cnt
    FROM cach
    GROUP BY type_code
    ORDER BY type_code
    """
    chart = get_piechart(sql, 600, 400)

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@geocacher_su
def geocaching_su_personal_found_cache_pie(request, geocacher_uid):
    chart = get_personal_caches_bar(
        request, geocacher_uid,
        RAWSQL['geocacher_found_caches_by_type'])

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@geocacher_su
def geocaching_su_personal_created_cache_pie(request, geocacher_uid):
    chart = get_personal_caches_bar(
        request, geocacher_uid, RAWSQL['geocacher_created_caches_by_type'])

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@geocacher_su
def gcsu_personal_found_current_chart(request):
    nickname = get_nickname(request)
    geocacher = get_object_or_404(Geocacher, nickname=nickname)
    year_ = date.today().year - 1

    sql = """
    SELECT MONTH(found_date) as month_, COUNT(l.id) as cnt
    FROM log_seek_cach as l
    WHERE l.cacher_uid=%s AND YEAR(l.found_date)=%s
    GROUP BY MONTH(found_date)
    """ % (geocacher.uid, year_)

    months = {}
    for item in iter_sql(sql):
        months[item[0]] = item[1]
    data = []
    legend = []
    for m in range(12):
        data.append(months.get(m + 1) or 0)
        legend.append(str(m + 1))

    width = 400
    height = 160

    chart = StackedHorizontalBarChart(width, height,
                                      x_range=(1, 12))
    chart.set_bar_width(10)
    chart.set_colours(['00ff00', 'ff0000'])
    chart.add_data(data)

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_cach_pertype_stat_chart(request):
    data_table = caches_per_year()

    data_real = []
    data_unreal = []
    legend = []

    dmax = 0
    for row in data_table:
        data_real.append(row['real'])
        data_unreal.append(row['unreal'])
        legend.append(row['year'])

        if dmax < row['real']:
            dmax = row['real']
        if dmax < row['unreal']:
            dmax = row['unreal']

    chart = create_chart(
        100, 200, 200, data_real, data_unreal, legend, None, dmax, name1=_('real'), name2=_('virtual'))

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_cache_per_type_chart(request):
    color1 = '#f89d53'
    color2= '#c56a20'
    linecolor1= '#987'
    linecolor2= '#876'

    chart= QuickChart()
    chart.width = 700
    chart.height = 250
    chart.device_pixel_ratio= 2.0

    datasets = []
    labels = []
    cache_per_year = created_caches_per_year()

    for row in cache_per_year:
        labels.append(row['year'])

    types = [
        {
            'code': 'VI',
            'color': '#f89d53'},
        {
            'code': 'MV',
            'color': '#e78c42'},
        {
            'code': 'MS',
            'color': '#81ea6f'},
        {
            'code': 'TR',
            'color': '#9dd872'},
        {
            'code': 'LT',
            'color': '#3c9fff'},
        {
            'code': 'LV',
            'color': '#5ebfff'},
        {
            'code': 'CT',
            'color': '#999'},
        {
            'code': 'EV',
            'color': '#555'}
    ]

    for type_code in types:
        code = type_code['code']
        dataset = {
            'borderColor': type_code['color'],
            'backgroundColor': type_code['color'],
            'pointRadius': 0,
            'label': code,
            'fill': 'false',
            'data': []
        }
        for row in cache_per_year:
            dataset['data'].append(row['types'][code])
        datasets.append(dataset)


    chart.config = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': datasets,
        },
        'options': {
            'plugins': {
            }
        }
    }
    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_cach_stat_chart(request):
    sql = """
    SELECT YEAR(created_date) as year_, COUNT(*)
    FROM cach
    WHERE  YEAR(created_date) <= YEAR(NOW())
    GROUP BY year_;
    """
    data, labels, summ = get_chart_data(sql)

    # Set the vertical range from 0 to 50
    # max_ = int(summ / 1000.0) + 1
    # max_y = max_ * 1000
    width = 600
    height = 250

    chart = QuickChart()
    chart.width = width
    chart.height = height

    chart.config = """
    {
        type: 'line',
        data: {
            labels: %(labels)s,
            datasets: [{
                data: %(data)s,
                fill: true,
                borderColor: '#f89d53',
                backgroundColor: '#fabf75'}],
        },
        options: {
            legend: false
        }
    }
    """ % {
        'labels': labels,
        'data': data
    }

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_geocacher_activity_chart(request):
    data_table = activity_per_month(last_years=6)

    dataf = []
    datac = []
    legend = []
    legend_y = []
    dmax = 0
    for row in data_table:
        datac.append(row['created'])
        dataf.append(row['found'])
        legend.append(row['month'])
        if not len(legend_y) or (legend_y[-1] != row['year']):
            legend_y.append(row['year'])
        if dmax < row['created']:
            dmax = row['created']
        if dmax < row['found']:
            dmax = row['found']

    chart = create_chart(
        1000, 1000, 1000, dataf, datac, legend, legend_y, dmax,
        name1=_('found'), name2=_('created')
    )

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_geocacher_activity_creating_chart(request):
    data_table = activity_creating_per_month(last_years=6)

    dataf = []
    datac = []
    legend = []
    legend_y = []
    dmax = 0
    for row in data_table:
        datac.append(row['virt'])
        dataf.append(row['trad'])
        legend.append(row['month'])
        if not len(legend_y) or (legend_y[-1] != row['year']):
            legend_y.append(row['year'])
        if dmax < row['trad']:
            dmax = row['trad']
        if dmax < row['virt']:
            dmax = row['virt']

    chart = create_chart(
        100, 100, 100, dataf, datac, legend, legend_y, dmax,
        name1=_('traditional'), name2=_('virtual')
    )

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_geocacher_stat_chart(request):
    width = 600
    height = 300
    labels = []

    #sql = """
    #SELECT YEAR(register_date) as year_, COUNT(*)
    #FROM geocacher
    #WHERE  YEAR(register_date) <= YEAR(NOW())
    #GROUP BY year_
    #"""
    #data = []

    #summ = 0
    # for item in iter_sql(sql):
        #summ += item[1]
        # data.append(summ)
        # labels.append(item[0])

    data = []
    sql = """
    SELECT YEAR(register_date) as year_, COUNT(*)
    FROM geocacher
    WHERE YEAR(register_date) <= YEAR(NOW()) AND
          found_caches > 0
    GROUP BY year_
    """
    summ = 0
    for item in iter_sql(sql):
        summ += item[1]
        data.append(summ)
        labels.append(item[0])

    chart = QuickChart()
    chart.width = width
    chart.height = height

    chart.config = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': [{
                'data': data,
                'fill': 'start',
                'borderColor': '#f89d53',
                'backgroundColor': '#fabf75'}],
        },
        'options': {
            'legend': False
        }
    }

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_geocacher_stat_pie(request, only_active=False):
    only_active_filter = ''
    if only_active:
        only_active_filter = 'WHERE g.found_caches > 0 '

    sql = """
    SELECT gc.name, COUNT(*) as cnt
    FROM geocacher g
    LEFT JOIN geo_country gc ON g.country_iso3=gc.iso3
    %s
    GROUP BY gc.name
    HAVING cnt > 99
    """ % only_active_filter
    data = []
    labels = []

    for item in iter_sql(sql):
        country = item[0] if item[0] else "Undefined"
        data.append(item[1])
        labels.append(country)

    sql = """
    SELECT gc.name, COUNT(*) as cnt
    FROM geocacher g
    LEFT JOIN geo_country gc ON g.country_iso3=gc.iso3
    %s
    GROUP BY gc.name
    HAVING cnt < 100
    """ % only_active_filter
    summ = 0
    for item in iter_sql(sql):
        summ += item[1]
    data.append(summ)
    labels.append("Other ( < 100)")

    width = 600
    height = 400

    chart = QuickChart()
    chart.width = width
    chart.height = height
    chart.device_pixel_ratio = 2.0

    chart.config = {
        'type': 'outlabeledPie',
        'data': {
            'labels': labels,
            'datasets': [{
                'backgroundColor': sorted([
                    '#f83c38', '#e61a16', '#1a7ddd', '#3c9fff',
                    '#9dd872', '#d67b31', '#7bb650', '#f89d53']),
                'data': data,
            }]
        },
        'options': {
            'plugins': {
                'legend': False,
                'outlabels': {
                    'text': '%l %p',
                    'color': '#666',
                    'stretch': 35,
                    'font': {
                        'resizable': True,
                        'minSize': 10,
                        'maxSize': 12
                    }
                }
            }
        }
    }

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_chart(request):
    # Set the vertical range from 0 to 50
    max_y = 50
    chart = SimpleLineChart(200, 125, y_range=[0, max_y])

    # First value is the highest Y value. Two of them are needed to be
    # plottable.
    chart.add_data([max_y] * 2)

    # 3 sets of real data
    chart.add_data([28, 30, 31, 33, 35, 36, 42, 48, 43, 37, 32, 24, 28])
    chart.add_data([16, 18, 18, 21, 23, 23, 29, 36, 31, 25, 20, 12, 17])
    chart.add_data([7, 9, 9, 12, 14, 14, 20, 27, 21, 15, 10, 3, 7])

    # Last value is the lowest in the Y axis.
    chart.add_data([0] * 2)

    # Black lines
    chart.set_colours(['000000'] * 5)

    # Filled colours
    # from the top to the first real data
    chart.add_fill_range('76A4FB', 0, 1)

    # Between the 3 data values
    chart.add_fill_range('224499', 1, 2)
    chart.add_fill_range('FF0000', 2, 3)

    # from the last real data to the
    chart.add_fill_range('80C65A', 3, 4)

    # Some axis data
    chart.set_axis_labels(Axis.LEFT, ['', max_y / 2, max_y])
    chart.set_axis_labels(Axis.BOTTOM, ['Sep', 'Oct', 'Nov', 'Dec'])

    chart.download('line-fill.png')

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@accept_ajax
def cache_info(request):
    rc = {'status': 'ERR',
          }
    pid = request.GET.get('cache_pid')
    cache = get_object_or_none(Cach, pid=pid)
    if not cache:
        return rc
    rc['content'] = render_to_string('Geocaching_su/cache_info.html',
                                     RequestContext(request,
                                                    {'cache': cache,
                                                     }))
    rc['status'] = 'OK'

    return rc


@it_isnt_updating
@accept_ajax
def change_country(request):
    rc = {'status': 'ERR',
          }
    country_code = request.GET.get('country')
    request.session['country'] = country_code
    request.session['region'] = []
    if not country_code:
        return rc
    country = get_object_or_none(GeoCountry, iso=country_code)
    address = 'Ukraine, Kharkov'
    if country:
        address = '%s,%s' % (country.name, country.capital)
    regions = GeoCountryAdminSubject.objects.filter(country_iso=country_code)
    regions = regions.values('code', 'name').order_by('name')
    rc['regions'] = list(regions)

    rc['regions'] = [('ALL', _('all')), ] + \
                    sorted(rc['regions'], key=lambda x: x['name'])
    rc['address'] = address
    rc['status'] = 'OK'

    return rc


@it_isnt_updating
@accept_ajax
def filter_change_subjects(request):
    rc = {'status': 'ERR',
          }
    country_code = request.GET.get('country')
    if not country_code:
        return rc
    country = get_object_or_none(GeoCountry, iso3=country_code)
    regions = GeoCountryAdminSubject.objects.filter(country_iso=country.iso)
    regions = regions.values('code', 'name').order_by('name')
    rc['regions'] = list(regions)
    rc['regions'] = sorted(rc['regions'], key=lambda x: x['name'])
    rc['status'] = 'OK'

    return rc


@it_isnt_updating
@accept_ajax
def region_caches(request):
    rc = {'status': 'ERR',
          }
    country_code = request.GET.get('country')
    request.session['country'] = country_code
    region_ids = request.GET.getlist('region')
    request.session['region'] = region_ids
    type_ids = request.GET.getlist('type')
    request.session['type'] = type_ids
    related_ids = request.GET.getlist('related')
    request.session['related'] = related_ids
    if not country_code:
        return rc

    caches = get_caches(
        request, country_code, region_ids, type_ids, related_ids)

    cache_list = []
    lat_min = lat_max = lng_min = lng_max = None
    for cache in caches:
        cache_list.append({'pid': cache.pid,
                           'name': cache.name,
                           'site': cache.site,
                           'type_code': cache.type_code,
                           'latitude_degree': cache.latitude_degree,
                           'longitude_degree': cache.longitude_degree})
        if lat_min is None or cache.latitude_degree < lat_min:
            lat_min = cache.latitude_degree
        if lat_max is None or cache.latitude_degree > lat_max:
            lat_max = cache.latitude_degree
        if lng_min is None or cache.longitude_degree < lng_min:
            lng_min = cache.longitude_degree
        if lng_max is None or cache.longitude_degree > lng_max:
            lng_max = cache.longitude_degree
    rc['caches'] = cache_list
    rc['rect'] = {'lat_min': lat_min or '',
                  'lat_max': lat_max or '',
                  'lng_min': lng_min or '',
                  'lng_max': lng_max or ''
                  }
    rc['status'] = 'OK'

    return rc


@it_isnt_updating
def selected_caches(request):
    country_code = request.session.get('country')
    region_ids = request.session.get('region')
    type_ids = request.session.get('type')
    related_ids = request.session.get('related')
    if not country_code:
        pass

    return get_caches(request, country_code, region_ids, type_ids, related_ids)


@it_isnt_updating
def map_import_caches_wpt(request):
    return  HttpResponse('')
    caches = selected_caches(request)

    response_text = render_to_string('caches.wpt', {'caches': caches})
    response = HttpResponse(response_text)
    response['Content-Type'] = u'text'
    response['Content-Disposition'] = u'attachment; filename = geocaches_%d.wpt' % int(time.time())
    response['Content-Length'] = unicode(len(response_text))

    return response


@it_isnt_updating
def map_import_caches_kml(request):
    return  HttpResponse('')

    def style_by_type(type_):
        if type_ == 'TR':
            return '#tradi'
        if type_ == 'VI':
            return '#virt'
        if type_ == 'MS':
            return '#multi'
        if type_ == 'MV':
            return '#multiv'
        return ''

    caches = selected_caches(request)

    root_tree = etree.Element('kml')
    root_tree.attrib['xmlns'] = "http://earth.google.com/kml/2.0"
    document_tree = etree.SubElement(root_tree, 'Document')

    styles = [
        {'id': 'tradi', 'href': "http://www.geocaching.su/images/ctypes/icons/maps/tr.png"},
        {'id': 'virt', 'href': "http://www.geocaching.su/images/ctypes/icons/maps/vi.png"},
        {'id': 'multi', 'href': "http://www.geocaching.su/images/ctypes/icons/maps/ms.png"},
        {'id': 'multiv', 'href': "http://www.geocaching.su/images/ctypes/icons/maps/mv.png"},
        ]
    for style in styles:
        style_tradi_tree = etree.SubElement(document_tree, 'Style')
        style_tradi_tree.attrib['id'] = style.get('id')
        iconstyle_tradi_tree = etree.SubElement(style_tradi_tree, 'IconStyle')
        icon_tradi_tree = etree.SubElement(iconstyle_tradi_tree, 'Icon')
        iconhref_tradi_tree = etree.SubElement(icon_tradi_tree, 'href')
        iconhref_tradi_tree.text = style.get('href')

    folder_tree = etree.SubElement(document_tree, 'Folder')
    folder_name_tree = etree.SubElement(folder_tree, 'Name')
    folder_name_tree.text = "Geocaches (gps-fun.info)"
    folder_open_tree = etree.SubElement(folder_tree, 'Open')
    folder_open_tree.text = "0"

    for cache in caches:
        placemark_tree = etree.SubElement(folder_tree, 'Placemark')
        desc_tree = etree.SubElement(pl999acemark_tree, 'description')
        desc_tree.text = """
        <a href="%(url)s">Cache %(code)s details</a><br />
        Created by %(author)s<br />&nbsp;<br />
        <table cellspacing="0" cellpadding="0" border="0">
        <tr>
        <td>Type: %(type)s<br />Size: %(size)s</td>
        </tr>
        <tr><td>: Difficulty %(diff)s<br />Terrain: %(terr)s</td></tr>
        </table>
        """ % {'url': cache.url, 'code': cache.code,
                'author': cache.author.nickname,
               'type': cache.cach_type, 'size': cache.size,
               'diff': cache.dostupnost, 'terr': cache.mestnost}
        name_tree = etree.SubElement(placemark_tree, 'name')
        name_tree.text = cache.name
        lookat_tree = etree.SubElement(placemark_tree, 'LookAt')
        long_tree = etree.SubElement(lookat_tree, 'longitude')
        long_tree.text = str(cache.longitude_degree)
        lat_tree = etree.SubElement(lookat_tree, 'latitude')
        lat_tree.text = str(cache.latitude_degree)
        range_tree = etree.SubElement(lookat_tree, 'range')
        range_tree.text = '500'
        tilt_tree = etree.SubElement(lookat_tree, 'tilt')
        tilt_tree.text = '45'
        heading_tree = etree.SubElement(lookat_tree, 'heading')
        heading_tree.text = '0'
        style_tree = etree.SubElement(placemark_tree, 'styleUrl')
        style_tree.text = style_by_type(cache.type_code)
        point_tree = etree.SubElement(placemark_tree, 'Point')
        coord_tree = etree.SubElement(point_tree, 'coordinates')
        coord_tree.text = '%s,%s' % (
            cache.longitude_degree, cache.latitude_degree)

    response_text = '%s%s' % (
        '<?xml version="1.0" encoding="utf-8"?>',
        etree.tostring(root_tree).decode("utf-8"))
    response = HttpResponse(response_text)
    response['Content-Type'] = u'text/xml'
    response['Content-Disposition'] = u'attachment; filename = geocaches_%d.kml' % int(time.time())
    response['Content-Length'] = unicode(len(response_text))

    return response


@it_isnt_updating
@geocacher_su
def geocaching_su_personal_statistics(request):
    if request.method == 'POST':
        if 'ok' in request.POST:
                nickname = request.POST.get('login_as') or ''
                if nickname:
                    request.session['login_as'] = nickname
                else:
                    request.session['login_as'] = None

    nickname = get_nickname(request)
    geocacher = get_object_or_none(Geocacher, nickname=nickname)

    return render(
        request,
        'Geocaching_su/personal_statistics.html',
        {
            'geocacher': geocacher,
            'curr_year': date.today().year,
        })


@it_isnt_updating
@geocacher_su
def gcsu_found_my_caches_stat(request):
    geocacher, geocachers, all_types = get_found_statistics(request)

    return render(
        request,
        'Geocaching_su/found_my_caches.html',
        {
            'geocacher': geocacher,
            'data': geocachers,
            'all_types': all_types,
        })


@it_isnt_updating
@geocacher_su
def gcsu_i_found_caches_stat(request):
    geocacher, geocachers, all_types = get_found_statistics(
                                            request, i_found=True)

    return render(
        request,
        'Geocaching_su/my_found_caches.html',
        {
            'geocacher': geocacher,
            'data': geocachers,
            'all_types': all_types,
        })


@it_isnt_updating
@geocacher_su
def gcsu_regions_found_caches_stat(request):
    nickname = get_nickname(request)
    geocacher = get_object_or_404(Geocacher, nickname=nickname)

    sql = """
        select cs.id, cs.code, cs.name, c.name, c.iso
        from geo_country_subject cs
        left join geo_country c on cs.country_iso=c.iso
        where cs.code is not null and
              cs.code <> '777' and
              cs.country_iso IN
              ('RU', 'UA', 'BY', 'KZ', 'LT',
               'LV', 'EE', 'MD', 'AZ', 'AM',
               'GE', 'UZ', 'KG', 'TM', 'TJ')
        order by c.name, cs.name
        """
    all_regions = []
    for item in iter_sql(sql):
        all_regions.append({'id': item[0],
                            'code': item[1],
                            'name': item[2],
                            'country_name': item[3],
                            'iso': item[4],
                            'count': 0, })

    regions = []
    sql = """
        select c.iso, cs.code, count(l.id) as cnt
        from log_seek_cach l
        left join cach on l.cach_pid = cach.pid
        left join geo_country_subject cs on (cach.admin_code=cs.code and cach.country_code=cs.country_iso)
        left join geo_country c on cach.country_code=c.iso
        where cach.pid is not null and
              l.cacher_uid=%s and
              cs.code is not null and
              cs.code <> '777' and
              cs.country_iso IN
              ('RU', 'UA', 'BY', 'KZ', 'LT',
               'LV', 'EE', 'MD', 'AZ', 'AM',
               'GE', 'UZ', 'KG', 'TM', 'TJ')
        group by c.iso, cs.code
        having cnt > 0
        """ % geocacher.uid
    for item in iter_sql(sql):
        regions.append({'iso': item[0],
                        'code': item[1],
                        'count': item[2],
                        })

    for my_region in regions:
        for region in all_regions:
            if  region['iso'] == my_region['iso'] and region['code'] == my_region['code']:
                region['count'] = my_region['count']

    countries = []
    regions = []
    count = 0
    regions_count = 0
    country = None
    for region in all_regions:
        if region['country_name'] != country:
            if country:
                countries.append({'country': country,
                                  'regions': regions,
                                  'count': count,
                                  'regions_count': regions_count,
                                  'all_regions': len(regions), })
            country = region['country_name']
            regions = []
            count = 0
            regions_count = 0
        regions.append(region)
        count += region['count'] or 0
        regions_count += 1 if region['count'] else 0
    countries.append({'country': country,
                    'regions': regions,
                    'count': count,
                    'regions_count': regions_count,
                    'all_regions': len(regions), })

    return render(
        request,
        'Geocaching_su/region_found_caches.html',
        {
            'geocacher': geocacher,
            'countries': countries,
        })


@it_isnt_updating
@geocacher_su
def geocaching_su_personal_charts(request):
    found_current_year = []
    found_last_year = []
    found_years = []
    created_years = []
    created_current_year = []
    created_last_year = []
    year_ = None
    last_year = None
    current_count = 0
    last_count = 0
    all_count = 0
    current_created_count = 0
    last_created_count = 0
    all_created_count = 0

    nickname = get_nickname(request)
    geocacher = get_object_or_404(Geocacher, nickname=nickname)
    stat = geocacher.statistics()
    cache_table = []
    created_table = []
    if stat:
        # FOUND
        caches_count = stat.found_count or 1
        sql = """
        SELECT cach.type_code, COUNT(l.id) as cnt
        FROM log_seek_cach as l
             LEFT JOIN cach ON l.cach_pid=cach.pid
        WHERE l.cacher_uid=%s AND cach.pid IS NOT NULL
        GROUP BY cach.type_code
        ORDER BY cnt desc
        """ % geocacher.uid

        for item in iter_sql(sql):
            cache_table.append({'type': item[0],
                               'description': GEOCACHING_SU_CACH_TYPES.get(item[0]) or 'undefined',
                               'count': item[1],
                               'percent': float(item[1])/caches_count*100})

        year_ = date.today().year
        last_year = year_ - 1

        current_count = LogSeekCach.objects.filter(cacher_uid=geocacher.uid)
        current_count = current_count.filter(found_date__year=year_).count()

        last_count = LogSeekCach.objects.filter(cacher_uid=geocacher.uid)
        last_count = last_count.filter(found_date__year=last_year).count()

        all_count = LogSeekCach.objects.filter(cacher_uid=geocacher.uid).count()

        found_current_year, found_last_year, first_year = \
            geocacher_year_statistics(
                geocacher, year_, last_year, creation=False)

        sql = """
        SELECT YEAR(found_date) as year_, COUNT(l.id) as cnt
        FROM log_seek_cach as l
        WHERE l.cacher_uid=%s
        GROUP BY YEAR(found_date)
        """ % geocacher.uid

        years = {}
        for item in iter_sql(sql):
            years[item[0]] = item[1]
        found_years = []
        m = first_year
        while m <= year_:
            found_years.append(
                {'count': years.get(m) or 0,
                 'year': m})
            m += 1

        # CREATED
        caches_count = stat.created_count or 1
        sql = """
        SELECT cach.type_code, COUNT(l.id) as cnt
        FROM log_create_cach as l
             LEFT JOIN cach ON l.cach_pid=cach.pid
        WHERE l.author_uid=%s AND cach.pid IS NOT NULL
        GROUP BY cach.type_code
        ORDER BY cnt desc
        """ % geocacher.uid

        for item in iter_sql(sql):
            created_table.append({
                'type': item[0],
                'description': GEOCACHING_SU_CACH_TYPES.get(item[0]) or 'undefined',
                'count': item[1],
                'percent': float(item[1]) / caches_count*100})

        current_created_count = LogCreateCach.objects.filter(
            author_uid=geocacher.uid)
        current_created_count = current_created_count.filter(created_date__year=year_).count()

        last_created_count = LogCreateCach.objects.filter(
            author_uid=geocacher.uid)
        last_created_count = last_created_count.filter(created_date__year=last_year).count()

        all_created_count = LogCreateCach.objects.filter(
            author_uid=geocacher.uid).count()

        created_current_year, created_last_year, first_year = \
            geocacher_year_statistics(
                geocacher, year_, last_year, creation=True)

        sql = """
        SELECT YEAR(created_date) as year_, COUNT(l.id) as cnt
        FROM log_create_cach as l
        WHERE l.author_uid=%s
        GROUP BY YEAR(created_date)
        """ % geocacher.uid

        years = {}
        for item in iter_sql(sql):
            years[item[0]] = item[1]
        created_years = []
        m = first_year or year_
        while m <= year_:
            created_years.append(
                {'count': years.get(m) or 0,
                 'year': m})
            m += 1
    return render(
        request,
        'Geocaching_su/personal_charts.html',
        {
           'geocacher': geocacher,
           'curr_year': date.today().year,
           'cache_table': cache_table,
           'created_table': created_table,
           'found_current_year': found_current_year,
           'found_last_year': found_last_year,
           'found_years': found_years,
           'created_current_year': created_current_year,
           'created_last_year': created_last_year,
           'created_years': created_years,
           'current_year': year_,
           'last_year': last_year,
           'current_count': current_count,
           'last_count': last_count,
           'all_count': all_count,
           'current_created_count': current_created_count,
           'last_created_count': last_created_count,
           'all_created_count': all_created_count,
        })


@it_isnt_updating
def map_import_caches_gpx(request):
    return HttpResponse('')


def coordinate_converter(request):
    return render(
        request,
        'Geocaching_su/coordinate_converter.html',
        {})


#@it_isnt_updating
#def geocacher_search_rating(request):
    #qs = GeocacherSearchStat.objects.all()
    #qs = qs.select_related('geocacher').filter(points__gt=0)
    #qs = qs.order_by('-points')

    #source = datasource.QSDataSource(qs)
    #table = GeocacherSearchRankListBase('geocacher_list')

    #cnt = get_controller(table, source, request, settings.ROW_PER_PAGE)

    #rc = cnt.process_request()
    #if rc:
        #return rc

    #return render(
        #request,
        #'Geocaching_su/geocacher_list.html',
        #{
            #'table': cnt,
            #'title': _("All years"),
            #'curr_year': datetime.now().year,
            #'last_year': datetime.now().year-1
        #})
@it_isnt_updating
def geocacher_rate_real_current(request):
    qs = GeocacherStat.objects.all().order_by(
        '-tr_curr_created_count', '-tr_curr_found_count')
    title = _("%s. Real caches") % datetime.now().year

    table = GeocacherRateRealCurrYearTable(qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(table)

    return render(request,
                  'Geocaching_su/dt2-geocacher_list.html',
                  {'table': table,
                   'title': title,
                   'curr_year': datetime.now().year,
                   'last_year': datetime.now().year - 1
                   })


@it_isnt_updating
def geocacher_search_rating(request):
    qs = GeocacherSearchStat.objects.all()
    qs = qs.select_related('geocacher').filter(points__gt=0)
    qs = qs.order_by('-points')

    table = GeocacherSearchTable(qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {
            'table': table,
            'title': _("Search rating. All years"),
            'curr_year': datetime.now().year,
            'last_year': datetime.now().year - 1
        })


@it_isnt_updating
def geocacher_search_rating_current(request):
    qs = GeocacherSearchStat.objects.all()
    qs = qs.select_related('geocacher').filter(year_points__gt=0)
    qs = qs.order_by('-year_points')

    table = GeocacherSearchYearTable(qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {
            'table': table,
            'title': _("Search rating. Current year %s") % datetime.now().year,
            'curr_year': datetime.now().year,
            'last_year': datetime.now().year - 1
        })


#@it_isnt_updating
#def geocacher_search_rating_current(request):
    #qs = GeocacherSearchStat.objects.all()
    #qs = qs.select_related('geocacher').filter(year_points__gt=0)
    #qs = qs.order_by('-year_points')

    #source = datasource.QSDataSource(qs)
    #table = GeocacherSearchRankListYear('geocacher_list')

    #cnt = get_controller(table, source, request, settings.ROW_PER_PAGE)

    #rc = cnt.process_request()
    #if rc:
        #return rc

    #return render(
        #request,
        #'Geocaching_su/geocacher_list.html',
        #{
            #'table': cnt,
            #'title': _("Current year %s")%datetime.now().year,
            #'curr_year': datetime.now().year,
            #'last_year': datetime.now().year-1
        #})


@accept_ajax
def ajax_converter(request):
    def minutes_from_degree(d):
        f = d - int(d)
        return f * 60

    def seconds_from_degree(d):
        f = d - int(d)
        f = f * 60
        s = f - int(f)

        return s * 60

    rc = {'status': 'ERR',
          'dms': '',
          'd': '',
          'dm': ''
          }

    s = request.POST.get('input')

    Deg = None
    Deg = get_degree(s)

    if Deg is None:
        return rc

    rc['d'] = '%.6f' % Deg
    rc['dms'] = '%d° %d\' %.2f"' % (int(Deg),
                                     int(minutes_from_degree(Deg)),
                                     seconds_from_degree(Deg))
    rc['dm'] = "%d° %.3f\'" % (int(Deg),
                               minutes_from_degree(Deg))

    rc['status'] = 'OK'

    return rc


def distinct_types_list(types):
    alist = []
    for type_ in types:
        if type_ == 'REAL':
            alist += GEOCACHING_SU_REAL_TYPES
        elif type_ == "UNREAL":
            alist += GEOCACHING_SU_UNREAL_TYPES
        elif type_ == 'ALL':
            alist += GEOCACHING_SU_REAL_TYPES + GEOCACHING_SU_UNREAL_TYPES
        else:
            alist.append(type_)
    return list(set(alist))


def get_iso_by_iso3(iso3):
    if iso3 and len(iso3) == 3:
        country = get_object_or_none(GeoCountry,
                                     iso3=iso3)
        if country:
            return country.iso


def get_nickname(request):
    nickname = request.session.get('login_as')
    if not nickname:
        nickname = request.user.gpsfunuser.geocaching_su_nickname
    if nickname:
        nickname = nickname.strip()
    return nickname


def get_list_of_counts(data, all_types):
    types = []
    for cache_type in all_types:
        types.append(data.get(cache_type) or 0)
    return types


#def update_recommendation(geocachers, data):
    #for gc in geocachers:
        #if gc.get('uid') == data[0]:
            #gc['recommendations'] = data[1]


def row_by_date(data, year, month):
    if not data or not year or not month:
        return None

    for item in data:
        if item.get('year') == year and item.get('month') == month:
            return item
    return None


def ym(year, month):
    return year * 100 + month


def get_found_statistics(request, i_found=False):
    nickname = get_nickname(request)
    geocacher = get_object_or_404(Geocacher, nickname=nickname)

    sql = RAWSQL['all_types_by_cacher'] if i_found else RAWSQL['all_types_by_author']
    sql = sql % geocacher.uid

    all_types = []
    for item in iter_sql(sql):
        all_types.append(item[0])

    sql = RAWSQL['found_by_me_caches_owners'] if i_found else RAWSQL['geocachers_found_my_caches']
    sql = sql % geocacher.uid

    geocachers = {}
    for item in iter_sql(sql):
        cacher = {
            'uid': item[0],
            'nick': item[1],
            'all': item[2],
            'last_found_date': item[3],
            'av_grade': item[4],
            'types': [],
        }
        geocachers[item[0]] = cacher

    sql = RAWSQL['i_found_caches_by_cacher_type'] if i_found else RAWSQL['found_my_caches_by_cacher_type']
    sql = sql % geocacher.uid

    uid = 0
    type_counts = {}
    for item in iter_sql(sql):
        if item[0] != uid:
            if uid:
                geocachers[uid]['types'] = get_list_of_counts(
                    type_counts, all_types)
            uid = item[0]
            type_counts = {}
        type_counts[item[1]] = item[2]

    if uid:
        geocachers[uid]['types'] = get_list_of_counts(type_counts, all_types)

    sql = RAWSQL['count_my_recommends'] if i_found else RAWSQL['count_cacher_recommends']
    sql = sql % geocacher.uid

    for item in iter_sql(sql):
        geocachers[item[0]]['recommendations'] = item[1]

    return geocacher, geocachers, all_types


def activity_per_month(last_years=None, creation=False):
    curr_year = datetime.now().year
    curr_month = datetime.now().month

    if last_years and int(last_years) > 0:
        year_ = curr_year - int(last_years) + 1
        month_ = 1
    else:
        sql = """
        SELECT YEAR(MIN(found_date)), MONTH(MIN(found_date))
        FROM log_seek_cach"""
        year_, month_ = sql2list(sql)

        sql = """
        SELECT YEAR(MIN(created_date)), MONTH(MIN(created_date))
        FROM log_create_cach"""
        year2, month2 = sql2list(sql)
        if ym(year2, month2) < ym(year_, month_):
            year_ = year2
            month_ = month2

    # init data table
    data_table = []
    field1 = 'found'
    field2 = 'created'
    if creation:
        field1 = 'trad'
        field2 = 'virt'
    for y in range(curr_year - year_ + 1):
        for m in range(12):
            if ym(y + year_, m + 1) >= ym(year_, month_) and \
               ym(y + year_, m + 1) <= ym(curr_year, curr_month):
                data_table.append({'year': y + year_,
                                   'month': m + 1,
                                   field1: 0,
                                   field2: 0})

    sql = RAWSQL['real_created_by_years'] if creation else RAWSQL['found_by_years']

    for item in iter_sql(sql):
        row = row_by_date(data_table, item[0], item[1])
        if row:
            row[field1] = item[2]

    sql = RAWSQL['virt_created_by_years'] if creation else RAWSQL['caches_created_by_years']
    for item in iter_sql(sql):
        row = row_by_date(data_table, item[0], item[1])
        if row:
            row[field2] = item[2]

    return data_table


def get_caches(request, country_code, region_ids, type_ids, related_ids):
    if 'all' in region_ids:
        caches = Cach.objects.filter(country_code=country_code,
                                     type_code__in=GEOCACHING_SU_ONMAP_TYPES)
    else:
        caches = Cach.objects.filter(country_code=country_code,
                                     admin_code__in=region_ids,
                                     type_code__in=GEOCACHING_SU_ONMAP_TYPES)
    if not type_ids:
        caches = []
    else:
        if not 'all' in type_ids:
            caches = caches.filter(type_code__in=type_ids)
    if related_ids:
        user_pid = request.session.get('pid')
        if not 'all' in related_ids and user_pid:
            if 'mine' in related_ids:
                caches = caches.filter(created_by=user_pid)
            if 'vis' in related_ids:
                caches = caches.extra(
                    where=["pid IN (SELECT cach_pid FROM log_seek_cach WHERE cacher_uid=%s)" % user_pid])
            if 'notvis' in related_ids:
                caches = caches.exclude(created_by=user_pid)
                caches = caches.extra(where=[
                                      "pid NOT IN (SELECT cach_pid FROM log_seek_cach WHERE cacher_uid=%s)" % user_pid])
    return caches


def geocacher_year_statistics(geocacher, year_, last_year, creation=False):
    counter_current_year = \
        get_geocacher_year_statistics(
            RAWSQL['geocacher_one_year_created_by_months'] if creation else RAWSQL['geocacher_one_year_found_by_months'],
            year_, geocacher)

    counter_last_year = \
        get_geocacher_year_statistics(
            RAWSQL['geocacher_one_year_created_by_months'] if creation else RAWSQL['geocacher_one_year_found_by_months'],
            last_year, geocacher)

    sql = RAWSQL['first_year_created'] if creation else RAWSQL['first_year_found']
    sql = sql % (geocacher.uid)

    first_year = sql2val(sql)

    return counter_current_year, counter_last_year, first_year


def create_chart(
    max_value, val2, val3, data1, data2, labels, legend_y, dmax,
    name1='', name2='', width=700, height=250):

    color1 = '#f89d53'
    color2 = '#c56a20'
    linecolor1 = '#987'
    linecolor2 = '#876'

    chart = QuickChart()
    chart.width = width
    chart.height = height
    chart.device_pixel_ratio = 2.0

    chart.config = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': [
                {
                    'borderColor': linecolor1,
                    'backgroundColor': color1,
                    'pointRadius': 0,
                    'fill': 1,
                    'label': str(name1),
                    'data': data1
                },
                {
                    'borderColor': linecolor2,
                    'backgroundColor': color2,
                    'pointRadius': 0,
                    'fill': 'start',
                    'label': str(name2),
                    'data': data2
                }
            ],
        },
        'options': {
            'plugins': {
            }
        }
    }

    return chart


def get_personal_caches_bar(request, geocacher_uid, sql):
    nickname = get_nickname(request)
    geocacher = get_object_or_404(Geocacher, nickname=nickname)

    sql = sql % geocacher.uid
    chart = get_geocacher_bar_chart(sql, 200, 150)

    return chart


def cach_rate(request, order_by, TableClass, template):
    qs = CachStat.objects.all().order_by(order_by)
    source = datasource.QSDataSource(qs)

    table = TableClass('cach_search')
    cnt = GPSFunTableController(table,
                                source,
                                request,
                                settings.ROW_PER_PAGE)
    cnt.kind = 'cache_rate'
    cnt.allow_manage_profiles = False

    rc = cnt.process_request()

    if rc:
        return rc

    return render(
        request,
        template,
        {
            'table': cnt,
        })


def geocaching_su_profile(request, nickname):
    geocacher = get_object_or_none(Geocacher, nickname=nickname)
    if geocacher:
        url = 'https://geocaching.su/profile.php?uid=%d' % geocacher.uid
    else:
        url = 'https://geocaching.su/?pn=108'
    return HttpResponseRedirect(url)


def get_controller(table, source, request, rows_per_page):
    cnt = GPSFunTableController(table, source, request, rows_per_page)
    cnt.kind = 'geocacher_rate'
    cnt.allow_manage_profiles = False

    return cnt


def get_geocacher_year_statistics(sql, year, geocacher):
    sql = RAWSQL['geocacher_one_year_created_by_months']
    sql = sql % (geocacher.uid, year)

    months = {}
    for item in iter_sql(sql):
        months[item[0]] = item[1]
    counters = []
    for m in range(12):
        counters.append(
            {'count': months.get(m + 1) or 0,
             'month': m + 1})
    return counters


def get_piechart(sql, width, height):
    colors = ['#f83c38', '#e61a16', '#1a7ddd', '#3c9fff',
        '#9dd872', '#d67b31', '#7bb650', '#f89d53']
    data = []
    labels = []

    for item in iter_sql(sql):
        data.append(item[1])
        labels.append(item[0])

    chart = QuickChart()
    chart.width = width
    chart.height = height
    chart.device_pixel_ratio = 2.0

    chart.config = {
        'type': 'doughnut',
        'data': {
            'labels': labels,
            'datasets': [{
                'backgroundColor': colors,
                'data': data}],
        },
        'options': {
            'plugins': {
                'datalabels': {
                    'display': True,
                    'backgroundColor': '#ccc',
                    'borderRadius': 3,
                    'font': {
                        'color': 'red',
                        'weight': 'bold',
                        'size': 10
                    },
                },
                'doughnutlabel': {
                    'labels': [
                        {
                            'text': str(sum(data)),
                            'font': {
                                'size': 14,
                                'weight': 'bold'
                            }
                        },
                        {
                            'text': str(_('total'))}]}
            }

        }
    }

    return chart


def get_geocacher_bar_chart(sql, width, height):
    type_colors = {
        'EV': '#f83c38',
        'CT': '#777',
        'LT': '#1a7ddd',
        'LV': '#3c9fff',
        'MS': '#9dd872',
        'MV': '#d67b31',
        'TR': '#7bb650',
        'VI': '#f89d53'
    }
    data = []
    labels = []
    colors = []

    for item in iter_sql(sql):
        data.append(item[1])
        labels.append(item[0])
        colors.append(type_colors[item[0]])

    chart = QuickChart()
    chart.width = width
    chart.height = height
    chart.device_pixel_ratio = 2.0

    chart.config = {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets': [{
                'backgroundColor': colors,
                'barThickness': 15,
                'data': data}],
        },
        'options': {
            'legend': {
                'display': False,
            },
            'labels': {
                'fontSize': 10,
            },
            'scales': {
                'yAxes': [
                    {
                        'ticks': {
                            'fontSize': 6
                        }
                    }
                ],
                'xAxes': [
                    {
                        'ticks': {
                            'fontSize': 6
                        }
                    }
                ]

            }
        }
    }

    return chart


def get_chart_data(sql):
    data = []
    legend = []
    summ = 0
    for item in iter_sql(sql):
        summ += item[1]
        data.append(summ)
        legend.append(item[0])
    return data, legend, summ


def created_caches_per_year():
    cache_per_year = []
    sql = """
    SELECT DISTINCT
    YEAR(created_date) as year_
    FROM cach
    ORDER BY year_
    """
    for item in iter_sql(sql):
        cache_per_year.append({'year': item[0], 'types': {}})

    sql = """
    SELECT DISTINCT type_code
    FROM cach
    WHERE type_code IS NOT NULL AND type_code != ''
    """
    for item in iter_sql(sql):
        for one in cache_per_year:
            one['types'][item[0]] = 0

    sql = """
    SELECT type_code, YEAR(created_date) as year_, COUNT(*)
    FROM cach
    WHERE type_code IS NOT NULL AND type_code != ''
    GROUP BY type_code, year_
    """
    for item in iter_sql(sql):
        year_item = find_item_by_year(cache_per_year, item[1])
        if year_item:
            year_item['types'][item[0]] = item[2]

    return cache_per_year
