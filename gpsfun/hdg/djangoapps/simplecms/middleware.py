from django.conf import settings
from django.views.generic.simple import direct_to_template


class simplecms(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a flatpage for non-404 responses.
        if settings.DEBUG:
            return direct_to_template(request, '404.html')
        #return response
