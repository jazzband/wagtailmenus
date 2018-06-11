from wagtailmenus.utils.conf import BaseAppSettingsHelper
from wagtailmenus.utils import deprecation
from . import defaults


class AppSettingsHelper(BaseAppSettingsHelper):
    prefix = 'WAGTAILMENUS_'

    @property
    def SECTION_MENU_CLASS(self):
        return self.get_or_try_deprecated_name(
            'SECTION_MENU_CLASS',
            'SECTION_MENU_CLASS_PATH',
            warning_category=deprecation.RemovedInWagtailMenus212Warning
        )

    @property
    def CHILDREN_MENU_CLASS(self):
        return self.get_or_try_deprecated_name(
            'CHILDREN_MENU_CLASS',
            'CHILDREN_MENU_CLASS_PATH',
            warning_category=deprecation.RemovedInWagtailMenus212Warning
        )


settings = AppSettingsHelper(defaults)
