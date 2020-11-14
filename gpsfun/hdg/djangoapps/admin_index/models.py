from django.db import models
from django.utils.translation import ugettext as _


class Bookmark(models.Model):
    user = models.ForeignKey('auth.User', limit_choices_to={'is_staff': True},
                             verbose_name=_('User'))
    title = models.CharField(_('Title'), max_length=80)
    link = models.URLField(_('Link'), verify_exists=True, max_length=200)
    is_public = models.BooleanField(default=True)

    class Meta:
        db_table = 'admin_index_bookmark'
