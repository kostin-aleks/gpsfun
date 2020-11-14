from datetime import datetime
from django.db import models

from django.utils.translation import ugettext_lazy as _
from gpsfun.DjHDGutils.dbutils import get_object_or_none
from gpsfun.main.GeoName.models import GeoCountry, GeoCountryAdminSubject, \
     country_iso_by_iso3
from gpsfun.main.db_utils import sql2val

GEOCACHING_SU_CACH_TYPES = {
    'EV': _('Event'),
    'CT': _('Contest'),
    'MS': _('Trad Multi step'),
    'MV': _('Virtual Multi step'),
    'TR': _('Traditional'),
    'VI': _('Virtual'),
    'LT': _('Logical'),
    'LV': _('Logical virtual'),
}

GEOCACHING_SU_REAL_TYPES = ('MS', 'TR', 'LT')
GEOCACHING_SU_UNREAL_TYPES = ('EV', 'CT', 'VI', 'MV', 'LV')
GEOCACHING_SU_ONMAP_TYPES = ('MV', 'MS', 'TR', 'VI', 'LV', 'LT')


class Geocacher(models.Model):
    uid = models.IntegerField(null=True, unique=True)
    nickname = models.CharField(max_length=64)
    name = models.CharField(max_length=128, blank=True, null=True)
    birstday = models.DateTimeField(blank=True, null=True)
    sex = models.CharField(max_length=1, null=True, blank=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    oblast = models.CharField(max_length=64, blank=True, null=True)
    created_caches = models.IntegerField(default=0, null=True)
    found_caches = models.IntegerField(default=0, null=True)
    register_date = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    forum_posts = models.IntegerField(default=0, null=True)
    country_iso3 = models.CharField(max_length=3, blank=True, null=True)
    admin_code = models.CharField(max_length=6, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['uid']),
            models.Index(fields=['nickname']),
        ]
        db_table = u'geocacher'

    def __unicode__(self):
        return u'%s/%s/%s/%s' % (self.id, self.uid, self.name, str(self.nickname).decode('utf-8'))

    def cacher_country(self):
        return get_object_or_none(GeoCountry, iso3=self.country_iso3)

    def cacher_region(self):
        iso = country_iso_by_iso3(self.country_iso3)
        return get_object_or_none(GeoCountryAdminSubject,
                                  country_iso=iso,
                                  code=self.admin_code)

    def statistics(self):
        return get_object_or_none(GeocacherStat, geocacher=self)

    def caching_months(self):
        months = []
        if self.register_date:
            seek_months = LogSeekCach.objects.filter(cacher_uid=self.uid)
            seek_months = seek_months.values_list('found_date', flat=True).distinct()

            for dt in seek_months:
                if not (dt.year, dt.month) in months:
                    months.append((dt.year, dt.month))
            hide_months = LogCreateCach.objects.filter(author_uid=self.uid)
            hide_months = hide_months.values_list('created_date', flat=True).distinct()

            for dt in hide_months:
                if not (dt.year, dt.month) in months:
                    months.append((dt.year, dt.month))

            return len(months)

    def total_months(self):
        #IMPROVE
        if self.register_date:
            return int(round((datetime.now() - self.register_date).days / 30.0))

    def avg_caches_per_month(self):
        sql = """
        SELECT AVG(cnt)
        FROM (
            SELECT YEAR(found_date), MONTH(found_date), COUNT(id) as cnt
            FROM log_seek_cach
            WHERE cacher_uid=%s
            GROUP BY YEAR(found_date), MONTH(found_date)
        ) as tbl
        """ % self.uid
        return sql2val(sql)

    def most_found_one_month(self):
        sql = """
        SELECT MAX(cnt)
        FROM (
            SELECT YEAR(found_date), MONTH(found_date), COUNT(id) as cnt
            FROM log_seek_cach
            WHERE cacher_uid=%s
            GROUP BY YEAR(found_date), MONTH(found_date)
        ) as tbl
        """ % self.uid
        return sql2val(sql)

    def avg_created_caches_per_month(self):
        sql = """
        SELECT AVG(cnt)
        FROM (
            SELECT YEAR(created_date), MONTH(created_date), COUNT(id) as cnt
            FROM log_create_cach
            WHERE author_uid=%s
            GROUP BY YEAR(created_date), MONTH(created_date)
        ) as tbl
        """ % self.uid
        return sql2val(sql)

    def most_created_one_month(self):
        sql = """
        SELECT MAX(cnt)
        FROM (
            SELECT YEAR(created_date), MONTH(created_date), COUNT(id) as cnt
            FROM log_create_cach
            WHERE author_uid=%s
            GROUP BY YEAR(created_date), MONTH(created_date)
        ) as tbl
        """ % self.uid
        return sql2val(sql)

    def latest_found_cache(self):
        last_found = LogSeekCach.objects.filter(cacher_uid=self.uid)
        last_found = last_found.order_by('-found_date')[:1]
        if last_found:
            last_found = last_found[0]
            cache = get_object_or_none(Cach, pid=last_found.cach_pid)
            return {'date': last_found.found_date,
                    'cache': cache, }

    def latest_created_cache(self):
        last_created = LogCreateCach.objects.filter(author_uid=self.uid)
        last_created = last_created.order_by('-created_date')[:1]
        if last_created:
            last_created = last_created[0]
            cache = get_object_or_none(Cach, pid=last_created.cach_pid)
            return {'date': last_created.created_date,
                    'cache': cache, }

    def recommendation_count(self):
        return LogRecommendCach.objects.filter(cacher_uid=self.uid).count()

    def recommendations(self):
        caches = Cach.objects.filter(author=self)
        caches = caches.values_list('pid', flat=True)
        return LogRecommendCach.objects.filter(cach_pid__in=caches)

    def caches_recommendation_count(self):
        caches = Cach.objects.filter(author=self)
        caches = caches.values_list('pid', flat=True)
        return self.recommendations().count()

    def recommended_caches_count(self):
        return self.recommendations().values('cach_pid').distinct().count()

    def ratio_recommended_caches(self):
        recommended = self.recommended_caches_count()
        if self.statistics() and  self.statistics().created_count:
            return float(recommended or 0) / self.statistics().created_count * 100.0

    def seek_milestones(self):
        found = LogSeekCach.objects.filter(cacher_uid=self.uid)
        found = found.order_by('found_date')
        stones = []
        cnt = found.count()
        if cnt:
            stones.append({'idx': 1,
                           'item': found[0]})
            k = 50
            while k <= cnt:
                stones.append({'idx': k,
                               'item': found[k - 1]})
                k += 50

        return stones

    def hide_milestones(self):
        hidden = LogCreateCach.objects.filter(author_uid=self.uid)
        hidden = hidden.order_by('created_date')
        stones = []
        cnt = hidden.count()
        if cnt:
            stones.append({'idx': 1,
                           'item': hidden[0]})
            k = 20
            while k <= cnt:
                stones.append({'idx': k,
                               'item': hidden[k - 1]})
                k += 20

        return stones


class Cach(models.Model):
    pid = models.IntegerField(default=0)
    code = models.CharField(max_length=32)
    type_code = models.CharField(max_length=2)
    name = models.CharField(max_length=128, blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    author = models.ForeignKey(Geocacher, on_delete=models.CASCADE, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    oblast = models.CharField(max_length=64, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    grade = models.FloatField(blank=True, null=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    admin_code = models.CharField(max_length=6, blank=True, null=True)
    country_name = models.CharField(max_length=64, blank=True, null=True)
    oblast_name = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = u'cach'
        indexes = [
            models.Index(fields=['pid']),
            models.Index(fields=['type_code']),
            models.Index(fields=['created_date']),
            models.Index(fields=['country_code']),
            models.Index(fields=['admin_code']),
        ]

    def __unicode__(self):
        return u'%s/%s/%s' % (self.id, self.code, self.name.decode('utf-8'))

    @property
    def latitude_degree(self):
        d = None
        if self.loc_NS_degree is not None:
            d = self.loc_NS_degree + (self.loc_NS_minute or 0) / 60.0
            if self.loc_NS != 'N':
                d = -d
        return d

    @property
    def longitude_degree(self):
        d = None
        if self.loc_EW_degree is not None:
            d = self.loc_EW_degree + (self.loc_EW_minute or 0) / 60.0
            if self.loc_EW != 'E':
                d = -d
        return d

    @property
    def site(self):
        return 'geocaching.su'

    @property
    def url(self):
        return "http://www.geocaching.su/?pn=101&cid=%s" % self.pid

    @property
    def status(self):
        return 'Available'

    @property
    def type_name(self):
        return GEOCACHING_SU_CACH_TYPES[self.type_code] or ''

    @property
    def archived(self):
        return False

    @property
    def size(self):
        return ''


class LogCreateCach(models.Model):
    author_uid = models.IntegerField(default=0)
    cach_pid = models.IntegerField(default=0)
    created_date = models.DateTimeField(blank=True, null=True)
    coauthor = models.BooleanField(default=False)

    class Meta:
        db_table = u'log_create_cach'
        indexes = [
            models.Index(fields=['author_uid']),
            models.Index(fields=['cach_pid']),
            models.Index(fields=['created_date']),
        ]

    def __unicode__(self):
        return u'Created cach %s/%s by %s' % (
            self.cach_pid, self.created_date, self.author_uid)

    def cache(self):
        return get_object_or_none(Cach, pid=self.cach_pid)


class LogSeekCach(models.Model):
    cacher_uid = models.IntegerField(default=0)
    cach_pid = models.IntegerField(default=0)
    found_date = models.DateTimeField(blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = u'log_seek_cach'
        indexes = [
            models.Index(fields=['cacher_uid']),
            models.Index(fields=['cach_pid']),
            models.Index(fields=['found_date']),
        ]

    def __unicode__(self):
        return u'Found cach %s/%s by %s' % (
            self.cach_pid, self.found_date, self.cacher_uid)

    def cache(self):
        return get_object_or_none(Cach, pid=self.cach_pid)


class LogRecommendCach(models.Model):
    cacher_uid = models.IntegerField(default=0)
    cach_pid = models.IntegerField(default=0)

    class Meta:
        db_table = u'log_recommend_cach'
        indexes = [
            models.Index(fields=['cacher_uid']),
            models.Index(fields=['cach_pid']),
        ]

    def __unicode__(self):
        return u'Recommend cach %s by %s' % (self.cach_pid, self.cacher_uid)


class CacheDescription(models.Model):
    cache = models.ForeignKey(Cach, on_delete=models.CASCADE)
    cache_pid = models.IntegerField(default=0)
    terrain_description = models.TextField(blank=True, null=True)
    cache_description = models.TextField(blank=True, null=True)
    virtual_part = models.TextField(blank=True, null=True)
    cache_content = models.TextField(blank=True, null=True)

    class Meta:
        db_table = u'cache_description'
        indexes = [
            models.Index(fields=['cache_pid']),
        ]

    def __unicode__(self):
        return u'Cache description %s' % self.cache_pid


class CacheLog(models.Model):
    cache = models.ForeignKey(Cach, on_delete=models.CASCADE)
    cache_pid = models.IntegerField(default=0)
    logged_by_uid = models.IntegerField(blank=True, null=True)
    logged_by_nick = models.CharField(max_length=64, blank=True, null=True)
    log_type = models.CharField(max_length=16, blank=True, null=True)
    log_date = models.DateTimeField(blank=True, null=True)
    txt = models.TextField(blank=True, null=True)

    class Meta:
        db_table = u'cache_log'
        indexes = [
            models.Index(fields=['logged_by_uid']),
            models.Index(fields=['cache_pid']),
            models.Index(fields=['log_type']),
            models.Index(fields=['log_date']),
        ]

    def __unicode__(self):
        return u'Cache log %s by %s - %s' % (
                    self.cache_pid, self.logged_by_nick, self.log_date)


CACHE_TYPE_WEIGHT = {
    'TR': 2,
    'VI': 1,
    'MS': 3,
    'MV': 2,
    'LV': 2,
    'LT': 3,
    'CT': 0.5,
    'EV': 0.5,
}
CRITICAL_COUNT = 40


class CachStat(models.Model):
    cach = models.ForeignKey(
        Cach, verbose_name='cache', on_delete=models.CASCADE)
    geocacher = models.ForeignKey(
        Geocacher, verbose_name='geocacher', on_delete=models.CASCADE)
    cach_pid = models.IntegerField(default=0, verbose_name='pid')
    recommend_count = models.IntegerField(
        verbose_name='recommendations', blank=True, null=True)
    found_count = models.IntegerField(
        verbose_name='found', blank=True, null=True)
    rank = models.FloatField(verbose_name='rank', blank=True, null=True)
    points = models.FloatField(verbose_name='points', blank=True, null=True)

    class Meta:
        db_table = u'cach_stat'
        indexes = [
            models.Index(fields=['cach_pid']),
        ]

    def __unicode__(self):
        return u'Cach stat %s/%s by %s' % (
                        self.pid, self.recommend_count, self.found_count)

    def multiply_factor(self):
        if self.found_count is not None:
            if self.found_count < 2:
                return 10
            if self.found_count >= CRITICAL_COUNT:
                return 1
            b = 9.0 / (1 - 1.0 / CRITICAL_COUNT)
            a = 10.0 - b
            return a + b / self.found_count
        return 0

    def calculate_points(self):
        self.points = self.multiply_factor() * \
                (CACHE_TYPE_WEIGHT.get(self.cach.type_code) or 0)
        self.save()


class GeocacherStat(models.Model):
    geocacher = models.ForeignKey(
        Geocacher, verbose_name='Geocacher', on_delete=models.CASCADE)
    uid = models.IntegerField(blank=True, null=True)
    found_count = models.IntegerField(blank=True, null=True)
    created_count = models.IntegerField(blank=True, null=True)
    curr_found_count = models.IntegerField(blank=True, null=True)
    curr_created_count = models.IntegerField(blank=True, null=True)
    last_found_count = models.IntegerField(blank=True, null=True)
    last_created_count = models.IntegerField(blank=True, null=True)
    av_grade = models.FloatField(blank=True, null=True)
    av_his_cach_grade = models.FloatField(blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    region = models.CharField(max_length=128, blank=True, null=True)
    vi_found_count = models.IntegerField(blank=True, null=True)
    vi_created_count = models.IntegerField(blank=True, null=True)
    vi_curr_found_count = models.IntegerField(blank=True, null=True)
    vi_curr_created_count = models.IntegerField(blank=True, null=True)
    vi_last_found_count = models.IntegerField(blank=True, null=True)
    vi_last_created_count = models.IntegerField(blank=True, null=True)
    tr_found_count = models.IntegerField(blank=True, null=True)
    tr_created_count = models.IntegerField(blank=True, null=True)
    tr_curr_found_count = models.IntegerField(blank=True, null=True)
    tr_curr_created_count = models.IntegerField(blank=True, null=True)
    tr_last_found_count = models.IntegerField(blank=True, null=True)
    tr_last_created_count = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = u'geocacher_stat'
        indexes = [
            models.Index(fields=['uid']),
        ]

    def __unicode__(self):
        return u'Geocacher stat %s-%s/%s' % (
                    self.geocacher, self.created_count, self.found_count)


class GeocacherSearchStat(models.Model):
    geocacher = models.ForeignKey(
        Geocacher, verbose_name='Geocacher', null=True,
        on_delete=models.CASCADE)
    geocacher_uid = models.IntegerField(default=0)
    points = models.IntegerField(blank=True, null=True, default=0)
    year_points = models.IntegerField(blank=True, null=True, default=0)
    country = models.CharField(max_length=64, blank=True, null=True)
    region = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = u'geocacher_search_stat'
        indexes = [
            models.Index(fields=['geocacher_uid']),
        ]

    def __unicode__(self):
        return u'Geocacher search stat %s by %s' % (
            self.points, self.geocacher_uid)

    def set_points(self):
        sql = """
        select sum(IFNULL(cs.points, 0)) as points_sum
        from  log_seek_cach lsc
        left join cach_stat cs on lsc.cach_pid = cs.cach_pid
        where lsc.cacher_uid = %s
        """ % self.geocacher_uid
        self.points = sql2val(sql)
        self.save()


class Cacher:
    # pid = None
    uid = None
    nickname = None
    name = None
    birstday = None
    sex = None
    email = None
    country = None
    town = None
    oblast = None
    phone = None
    icq = None
    web = None
    gps = None
    created_caches = None
    found_caches = None
    photo_albums = None
    register_date = None
    last_login = None
    forum_posts = None

    def __eq__(self, other):
        r = self.__dict__ == other.__dict__
        if not r:
            print(self.__dict__)
            print(other.__dict__)
        return r
