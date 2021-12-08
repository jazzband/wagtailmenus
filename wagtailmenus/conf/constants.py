from django.utils.translation import gettext_lazy as _


MAX_LEVELS_CHOICES = (
    (1, _('1: No sub-navigation (flat)')),
    (2, _('2: Allow 1 level of sub-navigation')),
    (3, _('3: Allow 2 levels of sub-navigation')),
    (4, _('4: Allow 3 levels of sub-navigation')),
)
