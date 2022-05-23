"""
models
"""

import pickle
from django.db import models
from django.contrib.auth.models import User


class TableViewProfile(models.Model):
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE)
    tableview_name = models.CharField(max_length=255)
    label = models.CharField(max_length=255, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    dump = models.TextField()

    class Meta:
        db_table = 'tableview_profile'

    def _get_state(self):
        dump = str(self.dump)
        dump = dump.decode('hex_codec')
        try:
            state = pickle.loads(dump)
        except:
            state = None
        return state
    state = property(_get_state)
