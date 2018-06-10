import sys
from wagtailmenus.constants import USE_SPECIFIC_AUTO
from wagtailmenus.utils.conf import AppSettings
from wagtailmenus.utils.deprecation import RemovedInWagtailMenus212Warning

# All supported app settings must be added to the following dictionary
defaults = dict(
    ACTIVE_CLASS='active',
    ADD_EDITOR_OVERRIDE_STYLES=True,
    ACTIVE_ANCESTOR_CLASS='ancestor',
    MAINMENU_MENU_ICON='list-ol',
    FLATMENU_MENU_ICON='list-ol',
    USE_CONDENSEDINLINEPANEL=True,
    SITE_SPECIFIC_TEMPLATE_DIRS=False,
    SECTION_ROOT_DEPTH=3,
    GUESS_TREE_POSITION_FROM_PATH=True,
    FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS=False,
    DEFAULT_MAIN_MENU_TEMPLATE='menus/main_menu.html',
    DEFAULT_FLAT_MENU_TEMPLATE='menus/flat_menu.html',
    DEFAULT_SECTION_MENU_TEMPLATE='menus/section_menu.html',
    DEFAULT_CHILDREN_MENU_TEMPLATE='menus/children_menu.html',
    DEFAULT_SUB_MENU_TEMPLATE='menus/sub_menu.html',
    DEFAULT_SECTION_MENU_MAX_LEVELS=2,
    DEFAULT_CHILDREN_MENU_MAX_LEVELS=1,
    DEFAULT_SECTION_MENU_USE_SPECIFIC=USE_SPECIFIC_AUTO,
    DEFAULT_CHILDREN_MENU_USE_SPECIFIC=USE_SPECIFIC_AUTO,
    PAGE_FIELD_FOR_MENU_ITEM_TEXT='title',
    MAIN_MENU_MODEL='wagtailmenus.MainMenu',
    FLAT_MENU_MODEL='wagtailmenus.FlatMenu',
    MAIN_MENU_ITEMS_RELATED_NAME='menu_items',
    FLAT_MENU_ITEMS_RELATED_NAME='menu_items',
    FLAT_MENUS_HANDLE_CHOICES=None,
    CHILDREN_MENU_CLASS='wagtailmenus.models.ChildrenMenu',
    SECTION_MENU_CLASS='wagtailmenus.models.SectionMenu',
    MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN=True,
    MAIN_MENU_MODELADMIN_CLASS='wagtailmenus.modeladmin.MainMenuAdmin',
    FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN=True,
    FLAT_MENU_MODELADMIN_CLASS='wagtailmenus.modeladmin.FlatMenuAdmin',
)


class WagtailmenusAppSettings(AppSettings):

    @property
    def SECTION_MENU_CLASS(self):
        return self.get_or_try_deprecated_name(
            'SECTION_MENU_CLASS',
            'SECTION_MENU_CLASS_PATH',
            warning_category=RemovedInWagtailMenus212Warning
        )

    @property
    def CHILDREN_MENU_CLASS(self):
        return self.get_or_try_deprecated_name(
            'CHILDREN_MENU_CLASS',
            'CHILDREN_MENU_CLASS_PATH',
            warning_category=RemovedInWagtailMenus212Warning
        )

sys.modules[__name__] = WagtailmenusAppSettings('WAGTAILMENUS_', defaults)
