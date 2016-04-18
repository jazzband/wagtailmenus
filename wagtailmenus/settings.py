# -*- coding: utf-8 -*-
from django.conf import settings

ACTIVE_CLASS = getattr(settings, 'WAGTAILMENUS_ACTIVE_CLASS', 'active')

ACTIVE_ANCESTOR_CLASS = getattr(settings, 'WAGTAILMENUS_ACTIVE_ANCESTOR_CLASS',
                                'ancestor')

MAINMENU_MENU_ICON = getattr(settings, 'WAGTAILMENUS_MAINMENU_MENU_ICON',
                             'list-ol')

FLATMENU_MENU_ICON = getattr(settings, 'WAGTAILMENUS_MAINMENU_MENU_ICON',
                             'list-ol')
