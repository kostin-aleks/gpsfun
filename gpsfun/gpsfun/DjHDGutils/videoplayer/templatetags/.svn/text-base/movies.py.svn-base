from django import template
from django.conf import settings
from DjHDGutils.videoplayer.models import VideoFile
register = template.Library()

@register.inclusion_tag('videoplayer/embed_video.html')
def embed_video(object, slug):
    movie = VideoFile.objects.get(object_id=object.id,
                                  slug=slug)
    return dict(movie=movie,
                MEDIA_URL=settings.MEDIA_URL)

