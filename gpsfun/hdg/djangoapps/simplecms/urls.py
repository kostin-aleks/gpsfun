from django.conf.urls.defaults import *
from django.conf import settings

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns(
    'hdg.djangoapps.simplecms.views',

    url(r'nav/addobj/$', 'nav_addobj', name='simplecms-nav-addobj'),
    url(r'nav/delobj/$', 'nav_delobj', name='simplecms-nav-delobj'),
    url(r'nav/editobj/$', 'editobj', name='simplecms-obj-edit'),
    url(r'nav/editnav/$', 'editnav', name='simplecms-nav-edit'),
#    url(r'^nav/addlnk/$', 'nav_link_add', name='simplecms-nav-add-link'),
#    url(r'^nav/dellnk/(?P<object_id>)/$', 'nav_object_del', name='simplecms-nav-link-del'),
)
