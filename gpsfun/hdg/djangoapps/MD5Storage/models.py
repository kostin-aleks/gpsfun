from django.db import models

class Refcount(models.Model):
    md5 = models.CharField(max_length=32, unique=True)
    refs = models.IntegerField(default=0)
    size = models.IntegerField()

    class Meta:
        db_table = 'md5storage_refcount'

