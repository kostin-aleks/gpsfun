"""
models for main
"""
from datetime import datetime
from django.db import models
from gpsfun.main.db_utils import get_object_or_none
from gpsfun.main.GeoCachSU.models import Geocacher, Cach


class UpdateType:
    """ UpdateType """
    gcsu = 'gcsu'
    gcsu_caches = 'gcsu_caches'
    gcsu_new_caches = 'gcsu_new_caches'
    gcsu_casherstat = 'gcsu_casherstat'
    gcsu_cashstat = 'gcsu_cashstat'
    gcsu_geocachers = 'gcsu_geocachers'
    gcsu_new_geocachers = 'gcsu_new_geocachers'
    gcsu_logs_found = 'gcsu_logs_found'
    gcsu_logs_created = 'gcsu_logs_created'
    gcsu_logs_recommended = 'gcsu_logs_recommended'
    gcsu_new_logs_created = 'gcsu_new_logs_created'
    gcsu_new_logs_recommended = 'gcsu_new_logs_recommended'
    gcsu_new_logs_found = 'gcsu_new_logs_found'
    gcsu_location = 'gcsu_location'
    gcsu_logs = 'gcsu_logs'
    gcsu_patch = 'gcsu_patch'
    gcsu_rating = 'gcsu_rating'
    kret = 'kret'
    map = 'map'
    map_gcsu_caches = 'map_gcsu_caches'
    map_occom_caches = 'map_occom_caches'
    map_occz_caches = 'map_occz_caches'
    map_ocde_caches = 'map_ocde_caches'
    map_ocnl_caches = 'map_ocnl_caches'
    map_ocpl_caches = 'map_ocpl_caches'
    map_ocuk_caches = 'map_ocuk_caches'
    map_ocus_caches = 'map_ocus_caches'
    map_opencaching = 'map_opencaching'
    map_set_location = 'map_set_location'
    map_shukach = 'map_shukach'
    updated_gcsu_cac = 'updated_gcsu_cac'
    upd_gcsu_cachers = 'upd_gcsu_cachers'
    upd_gcsu_caches = 'upd_gcsu_caches'
    set_caches_locations = 'set_caches_locations'
    set_geocachers_locations = 'set_geocachers_locations'
    geocacher_patch = 'geocacher_patch'
    geocacher_statistics = 'geocacher_statistics'
    cache_statistics = 'cache_statistics'
    set_caches_authors = 'set_caches_authors'
    search_statistics = 'search_statistics'
    gcsu_check_data = 'gcsu_check_data'
    geokrety_imported = 'geokrety_imported'
    geokrety_updated = 'geokrety_updated'


class LogUpdate(models.Model):
    """ LogUpdate """
    update_type = models.CharField(max_length=32)
    update_date = models.DateTimeField(blank=True, null=True)
    message = models.CharField(max_length=255)

    class Meta:
        db_table = 'log_update'

    def __str__(self):
        return f'Update {self.update_type} on {self.update_date}'


class Variable(models.Model):
    """ Variable """
    name = models.CharField(max_length=64)
    value = models.CharField(max_length=128)

    class Meta:
        db_table = 'variables'

    def __str__(self):
        return f'{self.name} -> {self.value}'


class LogAPI(models.Model):
    """ LogAPI """
    method = models.CharField(max_length=32)
    update_date = models.DateTimeField(blank=True, null=True)
    IP = models.CharField(max_length=16)

    class Meta:
        db_table = 'log_api'

    def __str__(self):
        return f'API request {self.method} at {self.update_date}'


def switch_off_status_updated():
    """ switch off the status 'updated' """
    updated = get_object_or_none(Variable, name='updated')
    if updated is None:
        return False
    if updated.value != 'successful':
        return False
    updated.value = ''
    updated.save()

    return True


def switch_on_status_updated():
    """ switch on the status 'updated' """
    updated = get_object_or_none(Variable, name='updated')
    if updated is None:
        return False

    updated.value = 'successful'
    updated.save()

    return True


def log(type_, message):
    """ log """
    log_ = LogUpdate(update_type=type_, message=message, update_date=datetime.now())
    log_.save()


def log_api(method, IP):
    """ log api """
    log_ = LogAPI(method=method, IP=IP, update_date=datetime.now())
    log_.save()


class LogCheckData(models.Model):
    """ LogCheckData """
    geocacher_count = models.IntegerField(blank=True, null=True)
    geocacher_wo_country_count = models.IntegerField(blank=True, null=True)
    geocacher_wo_region_count = models.IntegerField(blank=True, null=True)
    cache_count = models.IntegerField(blank=True, null=True)
    cache_wo_country_count = models.IntegerField(blank=True, null=True)
    cache_wo_region_count = models.IntegerField(blank=True, null=True)
    cache_wo_author_count = models.IntegerField(blank=True, null=True)
    checking_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'log_check_data'

    def __str__(self):
        return f'Cheked data at {self.checking_date}'

    @classmethod
    def check_data(cls):
        """ check data """
        cls.objects.create(
            geocacher_count=Geocacher.objects.all().count(),
            geocacher_wo_country_count=Geocacher.objects.filter(
                country_iso3__isnull=True).count(),
            geocacher_wo_region_count=Geocacher.objects.filter(
                admin_code__isnull=True).count(),
            cache_count=Cach.objects.all().count(),
            cache_wo_country_count=Cach.objects.filter(
                country_code__isnull=True).count(),
            cache_wo_region_count=Cach.objects.filter(
                admin_code__isnull=True).count(),
            cache_wo_author_count=Cach.objects.filter(
                author__isnull=True).count(),
            checking_date=datetime.now()
        )
