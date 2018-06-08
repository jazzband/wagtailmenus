from django.utils.translation import ugettext_lazy as _

USE_SPECIFIC_OFF = 0
USE_SPECIFIC_AUTO = 1
USE_SPECIFIC_TOP_LEVEL = 2
USE_SPECIFIC_ALWAYS = 3
USE_SPECIFIC_CHOICES = (
    (USE_SPECIFIC_OFF, _("Off (most efficient)")),
    (USE_SPECIFIC_AUTO, _("Auto")),
    (USE_SPECIFIC_TOP_LEVEL, _("Top level")),
    (USE_SPECIFIC_ALWAYS, _("Always (least efficient)")),
)
MAX_LEVELS_CHOICES = (
    (1, _('1: No sub-navigation (flat)')),
    (2, _('2: Allow 1 level of sub-navigation')),
    (3, _('3: Allow 2 levels of sub-navigation')),
    (4, _('4: Allow 3 levels of sub-navigation')),
)
