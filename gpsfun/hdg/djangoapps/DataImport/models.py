from django.db import models
from django.conf import settings 
from django.dispatch import dispatcher
from django.db.models import signals
from DjHDGutils.flow import view_to_url
from django.utils.translation import ugettext_lazy as _


# class NewsArticle(models.Model): 
#     pub_date = models.DateTimeField(_('Publishing date'), )
#     title = models.CharField(_('Title'), max_length=255)
#     slug = models.SlugField(_('Slug'), )
#     text = models.TextField(_('Text'), )
#     language = models.CharField(_('Language'), max_length=2,choices=settings.LANGUAGES)
# 
#     def __unicode__(self):
#         return self.title
# 
#     def get_absolute_url(self):
#         return view_to_url('newsarticle', self.slug)
#     
#     class Meta:
#         db_table = 'news'
#         verbose_name = _('news article')
#         verbose_name_plural = _('news articles')
# 
#     class Admin:
#         list_display=('slug','pub_date','title','language')
# 
# class NewsArticlePhoto(models.Model):
#     photo = models.ImageField(upload_to="news_images/")
#     article = models.ForeignKey(NewsArticle)


