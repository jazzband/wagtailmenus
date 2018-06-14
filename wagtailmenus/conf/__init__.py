from wagtailmenus.utils.conf import BaseAppSettingsHelper, DeprecatedSetting
from wagtailmenus.utils import deprecation
from . import defaults


class AppSettingsHelper(BaseAppSettingsHelper):
    prefix = 'WAGTAILMENUS_'
    deprecations = (
        DeprecatedSetting(
            'SECTION_MENU_CLASS_PATH',
            replaced_by='SECTION_MENU_CLASS',
            warning_category=deprecation.RemovedInWagtailMenus212Warning,
        ),
        DeprecatedSetting(
            'CHILDREN_MENU_CLASS_PATH',
            replaced_by='CHILDREN_MENU_CLASS',
            warning_category=deprecation.RemovedInWagtailMenus212Warning,
        ),
    )

settings = AppSettingsHelper(defaults)
