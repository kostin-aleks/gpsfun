from gpsfun.main.GeoCachSU.models import Cach, CachStat, GEOCACHING_SU_CACH_TYPES
#from core.Geoname.models import GeoCountry
from django.utils.translation import ugettext_lazy as _
from gpsfun.DjHDGutils.dbutils import iter_sql

def _populate(model, field, request, filter=None, exclude=None, add_empty=False):
    """
    filter={'field': value,
            'field__range': [value1, value]}
    """

    field.choices = []

    if add_empty:
        field.choices.append(('','-------'))

    qs = model.objects.all().order_by('name')
    if filter:
        qs = qs.filter(**filter)
    if exclude:
        qs = qs.exclude(**exclude)

    for item in qs:
        field.choices.append((item.id, item.name))


def populate_cach_type(field, *kargs, **kwargs):
    field.choices = []
    field.choices.append(('ALL',_('all')))
    field.choices.append(('REAL',_('all real')))
    field.choices.append(('UNREAL',_('all unreal')))

    sql = """
    SELECT DISTINCT type_code
    FROM cach
    """

    for item in iter_sql(sql):
        field.choices.append((item[0], GEOCACHING_SU_CACH_TYPES.get(item[0], '')))

def populate_country(field, *kargs, **kwargs):
    field.choices = []
    field.choices.append(('ALL',_('all')))

    qs = CachStat.objects.all()
    qs = qs.values_list('cach__country_code', 'cach__country_name')
    qs = qs.distinct().order_by('cach__country_name')
    l = []
    for item in qs:
        l.append((item[0], _(item[1])))

    field.choices = field.choices + sorted(l, key=lambda x: x[1])

def populate_country_iso3(field, *kargs, **kwargs):
    field.choices = []
    field.choices.append(('',_('all')))

    sql = """
    SELECT DISTINCT c.iso3, c.name
    FROM geocacher gc
    LEFT JOIN geo_country as c ON gc.country_iso3=c.iso3
    WHERE gc.found_caches > 0
    HAVING c.iso3 IS NOT NULL
    ORDER BY c.name
    """
    l = []
    for item in iter_sql(sql):
        l.append((item[0], _(item[1])))

    field.choices = field.choices + sorted(l, key=lambda x: x[1])

def populate_countries_iso3(field, *kargs, **kwargs):
    field.choices = []
    field.choices.append(('ALL',_('all')))

    sql = """
    SELECT DISTINCT c.iso3, c.name
    FROM cach
    LEFT JOIN geo_country as c ON cach.country_code=c.iso
    HAVING c.iso3 IS NOT NULL
    ORDER BY c.name
    """
    l = []
    for item in iter_sql(sql):
        l.append((item[0], _(item[1])))

    field.choices = field.choices + sorted(l, key=lambda x: x[1])

def populate_subjects(field, *kargs, **kwargs):
    field.choices = []
    field.choices.append(('ALL',_('all')))
    sql = """
    SELECT gcs.code, gcs.name
    FROM geo_country_subject gcs
    LEFT JOIN geo_country gc ON gcs.country_iso=gc.iso
    WHERE gc.iso3 = '%s'
    ORDER BY gcs.name
    """ % kwargs.get('selected_country_iso','')

    l = []
    for item in iter_sql(sql):
        l.append((item[0], _(item[1])))

    field.choices = field.choices + sorted(l, key=lambda x: x[1])
