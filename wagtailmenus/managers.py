from django.utils.timezone import now
from django.db import models


class MenuItemManager(models.Manager):
    ''' App-specific manager overrides '''

    def for_display(self):
        return self.filter(
            Q(link_page__isnull=True) |
            Q(link_page__live=True) & Q(link_page__expired=False) & 
            Q(link_page__in_menus=True)
        ).select_related('link_page')
