"""
Models for GeoName
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from gpsfun.DjHDGutils.dbutils import get_object_or_none


RU_CHARS = u"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ -"
UA_CHARS = u"ЇІЄ'"
RUUA_CHARS = RU_CHARS + UA_CHARS
SET_RUUA_UPPER = set(RUUA_CHARS)

SET_RU_UPPER = set(RU_CHARS)
SET_RU = SET_RU_UPPER | set(RU_CHARS.lower())
SET_UA_UPPER = set(RU_CHARS + UA_CHARS)
SET_UA = SET_UA_UPPER | set((RU_CHARS + UA_CHARS).lower())


class GeoCity(models.Model):
    """ GeoCity """
    geonameid = models.IntegerField(default=0)
    name = models.CharField(max_length=200, blank=True, null=True)
    asciiname = models.CharField(max_length=200, blank=True, null=True)
    alternatenames = models.CharField(max_length=4000, blank=True, null=True)
    latitude = models.FloatField(default=0, null=True)
    longitude = models.FloatField(default=0, null=True)
    fclass = models.CharField(max_length=1, blank=True, null=True)
    fcode = models.CharField(max_length=10, blank=True, null=True)

    country = models.CharField(max_length=2, null=True, db_index=True)
    cc2 = models.CharField(max_length=60, blank=True, null=True)
    admin1 = models.CharField(
        max_length=20, null=True, blank=True, db_index=True)
    admin2 = models.CharField(max_length=80, null=True, blank=True)
    admin3 = models.CharField(max_length=20, null=True, blank=True)
    admin4 = models.CharField(max_length=20, null=True, blank=True)
    population = models.IntegerField(null=True)
    elevation = models.IntegerField(null=True)
    gtopo30 = models.IntegerField(null=True)
    timezone = models.CharField(max_length=40, null=True, blank=True)
    moddate = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'geo_city'

    def __str__(self):
        return f'{self.geonameid}/{self.name}/{self.country}/{self.admin1}'

    @property
    def strana(self):
        """ Geocity country """
        return geocountry_by_code(self.country)

    def country_name(self):
        """ Geocity country name """
        if self.strana and self.strana.name:
            return self.strana.name
        return ''

    @property
    def region(self):
        """ Geocity region """
        return get_object_or_none(
            GeoCountryAdminSubject,
            country_iso=self.country,
            code=self.admin1)

    def region_name(self):
        """ Geocity region name """
        if self.region and self.region.name:
            return self.region.name
        return ''

    def address_string(self):
        """ geocity address string """
        return f'{self.country_name()}, {self.region_name()}, {self.name or ""}'

    def localized_name(self, location):
        """ geocity localized name """
        names = self.alternatenames.split(',')
        city_name = self.asciiname or self.name
        if location and location == 'ru':
            ru_variants = []
            ua_variants = []
            for name in names:
                aset = set(name.strip())
                if aset:
                    if aset.issubset(SET_RU):
                        ru_variants.append(name)
                    elif aset.issubset(SET_UA):
                        ua_variants.append(name)

            if ru_variants:
                city_name = ru_variants[-1]
            elif ua_variants:
                city_name = ua_variants[-1]

            set_city_name = set(city_name)
            if set_city_name and set_city_name.issubset(SET_UA_UPPER):
                city_name = city_name[0] + city_name[1:].lower()

        return city_name


class GeoCountry(models.Model):
    """ GeoCountry """
    geoname_id = models.IntegerField(default=0, db_index=True)
    iso = models.CharField(max_length=2, db_index=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    capital = models.CharField(max_length=128, blank=True, null=True)
    iso3 = models.CharField(max_length=3, db_index=True)
    iso_num = models.IntegerField(db_index=True)
    fips = models.CharField(max_length=2, blank=True, null=True)
    area_sqkm = models.IntegerField(blank=True, null=True)
    population = models.IntegerField(blank=True, null=True)
    continent = models.CharField(max_length=2)
    tld = models.CharField(max_length=6, blank=True, null=True)
    currency_code = models.CharField(
        max_length=3, blank=True, null=True, db_index=True)
    currency_name = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'geo_country'

    def __str__(self):
        return f'{self.iso3}-{self.name}'

    def languages(self):
        """ languages """
        return GeoCountryLanguage.objects.filter(country_iso3=self.iso3)

    def neighbour(self):
        """ neighbour """
        return GeoCountryNeighbour.objects.filter(country_iso3=self.iso3)


class GeoCountryLanguage(models.Model):
    """ GeoCountryLanguage """
    country_iso3 = models.CharField(max_length=3, db_index=True)
    lang_code = models.CharField(max_length=10, db_index=True)

    class Meta:
        db_table = 'geo_country_language'

    def __str__(self):
        return f'{self.country_iso3}-{self.lang_code}'


class GeoCountryNeighbour(models.Model):
    """ GeoCountryNeighbour """
    country_iso3 = models.CharField(max_length=3, db_index=True)
    neighbour_iso = models.CharField(max_length=2, db_index=True)

    class Meta:
        db_table = 'geo_country_neighbour'

    def __str__(self):
        return f'{self.country_iso3}-{self.neighbour_iso}'


class GeoCountryAdminSubject(models.Model):
    """ GeoCountryAdminSubject """
    geoname_id = models.IntegerField(default=0, db_index=True)
    country_iso = models.CharField(max_length=2, db_index=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    code = models.CharField(max_length=10, db_index=True)

    class Meta:
        db_table = 'geo_country_subject'

    def __str__(self):
        return f'{self.country_iso}-{self.code}/{self.name}'


class GeoRUSSubject(models.Model):
    """ GeoRUSSubject """
    geoname_id = models.IntegerField(default=0)
    country_iso = models.CharField(max_length=2)
    name = models.CharField(max_length=128, blank=True, null=True)
    code = models.CharField(max_length=10)
    ascii_name = models.CharField(max_length=128, blank=True, null=True)
    iso_3166_2_code = models.CharField(max_length=16)
    gai_code = models.CharField(max_length=32)

    class Meta:
        db_table = 'geo_russia_subject'

    def __str__(self):
        return f'{self.country_iso}-{self.code}/{self.ascii_name}'


class GeoUKRSubject(models.Model):
    """ GeoUKRSubject """
    geoname_id = models.IntegerField(default=0)
    country_iso = models.CharField(max_length=2)
    name = models.CharField(max_length=128, blank=True, null=True)
    code = models.CharField(max_length=10)
    ascii_name = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'geo_ukraine_subject'

    def __str__(self):
        return f'{self.country_iso}-{self.code}/{self.ascii_name}'


def country_by_code(country_code):
    """ get country by code """
    country = geocountry_by_code(country_code)
    return country.name if country else ''


def geocountry_by_code(country_code):
    """ get geocountry by code """
    if country_code is None:
        return None
    if len(country_code) == 2:
        country = GeoCountry.objects.filter(iso=country_code)
    elif len(country_code) == 3:
        country = GeoCountry.objects.filter(iso3=country_code)
    else:
        country = None
    if country and country.count() == 1:
        return country[0]
    return None


def region_by_code(country_code, region_codes):
    """ get region by code """
    region_code = ''
    if len(region_codes):
        region_code = region_codes[0]
    subject = GeoCountryAdminSubject.objects.filter(country_iso=country_code,
                                                 code=region_code)
    return subject[0].name if subject.count() else ''


def country_iso_by_iso3(iso3):
    """ get country ISO by ISO3 """
    countries = GeoCountry.objects.filter(iso3=iso3)
    if countries.count() == 1:
        return countries[0].iso
    return None


def populate_country_subject_city(
    field_country, field_subject, field_city, city):
    """ populate country subject city """
    field_country.choices = []
    field_country.choices.append(('NONE', _('-- choose country --')))

    countries = GeoCountry.objects.all().values_list('iso', 'name')

    lst = []
    for country in countries:
        lst.append((country[0], _(country[1])))

    field_country.choices = field_country.choices + sorted(lst, key=lambda x: x[1])

    field_subject.choices = []
    field_subject.choices.append(('NONE',_('-- choose admin subject --')))

    if city:
        subjects = GeoCountryAdminSubject.objects.filter(country_iso=city.country).values_list('code', 'name')

        lst = []
        for subject in subjects:
            lst.append((subject[0], _(subject[1])))

        field_subject.choices = field_subject.choices + sorted(lst, key=lambda x: x[1])

    field_city.choices = []
    field_city.choices.append(('NONE', _('-- choose city --')))
    if city:
        cities = GeoCity.objects.filter(country=city.country, admin1=city.admin1)
        lst = [(city.geonameid,
              city.localized_name(translation.get_language())) for city in cities]

        field_city.choices = field_city.choices + sorted(lst, key=lambda x: x[1])

    return field_country, field_subject, field_city


def get_city_by_geoname(city_geoname):
    """ get city by geoname """
    if city_geoname:
        return get_object_or_none(GeoCity, geonameid=city_geoname)
    return None
