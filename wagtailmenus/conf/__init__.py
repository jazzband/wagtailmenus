from wagtailmenus.utils.conf import BaseAppSettingsHelper, AppSettingDeprecation
from wagtailmenus.utils import deprecation
from . import defaults


class AppSettingsHelper(BaseAppSettingsHelper):
    prefix = 'WAGTAILMENUS_'
    defaults = defaults
    deprecations = (
        AppSettingDeprecation(
            'SECTION_MENU_CLASS_PATH',
            replaced_by='SECTION_MENU_CLASS',
            warning_category=deprecation.RemovedInWagtailMenus212Warning,
        ),
        AppSettingDeprecation(
            'CHILDREN_MENU_CLASS_PATH',
            replaced_by='CHILDREN_MENU_CLASS',
            warning_category=deprecation.RemovedInWagtailMenus212Warning,
        ),
    )

settings = AppSettingsHelper()
