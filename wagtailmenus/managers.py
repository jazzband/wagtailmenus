from __future__ import absolute_import, unicode_literals

import warnings
from django.db import models

from wagtailmenus.utils.deprecation import RemovedInWagtailMenus27Warning


class MenuItemManager(models.Manager):
    ''' App-specific manager overrides '''

    @classmethod
    def warn_of_deprecation(cls):
        warning_msg = (
            "The 'MenuItemManager' manager is deprecated. Any filtering out "
            "of pages based on their published status, visibility, or any "
            "other fields should be applied by a menu's "
            "'get_base_page_queryset' method. See the 2.5 release notes for "
            "more information: http://wagtailmenus.readthedocs.io/en/stable/"
            "releases/2.5.0.html"
        )
        warnings.warn(warning_msg, RemovedInWagtailMenus27Warning)

    def __init__(self, *args, **kwargs):
        self.warn_of_deprecation()
        super(MenuItemManager, self).__init__(*args, **kwargs)

    def for_display(self):
        self.warn_of_deprecation()
        return self.filter(
            models.Q(link_page__isnull=True) |
            models.Q(link_page__live=True) &
            models.Q(link_page__expired=False) &
            models.Q(link_page__show_in_menus=True)
        )
