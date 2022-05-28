"""
ajax utils
"""

import functools
import json as simplejson
import sys
import traceback

from django.conf import settings
from django.core.mail import mail_admins
from django.http import HttpResponse, Http404
from django.views import debug


def _get_traceback(exc_info=None):
    """ Helper function to return the traceback as a string """
    return '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))


def _copy_x_headers(orig_resp, target_resp):
    """ copy headers """
    if not orig_resp or not hasattr(orig_resp, 'items'):
        return

    for key, value in orig_resp.items():
        if key.lower().startswith('x-'):
            target_resp[key] = value


def _json_dump(data):
    """ dump data as json data """
    return HttpResponse(simplejson.dumps(data, ensure_ascii=False),
                        content_type='application/javascript')


def accept_ajax(view_func):
    """ decorator accept_ajax """
    @functools.wraps(view_func)
    def _wrap_view_func(request, *args, **kwargs):
        is_ajax = True

        if hasattr(request, 'is_ajax'):
            if not request.is_ajax():
                is_ajax = False
        else:
            # for backward compatibility with Django pre 1.0
            if not ('HTTP_ACCEPT' in request.META and 'application/javascript' in request.META['HTTP_ACCEPT']):
                is_ajax = False

        origin_resp = None

        # FIXME: require refactoring here
        if not is_ajax:
            # require direct call original function (out of try/except) to proper determine error exception
            # in orinical view
            origin_resp = view_func(request, *args, **kwargs)
            if isinstance(origin_resp, (dict, list)):
                return _json_dump(origin_resp)
            return origin_resp

        response_dict = {}
        response_dict['debug'] = False
        try:
            origin_resp = view_func(request, *args, **kwargs)

            if isinstance(origin_resp, (dict, list)):
                if isinstance(origin_resp, dict):
                    if 'status' not in origin_resp:
                        origin_resp['status'] = 200
                return _json_dump(origin_resp)

            if hasattr(origin_resp, 'content_type') and origin_resp.content_type == 'application/javascript':
                return origin_resp

            response_dict['status'] = origin_resp.status_code
            response_dict['content'] = origin_resp.content

        except Http404 as the_exception:
            raise Http404(the_exception)
        except Exception as the_exception:
            response_dict['status'] = 500

            if settings.DEBUG:
                debug.technical_500_response(request, *sys.exc_info())
                response_dict['debug'] = True
                response_dict['debug_msg'] = ''
            else:
                exc_info = sys.exc_info()

                remote_addr = (request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS and 'internal' or 'EXTERNAL')
                subject = f'Error ({remote_addr} IP): {request.path}'
                try:
                    request_repr = repr(request)
                except:
                    request_repr = "Request repr() unavailable"

                message = f"{_get_traceback(exc_info)}\n\n{request_repr}"
                mail_admins(subject, message, fail_silently=True)

        resp = HttpResponse(
            simplejson.dumps(response_dict, ensure_ascii=False),
            content_type='application/javascript')
        _copy_x_headers(origin_resp, resp)

        return resp

    return _wrap_view_func


def qs_to_json(qs, map_dict):
    """
      Iterate over qs and do mapping action for each item accoring to map_dict
      example:
         qs is QuerySet for object with fields id, name
         map_dict = {'value': 'id',
                     'label': 'name'}

         resulting dump will contain list of objects with fields value and label
    """
    def _get_value(name, obj):
        attr = getattr(obj, name)
        if callable(attr):
            return attr()
        return attr

    label_list = [dict([(key, _get_value(value, item)) for key, value in map_dict.iteritems()])
                  for item in qs]

    return simplejson.dumps(label_list)
