from django.conf import settings
from django import template
import os.path
from PIL import Image
import urllib
from django.utils.safestring import mark_safe
from django.utils import encoding

register = template.Library()

def src_and_size(filename, args=''):

    if filename is None:
        return ''
    if filename.startswith(settings.MEDIA_URL):
        full_filename = filename[len(settings.MEDIA_URL):]

    full_filename = os.path.join(settings.MEDIA_ROOT, full_filename)

    if not os.path.exists(full_filename):
        print("Warning, miniature not found: %s" % filename)
        return
    image = Image.open(full_filename)

    return mark_safe('width="%s" height="%s" src="%s"' % (image.size[0],
                                                          image.size[1],
                                                          filename))

register.filter(src_and_size)

def thumbnail(filename, args=''):
    """ args - string with params like "param1=val1[,param2=val2...]"

        params:
          height, width - limits of proportional image resizing (in pixels)
          square - make photo square by cropping longest size (True/False)
    """
    filename = encoding.smart_unicode(urllib.unquote(filename))

    def get_basename(filename):
        basename = extension = u''
        arr = filename.rsplit(u'.', 1)
        basename = arr[0]
        if len(arr)>1:
            extension = arr[1]
        return basename,extension

    if filename=='':
        return

    width = None
    height = None

    if filename.startswith(settings.MEDIA_URL):
        filename = filename[len(settings.MEDIA_URL):]

    basename,extension = get_basename(filename)
    if not extension or extension=='.':
        extension=u'png'
    miniature = basename # +'_t'

    modifications = set([])
    for arg in args.split(u','):
        arg = arg.strip()
        key, val = arg.split(u'=', 1)
        if key == 'width':
            modifications.add('resize_width')
            width = int(val)
            miniature += u'_w_' + unicode(val)
        elif key == 'height':
            modifications.add('resize_height')
            height = int(val)
            miniature += u'_h_' + unicode(val)
        elif key == 'square':
            modifications.add('resize_square')
            miniature += u'_sq_' + unicode(val)
            square = int(val)
        else:
            raise template.TemplateSyntaxError(
                "thumbnail filter requires arguments (width and/or height)")

    miniature += u'.' + extension
    miniature = u"%s/._t_%s" % (os.path.dirname(miniature),
                                os.path.basename(miniature))

    miniature_filename = os.path.join(settings.MEDIA_ROOT, miniature)
    miniature_url = os.path.join(settings.MEDIA_URL, miniature)
    filename = os.path.join(settings.MEDIA_ROOT, filename)

    if not os.path.exists(filename):
        print("Warning, miniature not created for non-exising file: %s" % filename)
        if hasattr(settings, 'STATIC_URL'):
            return settings.STATIC_URL+'img/image_not_found.gif'
        return

    if not os.path.exists(miniature_filename) or (os.path.getmtime(filename) > os.path.getmtime(miniature_filename)):
        image = Image.open(filename)

        if 'resize_square' in modifications:
            start_width, start_height = image.size
            if start_height < start_width:
                modifications.add('resize_height')
                height = square
            else:
                modifications.add('resize_width')
                width = square


        if 'resize_width' in modifications:
            new_height = int(image.size[1] * width / image.size[0])
            if (height is not None) and new_height>height:
                new_height = height
                new_width = int(image.size[0] * height / image.size[1])
            else:
                new_width = width
            image.thumbnail([new_width,new_height], Image.ANTIALIAS)

        if 'resize_height' in modifications:
            new_width = int(image.size[0] * height / image.size[1])
            if (width is not None) and new_width>width:
                new_width = width
                new_height = int(image.size[1] * width / image.size[0])
            else:
                new_height = height

        need_save = False
        try:
            image.thumbnail([new_width, new_height], Image.ANTIALIAS)
            need_save = True
        except IOError as e:
            print('DjHDGutils: thumbnail.py: '
                  'IOError %s for file: %s.' % (e, filename))
            return

        if 'resize_square' in modifications:
            cur_width, cur_height = image.size
            minsize = min(cur_width, cur_height)
            if cur_width > square or cur_height > square:
                horiz_cropped = (cur_width - minsize) / 2
                vert_cropped = (cur_height - minsize) / 2
                image = image.crop((0 + horiz_cropped,
                                    0 + vert_cropped,
                                    cur_width - horiz_cropped,
                                    cur_height - vert_cropped))

            try:
                image = image.crop((0,
                                    0,
                                    square,
                                    square))
                need_save = True
            except IOError as e:
                print('DjHDGutils: thumbnail.py: '\
                      'IOError %s for file: %s.' % (e,filename))
                return

        if need_save:
            image.save(miniature_filename, image.format)


    return encoding.iri_to_uri(miniature_url)


register.filter(thumbnail)

@register.simple_tag
def thumbnail_url(url, width, height):
    args=[]
    if width:
        args.append('width=%s' % width)
    if height:
        args.append('height=%s' % height)
    return thumbnail(url, ",".join(args))

@register.simple_tag
def square_thumbnail_url(url, square):
    """ make photo square by cropping longest size """
    args=[]
    args.append('square=%s' % square)
    return thumbnail(url, ",".join(args))
