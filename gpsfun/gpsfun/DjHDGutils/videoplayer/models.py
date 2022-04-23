"""
Models for Video
"""
import os
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from DjHDGutils.videoplayer.utils import convertvideo


class VideoFile(models.Model):
    """ VideoFile """
    movie = models.FileField(upload_to="news/attachments")
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    slug = models.SlugField()

    content_object = generic.GenericForeignKey()

    def related_object(self):
        """ related object """
        return self.content_object

    def get_flv_url(self):
        """ get flv url """
        flv_video_url = settings.MEDIA_URL + ''.join(os.path.splitext(self.movie)[0] + '.flv')
        return flv_video_url

    def get_png_url(self):
        """ get png url """
        png_video_url = settings.MEDIA_URL + ''.join(os.path.splitext(self.movie)[0] + '.png')
        return png_video_url

    class Admin:
        """ Admin """
        list_display = ('movie', 'content_type', 'related_object')

    def save(self):
        """ save """
        super(VideoFile, self).save()
        orig_video = settings.MEDIA_ROOT + '/' + self.movie
        filename, ext = os.path.splitext(orig_video)
        if ext.lower() not in ['.avi']:
            print('not converting non-video file: {ext}')
            return
        flv_video = ''.join(filename + '.flv')
        if not os.path.exists(flv_video):
            any_error = convertvideo(orig_video, flv_video)
            if any_error:
                print('error: {any_error}')
