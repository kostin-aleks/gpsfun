from django.conf.urls.defaults import patterns, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('hdg.djangoapps.admin_index.views',
                       url(r'^', "index"),
                       )
