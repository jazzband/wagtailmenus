import warnings
from wagtailmenus.conf.constants import * # noqa
from wagtailmenus.utils.deprecation import RemovedInWagtailMenus212Warning

warnings.warn(
    "The 'wagtailmenus.constants' module is deprecated in favour of using "
    "'wagtailmenus.conf.constants'. Please update the import statements in "
    "your code to use the new path.", category=RemovedInWagtailMenus212Warning
)
