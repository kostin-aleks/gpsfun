from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('hdg.djangoapps.DataImport.views',
    #url(r'^/(.*)$', 'django.views.static.serve', {'document_root': settings.HDG_MEDIA_ROOT}),
    url(r'^$', 'data_import', name="data-import"),
    #url(r'^get_model_fields/$', 'get_model_fields', name="get-model-fields"),
    )
