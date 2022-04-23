"""
database views
"""
from django.shortcuts import render_to_response
from django.template import RequestContext
from DjHDGutils.datatable.test import Data1


def test_view(request):
    cnt = Data1(request)

    redirect = cnt.get_redirect()
    if redirect:
        return redirect

    return render_to_response(
        'datatable_test.html',
        RequestContext(
            request,
            {'datatable': cnt, }))
