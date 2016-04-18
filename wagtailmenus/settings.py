# -*- coding: utf-8 -*-
from django.conf import settings

ACTIVE_CLASS = getattr(settings, 'WAGTAILMENUS_ACTIVE_CLASS', 'active')

ACTIVE_ANCESTOR_CLASS = getattr(settings, 'WAGTAILMENUS_ACTIVE_ANCESTOR_CLASS',
                                'ancestor')
