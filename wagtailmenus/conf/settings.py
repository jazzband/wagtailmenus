import sys

from django.conf import settings as django_settings
from cogwheels import BaseAppSettingsHelper


class WagtailmenusSettingsHelper(BaseAppSettingsHelper):
    deprecations = ()

    def __getattr__(self, name):
        value = super().__getattr__(name)
        # Auto-detect locale-awareness from Wagtail's own i18n flag when the
        # wagtailmenus-specific setting has not been explicitly overridden.
        if name == 'LOCALIZE_MENU_ITEMS' and not value and not self.is_overridden('LOCALIZE_MENU_ITEMS'):
            return bool(getattr(django_settings, 'WAGTAIL_I18N_ENABLED', False))
        return value


sys.modules[__name__] = WagtailmenusSettingsHelper()
