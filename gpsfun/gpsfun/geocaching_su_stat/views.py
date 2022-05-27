"""
views for application geocaching_su_stat
"""

import time
import itertools
from datetime import datetime, date
import django_filters
from lxml import etree

from pygooglechart import SimpleLineChart, StackedHorizontalBarChart
from pygooglechart import Axis
from quickchart import QuickChart

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
from django.utils.translation import ugettext_lazy as _

import django_tables2 as tables
from django_tables2.config import RequestConfig

from gpsfun.tableview import table, widgets, datasource, controller
from gpsfun.main.db_utils import iter_sql
from gpsfun.main.db_utils import get_object_or_none
from gpsfun.main.ajax import accept_ajax

from gpsfun.main.GeoCachSU.models import Cach, CachStat, Geocacher, \
    GEOCACHING_SU_CACH_TYPES, GEOCACHING_SU_REAL_TYPES, \
    GEOCACHING_SU_UNREAL_TYPES, LogSeekCach, LogCreateCach, \
    GeocacherStat, GEOCACHING_SU_ONMAP_TYPES, GeocacherSearchStat
from gpsfun.main.GeoCachSU.utils import (
    populate_cach_type, populate_country_iso3, populate_subjects,
    populate_countries_iso3, countries_iso, cache_types, countries_iso3)
from gpsfun.main.GeoName.models import GeoCountry, GeoCountryAdminSubject, \
    country_iso_by_iso3, geocountry_by_code
from gpsfun.main.models import LogUpdate
from gpsfun.main.db_utils import sql2list, sql2val
from gpsfun.geocaching_su_stat.decorators import it_isnt_updating, geocacher_su
from gpsfun.main.utils import get_degree
from gpsfun.main.forms import RequestForm
from gpsfun.geocaching_su_stat.sql import RAWSQL


MONTH_SHORT_NAMES = [
    _('Jan'), _('Feb'), _('Mar'), _('Apr'), _('May'), _('Jun'),
    _('Jul'), _('Aug'), _('Sep'), _('Oct'), _('Nov'), _('Dec')
]


def geocaching_su_cach_url(pid):
    """ cache url """
    return f"http://www.geocaching.su/?pn=101&cid={pid}"


def geocaching_su_geocacher_url(pid):
    """ geocacher url """
    return f"http://www.geocaching.su/profile.php?pid={pid}"


class GPSFunTableController(controller.TableController):
    """ Table controller """
    kind = None

    def filter_description(self):
        """ description """
        def valid_keys(afilter, kind):
            """ valid keys """
            if kind == 'geocacher_rate':
                if 'country' in afilter and 'subject' in afilter:
                    return True
            if kind == 'cache_rate':
                if 'country' in afilter and 'cach_type' in afilter:
                    return True
            return False

        def country_description(country):
            """ country description """
            by_country = {'title': _('Country'), 'value': _("All")}
            if country and country != 'ALL':
                geocountry = geocountry_by_code(country)
                if geocountry:
                    by_country['value'] = _(geocountry.name)
                else:
                    by_country['value'] = country
            return by_country

        def subject_description(admin_subject, country):
            """ subject description """
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

        description = []
        if self.kind == 'cache_rate':
            selected_values = self.filter.get('cach_type')
            if selected_values == ['']:
                selected_values = []

            if not selected_values or ('ALL' in selected_values) or \
               ('REAL' in selected_values and 'UNREAL' in selected_values):
                selected_values = []
            if selected_values:
                selected_values = distinct_types_list(selected_values)

            types = [GEOCACHING_SU_CACH_TYPES.get(type_)
                     for type_ in selected_values
                     if GEOCACHING_SU_CACH_TYPES.get(type_) is not None]

            if len(types) == 0:
                types = [_("Any")]
            if types:
                description.append({
                    'title': _('Cach Type'),
                    'value': types,
                    'type': 'list'})
            country = self.filter.get('country')
            description.append(country_description(country))
            description.append(subject_description(self.filter.get('subject'), country))

        if self.kind == 'geocacher_rate':
            country = self.filter.get('country')
            description.append(country_description(country))
            description.append(subject_description(self.filter.get('subject'), country))

        return description


class RankingFilter(RequestForm):
    """ Ranking Filter """
    country_ = None
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
        """ init """
        self.country_ = self.initial.get('country')
        if self.country_ is None:
            self.country_ = self.data.get('country')

        populate_cach_type(self.fields['cach_type'], request=self._request, add_empty=True)

        populate_countries_iso3(self.fields['country'], request=self._request, add_empty=True)
        populate_subjects(
            self.fields['subject'],
            request=self._request,
            add_empty=True,
            selected_country_iso=self.country_)


class RateFilter(RequestForm):
    """ Rate Filter """
    country_ = None
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
        """ init """
        self.country_ = self.initial.get('country')
        if self.country_ is None:
            self.country_ = self.data.get('country')

        populate_country_iso3(
            self.fields['country'], request=self._request, add_empty=True)
        populate_subjects(
            self.fields['subject'],
            request=self._request,
            add_empty=True,
            selected_country_iso=self.country_)

    def set_country(self, country):
        """ set country """
        self.country_ = country
        populate_subjects(
            self.fields['subject'],
            request=self._request,
            selected_country_iso=self.country_)


class BaseRankTable(table.TableView):
    """ Base Rank Table """
    _filter = None

    def apply_filter(self, filter, qs):
        """ apply filter """
        self._filter = {}
        for key, value in filter.iteritems():
            self._filter[key] = value
        selected_values = filter.get('cach_type') or []
        if selected_values and ('REAL' in selected_values) \
           and ('UNREAL' in selected_values):
            pass
        elif selected_values and ('ALL' in selected_values):
            pass
        else:
            selected_values = distinct_types_list(selected_values)
            if selected_values:
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
        """ filtered or not """
        if hasattr(self, '_filter'):
            return self._filter is not None
        return False


class RankByList(BaseRankTable):
    """ Rank By List Table """
    pid = widgets.HrefWidget(
        'ID',
        width="55px",
        refname='cach__code',
        reverse='geocaching-su-cach-view',
        reverse_column='cach_pid')
    cach_name = widgets.LabelWidget(_('Cach'), refname='cach__name')
    created = widgets.LabelWidget(_('Created'), refname='cach__created_date')
    author = widgets.HrefWidget(
        _('Author'),
        refname='geocacher__nickname',
        reverse='geocaching-su-geocacher-view',
        reverse_column='geocacher__pid')
    recommend_count = widgets.LabelWidget(
        _('Recommendations'),
        refname='recommend_count')
    grade = widgets.LabelWidget(_('Grade'), refname='cach__grade')


class RankByComputedList(RankByList):
    """ Table RankByComputedList """
    found_count = widgets.LabelWidget(_('Found'), refname='found_count')
    rank = widgets.LabelWidget(_('Rank'), refname='rank')

    class Meta:
        use_keyboard = True
        global_profile = True
        permanent = (
            'pid', 'cach_name', 'author', 'created',
            'recommend_count', 'found_count', 'rank', 'grade')
        search = ('cach__name', 'geocacher__nickname', 'cach__code')
        filter_form = RankingFilter

    def render_rank(self, table, row_index, row, value):
        """ render field rank """
        return f'{value:.0f}' if value else ''

    def render_grade(self, table, row_index, row, value):
        """ render field grade """
        return f'{value:.2f}' if value else None

    def render_created(self, table, row_index, row, value):
        """ render field created """
        return value.strftime("%d.%m.%Y") if value else ''


class RankByFoundList(RankByList):
    """ Table RankByFoundList """
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
        """ render field created """
        return value.strftime("%d.%m.%Y") if value else ''

    def render_points(self, table, row_index, row, value):
        """ render field points """
        return round(value, 1) if value else 0


class RankByRecommendedList(RankByList):
    """ Table RankByRecommendedList """

    class Meta:
        use_keyboard = True
        global_profile = True
        permanent = (
            'pid', 'cach_name', 'author', 'created',
            'recommend_count', 'grade')
        search = ('cach__name', 'geocacher__nickname', 'cach__code')
        filter_form = RankingFilter

    def render_grade(self, table, row_index, row, value):
        """ render field grade """
        value = value or 0
        return '{value:.2f}'

    def render_created(self, table, row_index, row, value):
        """ render field created """
        return value.strftime("%d.%m.%Y") if value else ''


class GeocacherRateList(table.TableView):
    """ Table GeocacherRateList """
    nickname = widgets.HrefWidget(
        _('Nickname'),
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
        permanent = (
            'nickname', 'country', 'region', 'registered',
            'created_count', 'found_count', 'av_grade',
            'av_his_cach_grade')
        search = ('geocacher__nickname',)
        sortable = ('created_count', 'found_count')
        filter_form = RateFilter

    def apply_filter(self, filter, qs):
        """ apply_filter """
        self._filter = {}
        for key, value in filter.iteritems():
            self._filter[key] = value

        country = filter.get('country', '')
        if country and country != "ALL":
            qs.filter(geocacher__country_iso3=country)

        subject = filter.get('subject', '')
        if subject and subject != 'ALL':
            if subject == '777':
                qs.filter(
                    geocacher__country_iso3=country,
                    geocacher__admin_code__isnull=True)
            else:
                qs.filter(
                    geocacher__country_iso3=country,
                    geocacher__admin_code=subject)

    def filtered(self):
        """ filtered or not """
        if '_filter' in self:
            return self._filter is not None
        return False

    def render_av_grade(self, table, row_index, row, value):
        """ render field av_grade """
        value = value or 0
        return f'{value:.1f}'

    def render_av_his_cach_grade(self, table, row_index, row, value):
        """ render field av_his_cach_grade """
        value = value or 0
        return f'{value:.1f}'

    def render_registered(self, table, row_index, row, value):
        """ render field registered """
        return value.strftime("%Y") if value else ''

    def render_country(self, table, row_index, row, value):
        """ render field country """
        return _(value) if value else ''

    def render_region(self, table, row_index, row, value):
        """ render field region """
        return _(value) if value else ''


class GeocacherRankListBase(table.TableView):
    """ Table GeocacherRankListBase """
    nickname = widgets.HrefWidget(
        _('Nickname'),
        refname='geocacher__nickname',
        reverse='geocaching-su-geocacher-view',
        reverse_column='geocacher__pid')
    country = widgets.LabelWidget(_('Country'), refname='country')
    region = widgets.LabelWidget(_('Region'), refname='region')
    registered = widgets.LabelWidget(
        _('Registered'), refname='geocacher__register_date')
    created_count = None
    found_count = None

    class Meta:
        use_keyboard = True
        global_profile = True
        permanent = (
            'nickname', 'country', 'region', 'registered',
            'created_count', 'found_count')
        search = ('geocacher__nickname',)
        sortable = ('created_count', 'found_count')
        filter_form = RateFilter

    def apply_filter(self, filter, qs):
        """ apply filter """
        self._filter = None

        country = filter.get('country')
        if country and country != 'ALL':
            qs.filter(geocacher__country_iso3=country)
            self._filter = filter

        subject = filter.get('subject', '')
        if subject and subject != 'ALL':
            if subject == '777':
                qs.filter(
                    geocacher__country_iso3=country,
                    geocacher__admin_code__isnull=True)
            else:
                qs.filter(
                    geocacher__country_iso3=country,
                    geocacher__admin_code=subject)
            self._filter = filter

    def filtered(self):
        """ filtered or not """
        if '_filter' in self:
            return self._filter is not None
        return False

    def render_registered(self, table, row_index, row, value):
        """ render field registered """
        return value.strftime("%Y") if value else ''

    def render_country(self, table, row_index, row, value):
        """ render field country """
        return _(value) if value else ''

    def render_region(self, table, row_index, row, value):
        """ render field region """
        return _(value) if value else ''


class GeocacherVirtRankList(GeocacherRankListBase):
    """ Table GeocacherVirtRankList """
    created_count = widgets.LabelWidget(
        _('Created by'), refname='vi_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='vi_found_count')


class GeocacherTradRankList(GeocacherRankListBase):
    """ Table  GeocacherTradRankList """
    created_count = widgets.LabelWidget(
        _('Created by'), refname='tr_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='tr_found_count')


class GeocacherCurrYearRateList(GeocacherRankListBase):
    """ Table GeocacherCurrYearRankList """
    created_count = widgets.LabelWidget(
        _('Created by'), refname='curr_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='curr_found_count')


class GeocacherCurrYearVirtRankList(GeocacherRankListBase):
    """ Table GeocacherCurrYearVirtRankList """
    created_count = widgets.LabelWidget(
        _('Created by'), refname='vi_curr_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='vi_curr_found_count')


class GeocacherCurrYearTradRankList(GeocacherRankListBase):
    """ Table GeocacherCurrYearTradRankList """
    created_count = widgets.LabelWidget(
        _('Created by'), refname='tr_curr_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='tr_curr_found_count')


class GeocacherLastYearRateList(GeocacherRankListBase):
    """ Table GeocacherLastYearRankList """
    created_count = widgets.LabelWidget(
        _('Created by'), refname='last_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='last_found_count')


class GeocacherLastYearVirtRankList(GeocacherRankListBase):
    """ Table GeocacherLastYearVirtRankList """
    created_count = widgets.LabelWidget(
        _('Created by'), refname='vi_last_created_count')
    found_count = widgets.LabelWidget(_('Found'), refname='vi_last_found_count')


class GeocacherLastYearTradRankList(GeocacherRankListBase):
    """ Table GeocacherLastYearTradRankList """
    created_count = widgets.LabelWidget(
        _('Created by'), refname='tr_last_created_count')
    found_count = widgets.LabelWidget(
        _('Found'), refname='tr_last_found_count')


class GeocacherSearchRankListBase(table.TableView):
    """ Table GeocacherSearchRankListBase """
    nickname = widgets.HrefWidget(
        _('Nickname'),
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
        """ apply_filter """
        self._filter = None

        country = filter.get('country')
        if country and country != 'ALL':
            qs.filter(geocacher__country_iso3=country)
            self._filter = filter

        subject = filter.get('subject', '')
        if subject and subject != 'ALL':
            if subject == '777':
                qs.filter(
                    geocacher__country_iso3=country,
                    geocacher__admin_code__isnull=True)
            else:
                qs.filter(
                    geocacher__country_iso3=country,
                    geocacher__admin_code=subject)
            self._filter = filter

    def filtered(self):
        """ filtered or not """
        if '_filter' in self:
            return self._filter is not None
        return False

    def render_country(self, table, row_index, row, value):
        """ render field country """
        return _(value) if value else ''

    def render_region(self, table, row_index, row, value):
        """ render field region """
        return _(value) if value else ''


class GeocacherSearchRankListYear(table.TableView):
    """ Table GeocacherSearchRankListYear """
    nickname = widgets.HrefWidget(
        _('Nickname'),
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
        """ apply filter """
        self._filter = None

        country = filter.get('country')
        if country and country != 'ALL':
            qs.filter(geocacher__country_iso3=country)
            self._filter = filter

        subject = filter.get('subject', '')
        if subject and subject != 'ALL':
            if subject == '777':
                qs.filter(
                    geocacher__country_iso3=country,
                    geocacher__admin_code__isnull=True)
            else:
                qs.filter(
                    geocacher__country_iso3=country,
                    geocacher__admin_code=subject)
            self._filter = filter

    def filtered(self):
        """ filtered or not """
        if '_filter' in self:
            return self._filter is not None
        return False

    def render_country(self, table, row_index, row, value):
        """ render field country """
        return _(value) if value else ''

    def render_region(self, table, row_index, row, value):
        """ render field region """
        return _(value) if value else ''


def get_base_count(request):
    """ get base count """
    page = int(request.GET.get('page') or 0)
    if page:
        return (page - 1) * settings.ROW_PER_PAGE
    return 0


class CacheTable(tables.Table):
    """ Cache Table """
    counter = tables.Column(
        verbose_name="#", empty_values=(), orderable=False)
    pid = tables.Column(accessor='cach_pid', verbose_name=_("pid"))
    type_code = tables.Column(
        accessor='cach__type_code', verbose_name=_("Type"))
    cache = tables.Column(accessor='cach__name', verbose_name=_("Name"))
    country = tables.Column(
        accessor='cach__country_code', verbose_name=_("Country"))
    created = tables.Column(
        accessor='cach__created_date', verbose_name=_("Created date"))
    geocacher = tables.Column(
        accessor='geocacher__nickname', verbose_name=_("Author"))
    grade = tables.Column(accessor='cach__grade', verbose_name=_("Grade"))

    class Meta:
        attrs = {'class': 'table'}

    def render_created(self, value):
        """ render field created """
        return value.strftime('%Y-%m-%d')

    def render_counter(self):
        """ render field counter """
        self.row_counter = getattr(
            self, 'row_counter', itertools.count(self.page.start_index()))
        return next(self.row_counter)

    def render_grade(self, value):
        """ render field grade """
        return f'{value:.1f}'

    def render_country(self, value):
        """ render field country """
        country = GeoCountry.objects.filter(iso=value).first()
        return _(country.name) if country else None

    def render_pid(self, value):
        """ render field pid """
        return format_html(
            '<a href="{}">{}</a>',
            f'https://geocaching.su/?pn=101&cid={value}', value)


class CacheRecommendsTable(CacheTable):
    """ Table CacheRecommends """
    recommend_count = tables.Column(verbose_name=_('Recommendations'))


class CacheFoundTable(CacheTable):
    """ Table CacheFound """
    found_count = tables.Column(verbose_name=_('Found'))


class CacheIndexTable(CacheTable):
    """ Table CacheIndex """
    found_count = tables.Column(verbose_name=_('Found'))
    recommend_count = tables.Column(verbose_name=_('Recommendations'))
    rank = tables.Column(verbose_name=_('Rating'))

    def render_rank(self, value):
        """ render field rank """
        return f'{value:.1f}'


@it_isnt_updating
def cach_rate_by_recommend(request):
    """ get list of caches rated by recommendations """
    order_by = '-recommend_count'
    qset = CachStat.objects.all().order_by(order_by)

    filtr = CacheStatFilter(request.GET, queryset=qset)

    the_table = CacheRecommendsTable(filtr.qs)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(the_table)
    return render(
        request,
        'Geocaching_su/dt2-cach_rank_by_recommend.html',
        {'table': the_table, 'filter': filtr})


class CacheStatFilter(django_filters.FilterSet):
    """ Filter CacheStat """
    cach__country_code = django_filters.ChoiceFilter(
        lookup_expr='iexact',
        choices=countries_iso,
        label=_('Country')
    )
    cach__type_code = django_filters.ChoiceFilter(
        lookup_expr='iexact',
        choices=cache_types,
        label=_('Type')
    )

    class Meta:
        model = CachStat
        fields = ['cach__country_code', 'cach__type_code']


@it_isnt_updating
def cach_rate_by_found(request):
    """ get list of caches rated by found """
    order_by = '-found_count'
    qset = CachStat.objects.all().order_by(order_by)

    filtr = CacheStatFilter(request.GET, queryset=qset)

    the_table = CacheFoundTable(filtr.qs)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(the_table)
    return render(
        request,
        'Geocaching_su/dt2-cach_rank_by_found.html',
        {'table': the_table, 'filter': filtr})


@it_isnt_updating
def cach_rate_by_index(request):
    """ get list of caches rated by special index """
    order_by = '-rank'
    qset = CachStat.objects.all().order_by(order_by)

    filtr = CacheStatFilter(request.GET, queryset=qset)

    the_table = CacheIndexTable(filtr.qs)
    RequestConfig(
        request, paginate={"per_page": 100}).configure(the_table)
    return render(
        request,
        'Geocaching_su/dt2-cache_rank_by_index.html',
        {'table': the_table, 'filter': filtr})


@it_isnt_updating
def activity_table(request, qset, table_class, title, table_slug, additional_meta=True):
    """ get list of geocachers with activity data """
    source = datasource.QSDataSource(qset)

    the_table = table_class(table_slug)
    if additional_meta:
        the_table.use_keyboard = True
        the_table.global_profile = True
        the_table.permanent = (
            'nickname', 'country', 'region', 'registered',
            'created_count', 'found_count')
        the_table.search = ('geocacher__nickname',)
        the_table.sortable = ('created_count', 'found_count')
        the_table.filter_form = RateFilter

    cnt = get_controller(the_table, source, request, settings.ROW_PER_PAGE)

    result = cnt.process_request()
    if result:
        return result

    return render(
        request,
        'Geocaching_su/geocacher_list.html',
        {'table': cnt,
         'title': title,
         'curr_year': datetime.now().year,
         'last_year': datetime.now().year - 1})


class GeocacherStatFilter(django_filters.FilterSet):
    """ Filter Geocacher Stat """
    geocacher__country_iso3 = django_filters.ChoiceFilter(
        lookup_expr='iexact',
        choices=countries_iso3,
        label=_('Country')
    )

    class Meta:
        model = GeocacherStat
        fields = ['geocacher__country_iso3', ]


class GeocacherTable(tables.Table):
    """ Table Geocacher """
    counter = tables.Column(verbose_name="#", empty_values=(), orderable=False)
    nickname = tables.Column(verbose_name=_("Nickname"),
                             accessor='geocacher__nickname')
    country = tables.Column(verbose_name=_("Country"), accessor='country')
    region = tables.Column(verbose_name=_("Region"), accessor='region')
    registered = tables.Column(
        verbose_name=_("Register date"), accessor='geocacher__register_date')

    def render_registered(self, value):
        """ render field registered """
        return value.strftime('%Y')

    def render_counter(self):
        """ render field counter """
        self.row_counter = getattr(
            self, 'row_counter', itertools.count(self.page.start_index()))
        return next(self.row_counter)

    def render_country(self, value):
        """ render field country """
        return _(value) if value else ''

    def render_region(self, value):
        """ render field region """
        return _(value) if value else ''

    def render_nickname(self, value):
        """ render field nick """
        return format_html(
            '<a href="{}">{}</a>',
            reverse('gcsu-profile', args=[value]), value)

    class Meta:
        template_name = "django_tables2/bootstrap.html"


class GeocacherRateTable(GeocacherTable):
    """ Table Geocacher Rate """
    found_count = tables.Column(verbose_name=_("Found"),)
    created_count = tables.Column(verbose_name=_("Created"),)
    av_grade = tables.Column(verbose_name=_('Average grade'))
    av_his_cach_grade = tables.Column(
        verbose_name=_('Av. grade of his caches'))

    def render_av_grade(self, value):
        """ render field av_grade """
        value = value or 0
        return f'{value:.1f}'

    def render_av_his_cach_grade(self, value):
        """ render field  av_his_cach_grade """
        value = value or 0
        return f'{value:.1f}'


class GeocacherRateCurrYearTable(GeocacherTable):
    """ Table Geocacher Rate Current Year """
    curr_found_count = tables.Column(verbose_name=_('Found'))
    curr_created_count = tables.Column(verbose_name=_('Created'))


class GeocacherRateLastYearTable(GeocacherTable):
    """ Table Geocacher Rate Last Year """
    last_found_count = tables.Column(verbose_name=_('Found'))
    last_created_count = tables.Column(verbose_name=_('Created'))


class GeocacherRateUnrealTable(GeocacherTable):
    """ Table Geocacher Rate Unreal """
    vi_found_count = tables.Column(verbose_name=_('Found'))
    vi_created_count = tables.Column(verbose_name=_('Created'))


class GeocacherRateUnrealCurrYearTable(GeocacherTable):
    """ Table Geocacher Rate Unreal Current Year """
    vi_curr_found_count = tables.Column(verbose_name=_('Found'))
    vi_curr_created_count = tables.Column(verbose_name=_('Created'))


class GeocacherRateUnrealLastYearTable(GeocacherTable):
    """ Table Geocacher Rate Unreal Last Year """
    vi_last_found_count = tables.Column(verbose_name=_('Found'))
    vi_last_created_count = tables.Column(verbose_name=_('Created'))


class GeocacherRateRealTable(GeocacherTable):
    """ Table Geocacher Rate Real """
    tr_found_count = tables.Column(verbose_name=_('Found'))
    tr_created_count = tables.Column(verbose_name=_('Created'))


class GeocacherRateRealCurrYearTable(GeocacherTable):
    """ Table Geocacher Rate Real Current Year """
    tr_curr_found_count = tables.Column(verbose_name=_('Found'))
    tr_curr_created_count = tables.Column(verbose_name=_('Created'))


class GeocacherRateRealLastYearTable(GeocacherTable):
    """ Table Geocacher Rate Real Last Year """
    tr_last_found_count = tables.Column(verbose_name=_('Found'))
    tr_last_created_count = tables.Column(verbose_name=_('Created'))


class GeocacherSearchTable(tables.Table):
    """ Table Geocacher Search """
    counter = tables.Column(verbose_name="#", empty_values=(), orderable=False)
    nickname = tables.Column(verbose_name=_(
        "Nickname"), accessor='geocacher__nickname')
    country = tables.Column(verbose_name=_("Country"), accessor='country')
    region = tables.Column(verbose_name=_("Region"), accessor='region')
    registered = tables.Column(verbose_name=_(
        "Registered"), accessor='geocacher__register_date')
    points = tables.Column(verbose_name=_("Points"), accessor='points')

    def render_registered(self, value):
        """ render field registered """
        return value.strftime('%Y')

    def render_counter(self):
        """ render field counter """
        self.row_counter = getattr(
            self, 'row_counter', itertools.count(self.page.start_index()))
        return next(self.row_counter)

    def render_country(self, value):
        """ render country """
        return _(value) if value else ''

    def render_region(self, value):
        """ render field region """
        return _(value) if value else ''

    class Meta:
        template_name = "django_tables2/bootstrap.html"


class GeocacherSearchYearTable(GeocacherSearchTable):
    """ Table GeocacherSearchYear """
    points = tables.Column(verbose_name=_('Points'), accessor='year_points')


@it_isnt_updating
def geocacher_rate(request):
    """
    get list of geocachers by rate
    """
    qset = GeocacherStat.objects.all().order_by('-created_count', '-found_count')

    filtr = GeocacherStatFilter(request.GET, queryset=qset)

    the_table = GeocacherRateTable(filtr.qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(the_table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {
            'table': the_table,
            'filter': filtr,
            'title': _("All caches"),
            'curr_year': datetime.now().year,
            'last_year': datetime.now().year - 1})


@it_isnt_updating
def geocacher_rate_unreal(request):
    """
    get list of geocachers by rate unreal
    """
    qset = GeocacherStat.objects.all().order_by(
        '-vi_created_count', '-vi_found_count')
    title = _("Unreal caches")

    filtr = GeocacherStatFilter(request.GET, queryset=qset)

    the_table = GeocacherRateUnrealTable(filtr.qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(the_table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {
            'table': the_table,
            'filter': filtr,
            'title': title,
            'curr_year': datetime.now().year,
            'last_year': datetime.now().year - 1
         })


@it_isnt_updating
def geocacher_rate_real(request):
    """
    get list of geocachers by rate real
    """
    qset = GeocacherStat.objects.all().order_by(
        '-tr_created_count', '-tr_found_count')
    title = _("Real caches")

    filtr = GeocacherStatFilter(request.GET, queryset=qset)

    the_table = GeocacherRateRealTable(filtr.qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(the_table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {
            'table': the_table,
            'filter': filtr,
            'title': title,
            'curr_year': datetime.now().year,
            'last_year': datetime.now().year - 1
         })


@it_isnt_updating
def geocacher_rate_current(request):
    """
    get list of geocachers by rate current
    """
    qset = GeocacherStat.objects.all().order_by(
        '-curr_created_count', '-curr_found_count')
    title = _("%s. All caches") % datetime.now().year

    filtr = GeocacherStatFilter(request.GET, queryset=qset)

    the_table = GeocacherRateCurrYearTable(filtr.qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(the_table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {
            'table': the_table,
            'filter': filtr,
            'title': title,
            'curr_year': datetime.now().year,
            'last_year': datetime.now().year - 1
         })


@it_isnt_updating
def geocacher_rate_last(request):
    """
    get list of geocachers by rate last year
    """
    qset = GeocacherStat.objects.all().order_by(
        '-last_created_count', '-last_found_count')
    title = _("%s. All caches") % (datetime.now().year - 1)

    filtr = GeocacherStatFilter(request.GET, queryset=qset)

    the_table = GeocacherRateLastYearTable(filtr.qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(the_table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {
            'table': the_table,
            'filter': filtr,
            'title': title,
            'curr_year': datetime.now().year,
            'last_year': datetime.now().year - 1
         })


@it_isnt_updating
def geocacher_rate_unreal_current(request):
    """
    get list of geocachers by rate current unreal
    """
    qset = GeocacherStat.objects.all().order_by(
        '-vi_curr_created_count', '-vi_curr_found_count')
    title = _("%s. Unreal caches") % datetime.now().year

    filtr = GeocacherStatFilter(request.GET, queryset=qset)

    the_table = GeocacherRateUnrealCurrYearTable(filtr.qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(the_table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {
            'table': the_table,
            'filter': filtr,
            'title': title,
            'curr_year': datetime.now().year,
            'last_year': datetime.now().year - 1
         })


@it_isnt_updating
def geocacher_rate_unreal_last(request):
    """
    get list of geocachers by rate last year unreal
    """
    qset = GeocacherStat.objects.all().order_by(
        '-vi_last_created_count', '-vi_last_found_count')
    title = _("%s. Unreal caches") % (datetime.now().year - 1)

    filtr = GeocacherStatFilter(request.GET, queryset=qset)

    the_table = GeocacherRateUnrealLastYearTable(filtr.qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(the_table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {
            'table': the_table,
            'filter': filtr,
            'title': title,
            'curr_year': datetime.now().year,
            'last_year': datetime.now().year - 1
         })


@it_isnt_updating
def geocacher_rate_real_last(request):
    """
    get list of geocachers by rate last year real
    """
    qset = GeocacherStat.objects.all().order_by(
        '-tr_last_created_count', '-tr_last_found_count')
    title = _("%s. Real caches") % (datetime.now().year - 1)

    filtr = GeocacherStatFilter(request.GET, queryset=qset)

    the_table = GeocacherRateRealLastYearTable(filtr.qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(the_table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {
            'table': the_table,
            'filter': filtr,
            'title': title,
            'curr_year': datetime.now().year,
            'last_year': datetime.now().year - 1
         })


@it_isnt_updating
def cach_view(request, cach_pid):
    """ redirect to cache """
    url = geocaching_su_cach_url(cach_pid)
    return HttpResponseRedirect(url)


@it_isnt_updating
def geocacher_view(request, geocacher_uid):
    """ redirect to geocacher """
    url = geocaching_su_geocacher_url(geocacher_uid)
    return HttpResponseRedirect(url)


@it_isnt_updating
def geocaching_su(request):
    """ geocaching generak statistic """
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
        {
            'countries': countries,
            'update_date': update_date.get("last_date")})


def find_item_by_year(items, year):
    """ find item by year """
    for item in items:
        if item.get('year') == year:
            return item


@it_isnt_updating
def geocaching_su_cach_stat(request):
    """ geocaching caches statistics """
    cach_count = Cach.objects.all().count()

    sql = """
    SELECT type_code, COUNT(*)
    FROM cach
    GROUP BY type_code
    """
    cach_table = []

    for item in iter_sql(sql):
        cach_table.append({
            'type': item[0],
            'description': GEOCACHING_SU_CACH_TYPES.get(item[0], ''),
            'count': item[1],
            'percent': float(item[1]) / cach_count * 100})
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
    """ redirect to geocaching statistics """
    return HttpResponseRedirect(reverse('geocaching-su-cach-stat'))


@it_isnt_updating
def geocaching_su_geocacher_stat_countries(request):
    """ geocaching statistics geocachers by countries """
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
        geocacher_table.append({
            'country': country,
            'count': item[1],
            'percent': float(item[1]) / geocacher_count * 100})
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
        active_table.append({
            'country': country,
            'count': item[1],
            'percent': float(item[1]) / active_count * 100})
    return render(
        request,
        'Geocaching_su/geocacher_stat_countries.html',
        {
            'geocacher_count': geocacher_count,
            'active_count': active_count,
            'geocacher_table': geocacher_table,
            'active_table': active_table})


@it_isnt_updating
def geocaching_su_geocacher_stat(request):
    """ redirect to geocachers statistic """
    return HttpResponseRedirect(reverse('geocacher-activity'))


def activity_creating_per_month(last_years=None):
    """ activity creating per month """
    return activity_per_month(last_years, creation=True)


def caches_per_year():
    """ caches per year """
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
    for year in range(curr_year - year_ + 1):
        data_table.append({'year': year + year_, 'real': 0, 'unreal': 0})

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
    """ geocacher activity """
    all_found = LogSeekCach.objects.all().count()
    all_created = LogCreateCach.objects.all().count()

    data_table = activity_per_month()
    data_table.reverse()

    return render(
        request,
        'Geocaching_su/geocacher_activity.html',
        {
            'data_table': data_table,
            'all_found': all_found,
            'all_created': all_created})


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_cach_stat_pie(request):
    """ pie chart for caches statistics """
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
    """ pie chart for found caches """
    chart = get_personal_caches_bar(
        request, RAWSQL['geocacher_found_caches_by_type'])

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@geocacher_su
def geocaching_su_personal_created_cache_pie(request, geocacher_uid):
    """ pie chart for created cache """
    chart = get_personal_caches_bar(
        request, RAWSQL['geocacher_created_caches_by_type'])

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@geocacher_su
def gcsu_personal_found_current_chart(request):
    """ chart for personal found caches, current year """
    nickname = get_nickname(request)
    geocacher = get_object_or_404(Geocacher, nickname=nickname)
    year_ = date.today().year - 1

    sql = f"""
    SELECT MONTH(found_date) as month_, COUNT(l.id) as cnt
    FROM log_seek_cach as l
    WHERE l.cacher_uid={geocacher.uid} AND YEAR(l.found_date)={year_}
    GROUP BY MONTH(found_date)
    """

    months = {}
    for item in iter_sql(sql):
        months[item[0]] = item[1]
    data = []
    legend = []
    for month in range(12):
        data.append(months.get(month + 1) or 0)
        legend.append(str(month + 1))

    width = 400
    height = 160

    chart = StackedHorizontalBarChart(
        width, height,
        x_range=(1, 12))
    chart.set_bar_width(10)
    chart.set_colours(['00ff00', 'ff0000'])
    chart.add_data(data)

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_cach_pertype_stat_chart(request):
    """ chart for caches per type """
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
        data_real, data_unreal, legend, name1=_('real'), name2=_('virtual'))

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_cache_per_type_chart(request):
    """ chart for caches per type """
    # color1 = '#f89d53'
    # color2= '#c56a20'
    # linecolor1= '#987'
    # linecolor2= '#876'

    chart = QuickChart()
    chart.width = 700
    chart.height = 250
    chart.device_pixel_ratio = 2.0

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
    """ chart for caches statistics """
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
    """ chart for activity of geocachers """
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
        if not legend_y or (legend_y[-1] != row['year']):
            legend_y.append(row['year'])
        if dmax < row['created']:
            dmax = row['created']
        if dmax < row['found']:
            dmax = row['found']

    chart = create_chart(
        dataf, datac, legend, name1=_('found'), name2=_('created')
    )

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_geocacher_activity_creating_chart(request):
    """ chart for activity of geocachers, creating """
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
        if not legend_y or (legend_y[-1] != row['year']):
            legend_y.append(row['year'])
        if dmax < row['trad']:
            dmax = row['trad']
        if dmax < row['virt']:
            dmax = row['virt']

    chart = create_chart(
        dataf, datac, legend, name1=_('traditional'), name2=_('virtual')
    )

    return HttpResponseRedirect(chart.get_url())


@it_isnt_updating
@cache_page(60 * 60 * 8)
def geocaching_su_geocacher_stat_chart(request):
    """ chart for geocachers statistic """
    width = 600
    height = 300
    labels = []

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
    """ pie chart for geocachers statistics """
    only_active_filter = ''
    if only_active:
        only_active_filter = 'WHERE g.found_caches > 0 '

    sql = f"""
    SELECT gc.name, COUNT(*) as cnt
    FROM geocacher g
    LEFT JOIN geo_country gc ON g.country_iso3=gc.iso3
    {only_active_filter}
    GROUP BY gc.name
    HAVING cnt > 99
    """
    data = []
    labels = []

    for item in iter_sql(sql):
        country = item[0] if item[0] else "Undefined"
        data.append(item[1])
        labels.append(country)

    sql = f"""
    SELECT gc.name, COUNT(*) as cnt
    FROM geocacher g
    LEFT JOIN geo_country gc ON g.country_iso3=gc.iso3
    {only_active_filter}
    GROUP BY gc.name
    HAVING cnt < 100
    """
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
    """ geocaching chart """
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
    """ get cache information """
    responce = {'status': 'ERR'}
    pid = request.GET.get('cache_pid')
    cache = get_object_or_none(Cach, pid=pid)
    if not cache:
        return responce
    responce['content'] = render_to_string(
        'Geocaching_su/cache_info.html',
        RequestContext(
            request,
            {'cache': cache}))
    responce['status'] = 'OK'

    return responce


@it_isnt_updating
@accept_ajax
def change_country(request):
    """ change country """
    responce = {'status': 'ERR'}
    country_code = request.GET.get('country')
    request.session['country'] = country_code
    request.session['region'] = []
    if not country_code:
        return responce
    country = get_object_or_none(GeoCountry, iso=country_code)
    address = 'Ukraine, Kharkov'
    if country:
        address = f'{country.name},{country.capital}'
    regions = GeoCountryAdminSubject.objects.filter(country_iso=country_code)
    regions = regions.values('code', 'name').order_by('name')
    responce['regions'] = list(regions)

    responce['regions'] = [('ALL', _('all')), ] + \
        sorted(responce['regions'], key=lambda x: x['name'])
    responce['address'] = address
    responce['status'] = 'OK'

    return responce


@it_isnt_updating
@accept_ajax
def filter_change_subjects(request):
    """ change regions """
    responce = {'status': 'ERR'}
    country_code = request.GET.get('country')
    if not country_code:
        return responce
    country = get_object_or_none(GeoCountry, iso3=country_code)
    regions = GeoCountryAdminSubject.objects.filter(country_iso=country.iso)
    regions = regions.values('code', 'name').order_by('name')
    responce['regions'] = list(regions)
    responce['regions'] = sorted(responce['regions'], key=lambda x: x['name'])
    responce['status'] = 'OK'

    return responce


@it_isnt_updating
@accept_ajax
def region_caches(request):
    """ list of region caches """
    responce = {'status': 'ERR'}
    country_code = request.GET.get('country')
    request.session['country'] = country_code
    region_ids = request.GET.getlist('region')
    request.session['region'] = region_ids
    type_ids = request.GET.getlist('type')
    request.session['type'] = type_ids
    related_ids = request.GET.getlist('related')
    request.session['related'] = related_ids
    if not country_code:
        return responce

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

    responce['caches'] = cache_list
    responce['rect'] = {
        'lat_min': lat_min or '',
        'lat_max': lat_max or '',
        'lng_min': lng_min or '',
        'lng_max': lng_max or ''
    }
    responce['status'] = 'OK'

    return responce


@it_isnt_updating
def selected_caches(request):
    """ selected caches """
    country_code = request.session.get('country')
    region_ids = request.session.get('region')
    type_ids = request.session.get('type')
    related_ids = request.session.get('related')
    if not country_code:
        pass

    return get_caches(request, country_code, region_ids, type_ids, related_ids)


@it_isnt_updating
def map_import_caches_wpt(request):
    """ import caches as WPT file """
    return HttpResponse('')
    caches = selected_caches(request)

    response_text = render_to_string('caches.wpt', {'caches': caches})
    response = HttpResponse(response_text)
    response['Content-Type'] = 'text'
    response['Content-Disposition'] = f'attachment; filename = geocaches_{int(time.time())}.wpt'
    response['Content-Length'] = str(len(response_text))

    return response


@it_isnt_updating
def map_import_caches_kml(request):
    """ import caches as KML file """
    return HttpResponse('')

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
        desc_tree = etree.SubElement(placemark_tree, 'description')
        desc_tree.text = """
        <a href="%(url)s">Cache %(code)s details</a><br />
        Created by %(author)s<br />&nbsp;<br />
        <table cellspacing="0" cellpadding="0" border="0">
        <tr>
        <td>Type: %(type)s<br />Size: %(size)s</td>
        </tr>
        <tr><td>: Difficulty %(diff)s<br />Terrain: %(terr)s</td></tr>
        </table>
        """ % {
            'url': cache.url, 'code': cache.code,
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
        coord_tree.text = f'{cache.longitude_degree},{cache.latitude_degree}'

    response_text = f'<?xml version="1.0" encoding="utf-8"?>{etree.tostring(root_tree).decode("utf-8")}'
    response = HttpResponse(response_text)
    response['Content-Type'] = 'text/xml'
    response['Content-Disposition'] = f'attachment; filename = geocaches_{int(time.time())}.kml'
    response['Content-Length'] = str(len(response_text))

    return response


@it_isnt_updating
@geocacher_su
def geocaching_su_personal_statistics(request):
    """ personal statistics """
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
    """ statistics for founding my caches """
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
    """ statistics for caches found by me """
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
    """ found caches by regions """
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
    sql = f"""
        select c.iso, cs.code, count(l.id) as cnt
        from log_seek_cach l
        left join cach on l.cach_pid = cach.pid
        left join geo_country_subject cs on (cach.admin_code=cs.code and cach.country_code=cs.country_iso)
        left join geo_country c on cach.country_code=c.iso
        where cach.pid is not null and
              l.cacher_uid={geocacher.uid} and
              cs.code is not null and
              cs.code <> '777' and
              cs.country_iso IN
              ('RU', 'UA', 'BY', 'KZ', 'LT',
               'LV', 'EE', 'MD', 'AZ', 'AM',
               'GE', 'UZ', 'KG', 'TM', 'TJ')
        group by c.iso, cs.code
        having cnt > 0
        """
    for item in iter_sql(sql):
        regions.append({
            'iso': item[0],
            'code': item[1],
            'count': item[2],
        })

    for my_region in regions:
        for region in all_regions:
            if region['iso'] == my_region['iso'] and region['code'] == my_region['code']:
                region['count'] = my_region['count']

    countries = []
    regions = []
    count = 0
    regions_count = 0
    country = None
    for region in all_regions:
        if region['country_name'] != country:
            if country:
                countries.append({
                    'country': country,
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
    countries.append({
        'country': country,
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
    """ personal charts """
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
        sql = f"""
        SELECT cach.type_code, COUNT(l.id) as cnt
        FROM log_seek_cach as l
             LEFT JOIN cach ON l.cach_pid=cach.pid
        WHERE l.cacher_uid={geocacher.uid} AND cach.pid IS NOT NULL
        GROUP BY cach.type_code
        ORDER BY cnt desc
        """

        for item in iter_sql(sql):
            cache_table.append({
                'type': item[0],
                'description': GEOCACHING_SU_CACH_TYPES.get(item[0]) or 'undefined',
                'count': item[1],
                'percent': float(item[1]) / caches_count * 100})

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

        sql = f"""
        SELECT YEAR(found_date) as year_, COUNT(l.id) as cnt
        FROM log_seek_cach as l
        WHERE l.cacher_uid={geocacher.uid}
        GROUP BY YEAR(found_date)
        """

        years = {}
        for item in iter_sql(sql):
            years[item[0]] = item[1]
        found_years = []
        counter = first_year
        while counter <= year_:
            found_years.append(
                {'count': years.get(counter) or 0,
                 'year': counter})
            counter += 1

        # CREATED
        caches_count = stat.created_count or 1
        sql = f"""
        SELECT cach.type_code, COUNT(l.id) as cnt
        FROM log_create_cach as l
             LEFT JOIN cach ON l.cach_pid=cach.pid
        WHERE l.author_uid={geocacher.uid} AND cach.pid IS NOT NULL
        GROUP BY cach.type_code
        ORDER BY cnt desc
        """

        for item in iter_sql(sql):
            created_table.append({
                'type': item[0],
                'description': GEOCACHING_SU_CACH_TYPES.get(item[0]) or 'undefined',
                'count': item[1],
                'percent': float(item[1]) / caches_count * 100})

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

        sql = f"""
        SELECT YEAR(created_date) as year_, COUNT(l.id) as cnt
        FROM log_create_cach as l
        WHERE l.author_uid={geocacher.uid}
        GROUP BY YEAR(created_date)
        """

        years = {}
        for item in iter_sql(sql):
            years[item[0]] = item[1]
        created_years = []
        counter = first_year or year_
        while counter <= year_:
            created_years.append(
                {'count': years.get(counter) or 0,
                 'year': counter})
            counter += 1
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
    """ import caches as GPX file """
    return HttpResponse('')


def coordinate_converter(request):
    """ converter for coordinates """
    return render(
        request,
        'Geocaching_su/coordinate_converter.html',
        {})


@it_isnt_updating
def geocacher_rate_real_current(request):
    """ rate of geocachers, real, current year """
    qs = GeocacherStat.objects.all().order_by(
        '-tr_curr_created_count', '-tr_curr_found_count')
    title = _("%s. Real caches") % datetime.now().year

    the_table = GeocacherRateRealCurrYearTable(qs)
    RequestConfig(
        request, paginate={"per_page": settings.ROW_PER_PAGE}).configure(the_table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {'table': the_table,
         'title': title,
         'curr_year': datetime.now().year,
         'last_year': datetime.now().year - 1
         })


@it_isnt_updating
def geocacher_search_rating(request):
    """ rate of geocachers, search """
    qs = GeocacherSearchStat.objects.all()
    qs = qs.select_related('geocacher').filter(points__gt=0)
    qs = qs.order_by('-points')

    f = GeocacherStatFilter(request.GET, queryset=qs)

    the_table = GeocacherSearchTable(f.qs)
    RequestConfig(
        request,
        paginate={"per_page": settings.ROW_PER_PAGE}).configure(the_table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {
            'table': the_table,
            'filter': f,
            'title': _("Search rating. All years"),
            'curr_year': datetime.now().year,
            'last_year': datetime.now().year - 1
        })


@it_isnt_updating
def geocacher_search_rating_current(request):
    """ rate of geocachers, search, current year """
    qs = GeocacherSearchStat.objects.all()
    qs = qs.select_related('geocacher').filter(year_points__gt=0)
    qs = qs.order_by('-year_points')

    f = GeocacherStatFilter(request.GET, queryset=qs)

    the_table = GeocacherSearchYearTable(f.qs)
    RequestConfig(
        request,
        paginate={"per_page": settings.ROW_PER_PAGE}).configure(the_table)

    return render(
        request,
        'Geocaching_su/dt2-geocacher_list.html',
        {
            'table': the_table,
            'filter': f,
            'title': _("Search rating. Current year %s") % datetime.now().year,
            'curr_year': datetime.now().year,
            'last_year': datetime.now().year - 1
        })


@accept_ajax
def ajax_converter(request):
    """ converter driven by ajax """
    def minutes_from_degree(degree):
        """ minutes from degree"""
        minutes = degree - int(degree)
        return minutes * 60

    def seconds_from_degree(degree):
        """ seconds from degree"""
        minutes = degree - int(degree)
        minutes = minutes * 60
        seconds = minutes - int(minutes)

        return seconds * 60

    responce = {
        'status': 'ERR',
        'dms': '',
        'd': '',
        'dm': ''
    }

    string = request.POST.get('input')

    degree = None
    degree = get_degree(string)

    if degree is None:
        return responce

    minutes = minutes_from_degree(degree)
    seconds = seconds_from_degree(degree)
    responce['d'] = f'{degree:.6f}'
    responce['dms'] = f'{int(degree)}° {int(minutes)}\' {seconds:.2f}"'
    responce['dm'] = f"{int(degree)}° {minutes:.3f}\'"

    responce['status'] = 'OK'

    return responce


def distinct_types_list(types):
    """ list of cache types """
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
    """ get ISO by known ISO3 """
    if iso3 and len(iso3) == 3:
        country = get_object_or_none(
            GeoCountry,
            iso3=iso3)
        if country:
            return country.iso


def get_nickname(request):
    """ get user nickname """
    nickname = request.session.get('login_as')
    if not nickname:
        nickname = request.user.gpsfunuser.geocaching_su_nickname
    if nickname:
        nickname = nickname.strip()
    return nickname


def get_list_of_counts(data, all_types):
    """ get list of counts from the data """
    types = []
    for cache_type in all_types:
        types.append(data.get(cache_type) or 0)
    return types


def row_by_date(data, year, month):
    """ row by date """
    if not data or not year or not month:
        return None

    for item in data:
        if item.get('year') == year and item.get('month') == month:
            return item
    return None


def yearmonth(year, month):
    """ year and month as single integer value """
    return year * 100 + month


def get_found_statistics(request, i_found=False):
    """ statistics of found caches """
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
    """ activity of geocacher per month """
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
        if yearmonth(year2, month2) < yearmonth(year_, month_):
            year_ = year2
            month_ = month2

    # init data table
    data_table = []
    field1 = 'found'
    field2 = 'created'
    if creation:
        field1 = 'trad'
        field2 = 'virt'
    for the_year in range(curr_year - year_ + 1):
        for the_month in range(12):
            if yearmonth(the_year + year_, the_month + 1) >= yearmonth(year_, month_) and \
               yearmonth(the_year + year_, the_month + 1) <= yearmonth(curr_year, curr_month):
                data_table.append({
                    'year': the_year + year_,
                    'month': the_month + 1,
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
    """ get caches """
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
        if 'all' not in type_ids:
            caches = caches.filter(type_code__in=type_ids)
    if related_ids:
        user_pid = request.session.get('pid')
        if 'all' not in related_ids and user_pid:
            if 'mine' in related_ids:
                caches = caches.filter(created_by=user_pid)
            if 'vis' in related_ids:
                caches = caches.extra(
                    where=[f"pid IN (SELECT cach_pid FROM log_seek_cach WHERE cacher_uid={user_pid})"])
            if 'notvis' in related_ids:
                caches = caches.exclude(created_by=user_pid)
                caches = caches.extra(
                    where=[f"pid NOT IN (SELECT cach_pid FROM log_seek_cach WHERE cacher_uid={user_pid})"])
    return caches


def geocacher_year_statistics(geocacher, year_, last_year, creation=False):
    """ year statistics for the geocacher """
    counter_current_year = \
        get_geocacher_year_statistics(
            RAWSQL['geocacher_one_year_created_by_months']
            if creation else RAWSQL['geocacher_one_year_found_by_months'],
            year_, geocacher)

    counter_last_year = \
        get_geocacher_year_statistics(
            RAWSQL['geocacher_one_year_created_by_months']
            if creation else RAWSQL['geocacher_one_year_found_by_months'],
            last_year, geocacher)

    sql = RAWSQL['first_year_created'] if creation else RAWSQL['first_year_found']
    sql = sql % (geocacher.uid)

    first_year = sql2val(sql)

    return counter_current_year, counter_last_year, first_year


def create_chart(
        data1, data2, labels, name1='', name2='', width=700, height=250):
    """ create the chart with parameters """

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


def get_personal_caches_bar(request, sql):
    """ bar chart for the geocacher """
    nickname = get_nickname(request)
    geocacher = get_object_or_404(Geocacher, nickname=nickname)

    sql = sql % geocacher.uid
    chart = get_geocacher_bar_chart(sql, 200, 150)

    return chart


def cach_rate(request, order_by, table_class, template):
    """ Caches statistics """
    qs = CachStat.objects.all().order_by(order_by)
    source = datasource.QSDataSource(qs)

    rate_table = table_class('cach_search')
    the_controller = GPSFunTableController(
        rate_table,
        source,
        request,
        settings.ROW_PER_PAGE)
    the_controller.kind = 'cache_rate'
    the_controller.allow_manage_profiles = False

    result = the_controller.process_request()

    if result:
        return result

    return render(
        request,
        template,
        {
            'table': the_controller,
        })


def geocaching_su_profile(request, nickname):
    """ profile of geocachers """
    geocacher = get_object_or_none(Geocacher, nickname=nickname)
    if geocacher:
        url = f'https://geocaching.su/profile.php?uid={geocacher.uid}'
    else:
        url = 'https://geocaching.su/?pn=108'
    return HttpResponseRedirect(url)


def get_controller(the_table, source, request, rows_per_page):
    """ get table controller """
    the_controller = GPSFunTableController(the_table, source, request, rows_per_page)
    the_controller.kind = 'geocacher_rate'
    the_controller.allow_manage_profiles = False

    return the_controller


def get_geocacher_year_statistics(sql, year, geocacher):
    """ get statistics for geocacher, one year """
    sql = RAWSQL['geocacher_one_year_created_by_months']
    sql = sql % (geocacher.uid, year)

    months = {}
    for item in iter_sql(sql):
        months[item[0]] = item[1]
    counters = []
    for month in range(12):
        counters.append(
            {'count': months.get(month + 1) or 0,
             'month': month + 1})
    return counters


def get_piechart(sql, width, height):
    """ create pie chart """
    colors = ['#f83c38', '#e61a16', '#1a7ddd', '#3c9fff', '#9dd872', '#d67b31', '#7bb650', '#f89d53']
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
    """ get bar chart for geoacher """
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
    """ get data for the chart """
    data = []
    legend = []
    summ = 0
    for item in iter_sql(sql):
        summ += item[1]
        data.append(summ)
        legend.append(item[0])
    return data, legend, summ


def created_caches_per_year():
    """ get count of created caches per year """
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
