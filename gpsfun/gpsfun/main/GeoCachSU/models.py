"""
Models GeoCachSU
"""
from datetime import datetime
from django.db import models

from django.utils.translation import ugettext_lazy as _
from gpsfun.main.db_utils import get_object_or_none
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
    """ Geocacher """
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
        db_table = 'geocacher'

    def __str__(self):
        nick = str(self.nickname).decode('utf-8')
        return f'{self.id}/{self.uid}/{self.name}/{nick}'

    def cacher_country(self):
        """ get geocacher country """
        return get_object_or_none(GeoCountry, iso3=self.country_iso3)

    def cacher_region(self):
        """ get geocacher region """
        iso = country_iso_by_iso3(self.country_iso3)
        return get_object_or_none(
            GeoCountryAdminSubject,
            country_iso=iso,
            code=self.admin_code)

    def statistics(self):
        """ get geocacher statistic """
        return get_object_or_none(GeocacherStat, geocacher=self)

    def caching_months(self):
        """ list of months with geocaching """
        months = []
        if self.register_date:
            seek_months = LogSeekCach.objects.filter(cacher_uid=self.uid)
            seek_months = seek_months.values_list('found_date', flat=True).distinct()

            for dtime in seek_months:
                if (dtime.year, dtime.month) not in months:
                    months.append((dtime.year, dtime.month))
            hide_months = LogCreateCach.objects.filter(author_uid=self.uid)
            hide_months = hide_months.values_list('created_date', flat=True).distinct()

            for dtime in hide_months:
                if (dtime.year, dtime.month) not in months:
                    months.append((dtime.year, dtime.month))

        return len(months)

    def total_months(self):
        """ total months after registration of user """
        #IMPROVE
        if self.register_date:
            return int(round((datetime.now() - self.register_date).days / 30.0))
        return 0

    def avg_caches_per_month(self):
        """ average count of caches per month """
        sql = f"""
        SELECT AVG(cnt)
        FROM (
            SELECT YEAR(found_date), MONTH(found_date), COUNT(id) as cnt
            FROM log_seek_cach
            WHERE cacher_uid={self.uid}
            GROUP BY YEAR(found_date), MONTH(found_date)
        ) as tbl
        """
        return sql2val(sql)

    def most_found_one_month(self):
        """ the most count of found caches for one month """
        sql = f"""
        SELECT MAX(cnt)
        FROM (
            SELECT YEAR(found_date), MONTH(found_date), COUNT(id) as cnt
            FROM log_seek_cach
            WHERE cacher_uid={self.uid}
            GROUP BY YEAR(found_date), MONTH(found_date)
        ) as tbl
        """
        return sql2val(sql)

    def avg_created_caches_per_month(self):
        """ average count of created caches per month """
        sql = f"""
        SELECT AVG(cnt)
        FROM (
            SELECT YEAR(created_date), MONTH(created_date), COUNT(id) as cnt
            FROM log_create_cach
            WHERE author_uid={self.uid}
            GROUP BY YEAR(created_date), MONTH(created_date)
        ) as tbl
        """
        return sql2val(sql)

    def most_created_one_month(self):
        """ the most count of created caches for one month """
        sql = f"""
        SELECT MAX(cnt)
        FROM (
            SELECT YEAR(created_date), MONTH(created_date), COUNT(id) as cnt
            FROM log_create_cach
            WHERE author_uid={self.uid}
            GROUP BY YEAR(created_date), MONTH(created_date)
        ) as tbl
        """
        return sql2val(sql)

    def latest_found_cache(self):
        """ latest found cache """
        last_found = LogSeekCach.objects.filter(cacher_uid=self.uid)
        last_found = last_found.order_by('-found_date')[:1]
        if last_found:
            last_found = last_found[0]
            cache = get_object_or_none(Cach, pid=last_found.cach_pid)
            return {
                'date': last_found.found_date,
                'cache': cache, }
        return None

    def latest_created_cache(self):
        """ latest created cache """
        last_created = LogCreateCach.objects.filter(author_uid=self.uid)
        last_created = last_created.order_by('-created_date')[:1]
        if last_created:
            last_created = last_created[0]
            cache = get_object_or_none(Cach, pid=last_created.cach_pid)
            return {
                'date': last_created.created_date,
                'cache': cache, }
        return None

    def recommendation_count(self):
        """ count of geocacher recommendations """
        return LogRecommendCach.objects.filter(cacher_uid=self.uid).count()

    def recommendations(self):
        """ recommendations """
        caches = Cach.objects.filter(author=self)
        caches = caches.values_list('pid', flat=True)
        return LogRecommendCach.objects.filter(cach_pid__in=caches)

    def caches_recommendation_count(self):
        """ count of caches recommendations """
        caches = Cach.objects.filter(author=self)
        caches = caches.values_list('pid', flat=True)
        return self.recommendations().count()

    def recommended_caches_count(self):
        """ count of recommended caches """
        return self.recommendations().values('cach_pid').distinct().count()

    def ratio_recommended_caches(self):
        """ ratio for recommended caches """
        recommended = self.recommended_caches_count()
        if self.statistics() and  self.statistics().created_count:
            return float(recommended or 0) / self.statistics().created_count * 100.0
        return None

    def seek_milestones(self):
        """ milestones for found caches """
        found = LogSeekCach.objects.filter(cacher_uid=self.uid)
        found = found.order_by('found_date')
        stones = []
        cnt = found.count()
        if cnt:
            stones.append({
                'idx': 1,
                'item': found[0]})
            k = 50
            while k <= cnt:
                stones.append({
                    'idx': k,
                    'item': found[k - 1]})
                k += 50

        return stones

    def hide_milestones(self):
        """ milestones for created caches """
        hidden = LogCreateCach.objects.filter(author_uid=self.uid)
        hidden = hidden.order_by('created_date')
        stones = []
        cnt = hidden.count()
        if cnt:
            stones.append({
                'idx': 1,
                'item': hidden[0]})
            k = 20
            while k <= cnt:
                stones.append({
                    'idx': k,
                    'item': hidden[k - 1]})
                k += 20

        return stones


class Cach(models.Model):
    """ Geocache """
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
        db_table = 'cach'
        indexes = [
            models.Index(fields=['pid']),
            models.Index(fields=['type_code']),
            models.Index(fields=['created_date']),
            models.Index(fields=['country_code']),
            models.Index(fields=['admin_code']),
        ]

    def __str__(self):
        name = self.name.decode('utf-8')
        return f'{self.id}/{self.code}/{name}'

    @property
    def latitude_degree(self):
        """ cache latitude, degree """
        return self.latitude

    @property
    def longitude_degree(self):
        """ cache longitude, degree """
        return self.longitude

    @property
    def site(self):
        """ site where the cache is published """
        return 'geocaching.su'

    @property
    def url(self):
        """ url to the cache """
        return f"http://www.geocaching.su/?pn=101&cid={self.pid}"

    @property
    def status(self):
        """ cache status """
        return 'Available'

    @property
    def type_name(self):
        """ type name for the cache """
        return GEOCACHING_SU_CACH_TYPES[self.type_code] or ''

    @property
    def archived(self):
        """ archived? """
        return False

    @property
    def size(self):
        """ cache size """
        return ''


class LogCreateCach(models.Model):
    """ LogCreateCach """
    author_uid = models.IntegerField(default=0)
    cach_pid = models.IntegerField(default=0)
    created_date = models.DateTimeField(blank=True, null=True)
    coauthor = models.BooleanField(default=False)

    class Meta:
        db_table = 'log_create_cach'
        indexes = [
            models.Index(fields=['author_uid']),
            models.Index(fields=['cach_pid']),
            models.Index(fields=['created_date']),
        ]

    def __str__(self):
        return f'Created cach {self.cach_pid}/{self.created_date} by {self.author_uid}'

    def cache(self):
        """ get logged cache """
        return get_object_or_none(Cach, pid=self.cach_pid)


class LogSeekCach(models.Model):
    """ LogSeekCach """
    cacher_uid = models.IntegerField(default=0)
    cach_pid = models.IntegerField(default=0)
    found_date = models.DateTimeField(blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'log_seek_cach'
        indexes = [
            models.Index(fields=['cacher_uid']),
            models.Index(fields=['cach_pid']),
            models.Index(fields=['found_date']),
        ]

    def __str__(self):
        return f'Found cach {self.cach_pid}/{self.found_date} by {self.cacher_uid}'

    def cache(self):
        """ get logged cache """
        return get_object_or_none(Cach, pid=self.cach_pid)


class LogRecommendCach(models.Model):
    """ LogRecommendCach """
    cacher_uid = models.IntegerField(default=0)
    cach_pid = models.IntegerField(default=0)

    class Meta:
        db_table = 'log_recommend_cach'
        indexes = [
            models.Index(fields=['cacher_uid']),
            models.Index(fields=['cach_pid']),
        ]

    def __str__(self):
        return f'Recommend cach {self.cach_pid} by {self.cacher_uid}'


class CacheDescription(models.Model):
    """ CacheDescription """
    cache = models.ForeignKey(Cach, on_delete=models.CASCADE)
    cache_pid = models.IntegerField(default=0)
    terrain_description = models.TextField(blank=True, null=True)
    cache_description = models.TextField(blank=True, null=True)
    virtual_part = models.TextField(blank=True, null=True)
    cache_content = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cache_description'
        indexes = [
            models.Index(fields=['cache_pid']),
        ]

    def __str__(self):
        return f'Cache description {self.cache_pid}'


class CacheLog(models.Model):
    """ CacheLog """
    cache = models.ForeignKey(Cach, on_delete=models.CASCADE)
    cache_pid = models.IntegerField(default=0)
    logged_by_uid = models.IntegerField(blank=True, null=True)
    logged_by_nick = models.CharField(max_length=64, blank=True, null=True)
    log_type = models.CharField(max_length=16, blank=True, null=True)
    log_date = models.DateTimeField(blank=True, null=True)
    txt = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cache_log'
        indexes = [
            models.Index(fields=['logged_by_uid']),
            models.Index(fields=['cache_pid']),
            models.Index(fields=['log_type']),
            models.Index(fields=['log_date']),
        ]

    def __str__(self):
        return f'Cache log {self.cache_pid} by {self.logged_by_nick} - {self.log_date}'


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
    """ CachStat """
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
        db_table = 'cach_stat'
        indexes = [
            models.Index(fields=['cach_pid']),
        ]

    def __str__(self):
        return 'Cach stat {self.pid}/{self.recommend_count} by {self.found_count}'

    def multiply_factor(self):
        """ factor """
        if self.found_count is not None:
            if self.found_count < 2:
                return 10
            if self.found_count >= CRITICAL_COUNT:
                return 1
            b_prm = 9.0 / (1 - 1.0 / CRITICAL_COUNT)
            a_prm = 10.0 - b_prm
            return a_prm + b_prm / self.found_count
        return 0

    def calculate_points(self):
        """ calculate points """
        self.points = self.multiply_factor() * \
                (CACHE_TYPE_WEIGHT.get(self.cach.type_code) or 0)
        self.save()


class GeocacherStat(models.Model):
    """ GeocacherStat """
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
        db_table = 'geocacher_stat'
        indexes = [
            models.Index(fields=['uid']),
        ]

    def __str__(self):
        return f'Geocacher stat {self.geocacher}-{self.created_count}/{self.found_count}'


class GeocacherSearchStat(models.Model):
    """ GeocacherSearchStat """
    geocacher = models.ForeignKey(
        Geocacher, verbose_name='Geocacher', null=True,
        on_delete=models.CASCADE)
    geocacher_uid = models.IntegerField(default=0)
    points = models.IntegerField(blank=True, null=True, default=0)
    year_points = models.IntegerField(blank=True, null=True, default=0)
    country = models.CharField(max_length=64, blank=True, null=True)
    region = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'geocacher_search_stat'
        indexes = [
            models.Index(fields=['geocacher_uid']),
        ]

    def __str__(self):
        return f'Geocacher search stat {self.points} by {self.geocacher_uid}'

    def set_points(self):
        """ set points """
        sql = f"""
        select sum(IFNULL(cs.points, 0)) as points_sum
        from  log_seek_cach lsc
        left join cach_stat cs on lsc.cach_pid = cs.cach_pid
        where lsc.cacher_uid = {self.geocacher_uid}
        """
        self.points = sql2val(sql)
        self.save()


class Cacher:
    """ Cacher """
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
        result = self.__dict__ == other.__dict__
        if not result:
            print(self.__dict__)
            print(other.__dict__)
        return result
