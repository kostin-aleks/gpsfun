from django.middleware.locale import LocaleMiddleware
from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.conf import settings

def get_language_from_request_path(request):
    try:
        lang = request.META['PATH_INFO'][-3:-1]
        if lang in ['en','ru']:
            return lang
        else:
            return ''
    except:
        return ''
    

class HDGLocaleMiddleware(LocaleMiddleware):
    def process_request(self, request):
        language = translation.get_language_from_request(request)
        lang = get_language_from_request_path(request)
        if lang in [x[0] for x in settings.LANGUAGES]:
            language=lang
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
