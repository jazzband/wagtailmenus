from __future__ import absolute_import, unicode_literals

from django.db import models


class MenuItemManager(models.Manager):
    ''' App-specific manager overrides '''

    def for_display(self):
        return self.all()
