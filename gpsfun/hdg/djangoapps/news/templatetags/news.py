from django import template
from hdg.djangoapps.news.models import NewsArticle
register = template.Library()

@register.inclusion_tag('news/news_box.html', takes_context=True)
def news_box(context,lang,howmany=5):
    articles = NewsArticle.objects.all()
    if lang != 'all':
        articles = articles.filter(language=lang)
    articles=articles.order_by('-pub_date')[:howmany]
    context['articles']=articles
    context['lang']=lang
    return context
