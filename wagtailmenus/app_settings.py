import sys
import warnings

from wagtailmenus.conf import settings
from wagtailmenus.utils.deprecation import RemovedInWagtailMenus212Warning

warnings.warn(
    "The 'wagtailmenus.app_settings' module is deprecated in favour of "
    "using 'wagtailmenus.conf.settings'. Please update the import "
    "statements in your code to use the new path.",
    category=RemovedInWagtailMenus212Warning
)

sys.modules[__name__] = settings
