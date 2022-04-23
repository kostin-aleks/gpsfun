"""
utils for main.GeoCachSU
"""
from django.utils.translation import ugettext_lazy as _
from gpsfun.main.GeoCachSU.models import CachStat, GEOCACHING_SU_CACH_TYPES
from gpsfun.main.db_utils import iter_sql


def _populate(model, field, request, filter_=None, exclude=None, add_empty=False):
    """
    filter={'field': value,
            'field__range': [value1, value]}
    """

    field.choices = []

    if add_empty:
        field.choices.append(('','-------'))

    qs = model.objects.all().order_by('name')
    if filter_:
        qs = qs.filter(**filter_)
    if exclude:
        qs = qs.exclude(**exclude)

    for item in qs:
        field.choices.append((item.id, item.name))


def populate_cach_type(field, *kargs, **kwargs):
    """ populate cache types """
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


def cache_types():
    """ list of cache types """
    choices = []
    sql = """
    SELECT DISTINCT type_code
    FROM cach
    """
    for item in iter_sql(sql):
        choices.append((item[0], GEOCACHING_SU_CACH_TYPES.get(item[0], '')))

    return choices


def populate_country(field, *kargs, **kwargs):
    """ populate country """
    field.choices = []
    field.choices.append(('ALL', _('all')))

    qs = CachStat.objects.all()
    qs = qs.values_list('cach__country_code', 'cach__country_name')
    qs = qs.distinct().order_by('cach__country_name')
    lst = []
    for item in qs:
        lst.append((item[0], _(item[1])))

    field.choices = field.choices + sorted(lst, key=lambda x: x[1])


def countries_iso():
    """ list of countries """
    choices = []
    # choices.append(('', _('all')))

    qs = CachStat.objects.exclude(cach__country_code__isnull=True)
    qs = qs.values_list('cach__country_code', 'cach__country_name')
    qs = qs.distinct().order_by('cach__country_name')
    lst = []
    for item in qs:
        lst.append((item[0], _(item[1])))

    return choices + sorted(lst, key=lambda x: x[1])


def countries_iso3():
    """ list of countries """
    choices = []

    sql = """
    SELECT DISTINCT c.iso3, c.name
    FROM geocacher gc
    LEFT JOIN geo_country as c ON gc.country_iso3=c.iso3
    WHERE gc.found_caches > 0
    HAVING c.iso3 IS NOT NULL
    ORDER BY c.name
    """
    lst = []
    for item in iter_sql(sql):
        lst.append((item[0], _(item[1])))

    return choices + sorted(lst, key=lambda x: x[1])


def populate_country_iso3(field, *kargs, **kwargs):
    """ populate country """
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
    lst = []
    for item in iter_sql(sql):
        lst.append((item[0], _(item[1])))

    field.choices = field.choices + sorted(lst, key=lambda x: x[1])


def populate_countries_iso3(field, *kargs, **kwargs):
    """ populate countries """
    field.choices = []
    field.choices.append(('ALL',_('all')))

    sql = """
    SELECT DISTINCT c.iso3, c.name
    FROM cach
    LEFT JOIN geo_country as c ON cach.country_code=c.iso
    HAVING c.iso3 IS NOT NULL
    ORDER BY c.name
    """
    lst = []
    for item in iter_sql(sql):
        lst.append((item[0], _(item[1])))

    field.choices = field.choices + sorted(lst, key=lambda x: x[1])


def populate_subjects(field, *kargs, **kwargs):
    """ populate subjects """
    field.choices = []
    field.choices.append(('ALL', _('all')))
    iso3 = kwargs.get('selected_country_iso', '')
    sql = f"""
    SELECT gcs.code, gcs.name
    FROM geo_country_subject gcs
    LEFT JOIN geo_country gc ON gcs.country_iso=gc.iso
    WHERE gc.iso3 = '{iso3}'
    ORDER BY gcs.name
    """

    lst = []
    for item in iter_sql(sql):
        lst.append((item[0], _(item[1])))

    field.choices = field.choices + sorted(lst, key=lambda x: x[1])
