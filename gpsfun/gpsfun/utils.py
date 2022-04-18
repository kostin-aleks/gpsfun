"""
Module stores utilities
"""

import os
from datetime import datetime

from django.shortcuts import _get_queryset


def class_name(instance):
    """
    returns name of class for the object
    """
    return instance.__class__.__name__.lower()


def get_image_path(instance, filename):
    """
    returns path related to type of object and current datetime
    """
    now = datetime.now()
    return os.path.join(
        class_name(instance),
        now.strftime('%Y%m%d%H%M'), filename)


def get_object_or_none(klass, *args, **kwargs):
    """
    returns object by args or None
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def media_url(request, url):
    """
    creates media url for the local url
    """
    if request and url:
        return request.build_absolute_uri(url)
    return url


def image_url(image):
    """
    checks image and returns image local url
    """
    if image is not None:
        try:
            url = image.url
        except ValueError:
            url = ''
        return url
    return ''
