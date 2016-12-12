from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class Settings:

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

    @property
    def ACTIVE_CLASS(self):
        return getattr(settings, 'WAGTAILMENUS_ACTIVE_CLASS', 'active')

    @property
    def ADD_EDITOR_OVERRIDE_STYLES(self):
        return getattr(
            settings, 'WAGTAILMENUS_ADD_EDITOR_OVERRIDE_STYLES', True
        )

    @property
    def ACTIVE_ANCESTOR_CLASS(self):
        return getattr(
            settings, 'WAGTAILMENUS_ACTIVE_ANCESTOR_CLASS', 'ancestor'
        )

    @property
    def MAINMENU_MENU_ICON(self):
        return getattr(
            settings, 'WAGTAILMENUS_MAINMENU_MENU_ICON', 'list-ol'
        )

    @property
    def FLATMENU_MENU_ICON(self):
        return getattr(
            settings, 'WAGTAILMENUS_FLATMENU_MENU_ICON', 'list-ol'
        )

    @property
    def SECTION_ROOT_DEPTH(self):
        return getattr(
            settings, 'WAGTAILMENUS_SECTION_ROOT_DEPTH', 3
        )

    @property
    def GUESS_TREE_POSITION_FROM_PATH(self):
        return getattr(
            settings, 'WAGTAILMENUS_GUESS_TREE_POSITION_FROM_PATH', True
        )

    @property
    def FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS(self):
        return getattr(
            settings,
            'WAGTAILMENUS_FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS',
            False
        )

    @property
    def DEFAULT_MAIN_MENU_TEMPLATE(self):
        return getattr(
            settings,
            'WAGTAILMENUS_DEFAULT_MAIN_MENU_TEMPLATE',
            'menus/main_menu.html'
        )

    @property
    def DEFAULT_FLAT_MENU_TEMPLATE(self):
        return getattr(
            settings,
            'WAGTAILMENUS_DEFAULT_FLAT_MENU_TEMPLATE',
            'menus/flat_menu.html'
        )

    @property
    def DEFAULT_SECTION_MENU_TEMPLATE(self):
        return getattr(
            settings,
            'WAGTAILMENUS_DEFAULT_SECTION_MENU_TEMPLATE',
            'menus/section_menu.html'
        )

    @property
    def DEFAULT_CHILDREN_MENU_TEMPLATE(self):
        return getattr(
            settings,
            'WAGTAILMENUS_DEFAULT_CHILDREN_MENU_TEMPLATE',
            'menus/children_menu.html'
        )

    @property
    def DEFAULT_SUB_MENU_TEMPLATE(self):
        return getattr(
            settings,
            'WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE',
            'menus/sub_menu.html'
        )

    @property
    def DEFAULT_SECTION_MENU_MAX_LEVELS(self):
        return getattr(
            settings, 'WAGTAILMENUS_DEFAULT_SECTION_MENU_MAX_LEVELS', 2
        )

    @property
    def DEFAULT_CHILDREN_MENU_MAX_LEVELS(self):
        return getattr(
            settings, 'WAGTAILMENUS_DEFAULT_CHILDREN_MENU_MAX_LEVELS', 1
        )

    @property
    def DEFAULT_SECTION_MENU_USE_SPECIFIC(self):
        return getattr(
            settings,
            'WAGTAILMENUS_DEFAULT_SECTION_MENU_USE_SPECIFIC',
            self.USE_SPECIFIC_AUTO
        )

    @property
    def DEFAULT_CHILDREN_MENU_USE_SPECIFIC(self):
        return getattr(
            settings,
            'WAGTAILMENUS_DEFAULT_CHILDREN_MENU_USE_SPECIFIC',
            self.USE_SPECIFIC_AUTO
        )

    @property
    def FLAT_MENUS_HANDLE_CHOICES(self):
        return getattr(
            settings,
            'WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES',
            None
        )

    @property
    def PAGE_FIELD_FOR_MENU_ITEM_TEXT(self):
        return getattr(
            settings, "WAGTAILMENUS_PAGE_FIELD_FOR_MENU_ITEM_TEXT", 'title'
        )

    @property
    def MAIN_MENU_MODEL(self):
        return getattr(
            settings, 'WAGTAILMENUS_MAIN_MENU_MODEL', 'wagtailmenus.MainMenu'
        )

    @property
    def FLAT_MENU_MODEL(self):
        return getattr(
            settings, 'WAGTAILMENUS_FLAT_MENU_MODEL', 'wagtailmenus.FlatMenu'
        )

    @property
    def MAIN_MENU_ITEMS_RELATED_NAME(self):
        return getattr(
            settings, 'WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME', 'menu_items'
        )

    @property
    def FLAT_MENU_ITEMS_RELATED_NAME(self):
        return getattr(
            settings, 'WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME', 'menu_items'
        )
