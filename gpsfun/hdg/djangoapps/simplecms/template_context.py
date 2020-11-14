from django.conf import settings
from django.contrib.sites.models import Site

def common(request):
    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'current_site': Site.objects.get_current(),
        'PATH_INFO': request.META['PATH_INFO'],
        'is_staff': request.user.is_authenticated() and request.user.is_staff,
        }
