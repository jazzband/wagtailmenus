import sys
from cogwheels import BaseAppSettingsHelper


class WagtailmenusAPISettingsHelper(BaseAppSettingsHelper):
    deprecations = ()


sys.modules[__name__] = WagtailmenusAPISettingsHelper()
