from django.conf.urls.defaults import *

urlpatterns = patterns(
    'DjHDGutils.datatable.views',
    url(r'^test/$', 'test_view'),
   )
