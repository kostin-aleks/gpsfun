"""
model fields
"""
import os
from django.forms.fields import ChoiceField
import re

from django.db import models


def _to_absolute_path(path, base_path):
    """ to absolute path """
    if path and not path.startswith("/"):
        return os.path.join(base_path, path)
    return path


class RelativeFilePathField(models.FilePathField):
    """
    This field adds get_[field_name]_path function to the model class that returns absolute path.
    """

    def value_from_object(self, obj):
        """ value from object """
        val = super(RelativeFilePathField, self).value_from_object(obj)
        return _to_absolute_path(val, self.path)

    def pre_save(self, model_instance, add):
        """ pre save """
        val = super(RelativeFilePathField, self).pre_save(model_instance, add)
        if val and val.startswith(self.path):
            return os.path.relpath(val, self.path)
        return val

    def contribute_to_class(self, cls, name):
        """ contribute to class """
        super(RelativeFilePathField, self).contribute_to_class(cls, name)

        field = self

        def path_func(obj):
            path = getattr(obj, name)
            return _to_absolute_path(path, field.path)

        setattr(cls, f'get_{self.name}_path', path_func)


class MediaPathFieldForm(ChoiceField):
    def __init__(self, path, match=None, recursive=False, required=True,
                 widget=None, label=None, initial=None, help_text=None,
                 *args, **kwargs):
        self.path, self.match, self.recursive = path, match, recursive
        super(MediaPathFieldForm, self).__init__(
            choices=(), required=required,
            widget=widget, label=label, initial=initial, help_text=help_text,
            *args, **kwargs)

        if self.required:
            self.choices = []
        else:
            self.choices = [("", "---------")]

        if self.match is not None:
            self.match_re = re.compile(self.match)

        from django.conf import settings
        if recursive:
            for root, dirs, files in os.walk(settings.MEDIA_ROOT + self.path):
                for f in files:
                    if self.match is None or self.match_re.search(f):
                        f = os.path.join(root, f)
                        self.choices.append((f, f.replace(path, "", 1)))
        else:
            try:
                for f in os.listdir(settings.MEDIA_ROOT + self.path):
                    full_file = os.path.join(settings.MEDIA_ROOT + self.path, f)
                    if os.path.isfile(full_file) and (self.match is None or self.match_re.search(f)):
                        self.choices.append((full_file[len(settings.MEDIA_ROOT):], f))
            except OSError:
                pass

        self.widget.choices = self.choices


class MediaFilePathField(models.FilePathField):
    """ Files are placed in sub-directory of settings.MEDIA_ROOT.
    use object.get_field_path to get full path
    and object.get_field_url to get URL.
    """

    def formfield(self, **kwargs):
        """ form field """
        defaults = {
            'path': self.path,
            'match': self.match,
            'recursive': self.recursive,
            'form_class': MediaPathFieldForm,
        }
        defaults.update(kwargs)
        return super(MediaFilePathField, self).formfield(**defaults)

    def contribute_to_class(self, cls, name):
        """ contribute to class """
        super(MediaFilePathField, self).contribute_to_class(cls, name)

        field = self

        def get_url(obj):
            from django.conf import settings
            return settings.MEDIA_URL + getattr(obj, name)
        setattr(cls, f'get_{self.name}_url', get_url)

        def get_abspath(obj):
            from django.conf import settings
            return settings.MEDIA_ROOT + getattr(obj, name)
        setattr(cls, f'get_{self.name}_abspath', get_abspath)
