import sys
from cogwheels import BaseAppSettingsHelper, DeprecatedAppSetting
from wagtailmenus.utils import deprecation


class WagtailmenusSettingsHelper(BaseAppSettingsHelper):
    deprecations = (
        DeprecatedAppSetting(
            'SECTION_MENU_CLASS_PATH',
            renamed_to='SECTION_MENU_CLASS',
            warning_category=deprecation.RemovedInWagtailMenus212Warning,
        ),
        DeprecatedAppSetting(
            'CHILDREN_MENU_CLASS_PATH',
            renamed_to='CHILDREN_MENU_CLASS',
            warning_category=deprecation.RemovedInWagtailMenus212Warning,
        ),
    )


sys.modules[__name__] = WagtailmenusSettingsHelper()
