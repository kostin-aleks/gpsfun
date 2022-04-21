"""
context
"""
import time
from django.conf import settings


def template(request):
    """ template """
    return {
        'CSSVERSION': settings.CSSVERSION,
        'current_time': str(time.time()),
    }
