"""
There are Admin Classes to present in admin interface objects
related to geocaching statistics
"""

from django.contrib import admin
from gpsfun.main.GeoCachSU.models import (
    Geocacher, Cach, LogCreateCach, LogSeekCach, LogRecommendCach,
    CacheDescription, CacheLog, CachStat,
    GeocacherStat, GeocacherSearchStat)


class GeocacherAdmin(admin.ModelAdmin):
    list_display = (
        'uid', 'nickname', 'register_date', 'name', 'birstday',
        'sex', 'country', 'town', 'oblast',
        'created_caches', 'found_caches', 'last_login',
        'forum_posts', 'country_iso3', 'admin_code'
    )
    search_fields = ('nickname', 'name', 'uid')
    ordering = ('id', )

admin.site.register(Geocacher, GeocacherAdmin)


class CachAdmin(admin.ModelAdmin):
    list_display = (
        'pid', 'code', 'type_code', 'name', 'created_date',
        'author',
        'country', 'town', 'oblast',
        'latitude', 'longitude',
        'grade', 'country_code', 'admin_code',
        'country_name', 'oblast_name'
    )
    search_fields = ('code', 'name', 'pid')
    ordering = ('id', )

admin.site.register(Cach, CachAdmin)


class LogCreateCachAdmin(admin.ModelAdmin):
    list_display = (
        'author_uid', 'cach_pid', 'created_date', 'coauthor'
    )
    search_fields = ('author_uid', 'cach_pid')
    ordering = ('id', )

admin.site.register(LogCreateCach, LogCreateCachAdmin)


class LogSeekCachAdmin(admin.ModelAdmin):
    list_display = (
        'cacher_uid', 'cach_pid', 'found_date', 'grade'
    )
    search_fields = ('cacher_uid', 'cach_pid')
    ordering = ('id', )

admin.site.register(LogSeekCach, LogSeekCachAdmin)


class LogRecommendCachAdmin(admin.ModelAdmin):
    list_display = (
        'cacher_uid', 'cach_pid'
    )
    search_fields = ('cacher_uid', 'cach_pid')
    ordering = ('id', )

admin.site.register(LogRecommendCach, LogRecommendCachAdmin)


class CachStatAdmin(admin.ModelAdmin):
    list_display = (
        'geocacher', 'cach', 'cach_pid', 'recommend_count',
        'found_count', 'rank', 'points'
    )
    search_fields = ('cach_pid', )
    raw_id_fields = ('geocacher', 'cach')
    ordering = ('id', )

admin.site.register(CachStat, CachStatAdmin)


class GeocacherStatAdmin(admin.ModelAdmin):
    list_display = (
        'geocacher', 'uid', 'created_count', 'found_count',
        'curr_found_count', 'curr_created_count',
        'last_found_count', 'last_created_count',
        'av_grade', 'av_his_cach_grade',
        'country', 'region',
        'vi_found_count', 'vi_created_count',
        'vi_curr_found_count', 'vi_curr_created_count',
        'vi_last_found_count', 'vi_last_created_count',
        'tr_found_count', 'tr_created_count',
        'tr_curr_found_count', 'tr_curr_created_count',
        'tr_last_found_count', 'tr_last_created_count',
    )
    search_fields = ('pid', )
    raw_id_fields = ('geocacher', )
    ordering = ('id', )

admin.site.register(GeocacherStat, GeocacherStatAdmin)


class GeocacherSearchStatAdmin(admin.ModelAdmin):
    list_display = (
        'geocacher', 'geocacher_uid', 'points', 'year_points',
        'country', 'region'
    )
    search_fields = ('geocacher_uid', )
    raw_id_fields = ('geocacher', )
    ordering = ('id', )

admin.site.register(GeocacherSearchStat, GeocacherSearchStatAdmin)

