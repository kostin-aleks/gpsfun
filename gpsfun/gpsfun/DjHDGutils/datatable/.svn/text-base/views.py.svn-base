from django.shortcuts import render_to_response,get_object_or_404
from django.http import Http404,HttpResponse,HttpResponseRedirect,HttpResponseForbidden
from django.conf import settings
from django.template import RequestContext


def test_view(request):
    from DjHDGutils.datatable.test import Data1


    cnt = Data1(request)

    redirect = cnt.get_redirect()
    if redirect:
        return redirect

    return render_to_response('datatable_test.html',
                              RequestContext(request,
                                             {'datatable': cnt,}))

    

