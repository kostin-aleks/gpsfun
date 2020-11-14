from django.conf.urls.defaults import *
from hdg.djangoapps.news.models import NewsArticle

info_dict = {
    'queryset': NewsArticle.objects.all(),
    'date_field': 'pub_date',
    'allow_future': 'True',
}

info_dict1 = info_dict.copy()
info_dict1['month_format']='%m'

    
urlpatterns = patterns(
    '',
    url(r'(?P<slug>[-\w]+)/$', 'hdg.djangoapps.news.views.object_detail', name='newsarticle'),
    url(r'^$', 'django.views.generic.date_based.archive_index',  info_dict, name='news'),
)
