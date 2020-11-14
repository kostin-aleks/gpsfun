from django.conf import settings
import time

def template(request):
    return {'CSSVERSION': settings.CSSVERSION,
            'current_time': str(time.time()),
            }

