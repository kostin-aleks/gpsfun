from django.db import models
from hdg.djangoapps.MD5Storage.storage import MD5Storage
from django.utils.translation import ugettext_lazy as _

class ObjectImage(models.Model):
    image = models.ImageField(_('Image'), upload_to='object_images',
                              storage=MD5Storage())
    filename = models.CharField(_('Filename'), max_length=100)

    class Meta:
        db_table = 'object_image'
        abstract = True

class ObjectFile(models.Model):
    afile = models.FileField(_('File'), upload_to='object_files',
                             storage=MD5Storage())
    title = models.CharField(_('Title'), max_length=255,blank=True,
                             null=True)
    filename = models.CharField(_('Filename'), max_length=100)

    def fname(self):
        return self.afile.name.split('/')[-1]

    class Meta:
        db_table = 'object_file'
        abstract = True
