# Create your views here.
from django.shortcuts import render_to_response
from hdg.djangoapps.news.models import NewsArticle
from django.template import RequestContext
from django.http import Http404

def object_detail(request,slug):
    try:
        article = NewsArticle.objects.get(slug=slug)
    except NewsArticle.DoesNotExist:
        raise Http404
        
    return render_to_response('news/newsarticle_detail.html',RequestContext(request,dict(object=article)))
