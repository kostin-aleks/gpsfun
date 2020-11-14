from django import http
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import requires_csrf_token
from django.template import RequestContext, loader
from django.shortcuts import render
from django.core.urlresolvers import reverse
from datetime import datetime


@requires_csrf_token
def page_not_found(request):
    """ YP 404 handler """
    template_name = '404.html'

    t = loader.get_template(template_name)
    return http.HttpResponseNotFound(t.render(RequestContext(request, {})))


@cache_page(60 * 60 * 24)
def jsu18n(request):
    return render(request, 'js/i18n.js.html',
                  content_type='text/javascript;charset=UTF-8')


def disable_ssl(request):
    """
    Once we set cookie, the middleware will stop redirecting to https
    """
    response = http.HttpResponseRedirect(reverse('yp-main'))
    if 'DisableSSL' not in request.COOKIES:
        response.set_cookie('DisableSSL', 'True')
    return response


def allow_ssl(request):
    """
    Once SSL was disabled by disable_ssl() view above we need a way to enable
    it back
    """
    referer_url = request.GET.get('p', reverse(('yp-main')))
    response = http.HttpResponseRedirect(referer_url)
    response.delete_cookie('DisableSSL')
    return response


def disable_ssl_info(request):
    return render(request, "Teacher/Freemium/disable_ssl_info.html")


def custom_csrf_error(request, reason=""):
    csrf_error = ErrorLog()
    csrf_error.error_type = "CSRF"
    csrf_error.error_source = request.path
    csrf_error.error_date = datetime.now()
    csrf_error.error_details = reason
    csrf_error.save()
    return render(request, 'custom_csrf_error.html', {'reason': reason})
