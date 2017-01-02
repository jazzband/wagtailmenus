from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig
from . import initialize_settings


class WagtailMenusConfig(AppConfig):
    name = 'wagtailmenus'
    verbose_name = 'WagtailMenus'

    def __init__(self, app_name, app_module):
        super(WagtailMenusConfig, self).__init__(app_name, app_module)
        initialize_settings()
