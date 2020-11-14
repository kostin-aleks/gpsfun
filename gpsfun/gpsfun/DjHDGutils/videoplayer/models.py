from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class VideoFile(models.Model):
    movie = models.FileField(upload_to="news/attachments")
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    slug = models.SlugField()

    content_object = generic.GenericForeignKey()


    def related_object(self):
        return self.content_object

    def get_flv_url(self):
        from django.conf import settings
        import os
        flv_video_url = settings.MEDIA_URL+''.join(os.path.splitext(self.movie)[0]+'.flv')
        return flv_video_url

    def get_png_url(self):
        from django.conf import settings
        import os
        png_video_url = settings.MEDIA_URL+''.join(os.path.splitext(self.movie)[0]+'.png')
        return png_video_url
    
    class Admin:
        list_display = ('movie','content_type', 'related_object')

    def save(self):
        from DjHDGutils.videoplayer.utils import convertvideo
        from django.conf import settings
        import os
        super(VideoFile,self).save()
        orig_video = settings.MEDIA_ROOT+'/'+self.movie
        filename, ext = os.path.splitext(orig_video)
        if ext.lower() not in ['.avi']:
            print 'not converting non-video file: %s' % ext
            return
        flv_video = ''.join(filename+'.flv')
        if not os.path.exists(flv_video):
            any_error = convertvideo(orig_video,flv_video)
            if any_error:
                print 'error: %s' % any_error


