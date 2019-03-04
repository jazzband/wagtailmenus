import sys
from cogwheels import BaseAppSettingsHelper


class WagtailmenusSettingsHelper(BaseAppSettingsHelper):
    deprecations = ()


sys.modules[__name__] = WagtailmenusSettingsHelper()
