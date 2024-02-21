# NOTE: All supported app settings must be added here


# -------------------
# Admin / UI settings
# -------------------

FLATMENU_MENU_ICON = 'list-ol'

FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN = True

FLAT_MENUS_ADMIN_CLASS = 'wagtailmenus.menuadmin.FlatMenuAdmin'

FLAT_MENUS_HANDLE_CHOICES = None

MAINMENU_MENU_ICON = 'list-ol'

MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN = True

MAIN_MENUS_ADMIN_CLASS = 'wagtailmenus.menuadmin.MainMenuAdmin'

USE_CONDENSEDINLINEPANEL = True


# ----------------------------------------------
# Default templates and template finder settings
# ----------------------------------------------

DEFAULT_CHILDREN_MENU_TEMPLATE = 'menus/children_menu.html'

DEFAULT_FLAT_MENU_TEMPLATE = 'menus/flat_menu.html'

DEFAULT_MAIN_MENU_TEMPLATE = 'menus/main_menu.html'

DEFAULT_SECTION_MENU_TEMPLATE = 'menus/section_menu.html'

DEFAULT_SUB_MENU_TEMPLATE = 'menus/sub_menu.html'

SITE_SPECIFIC_TEMPLATE_DIRS = False


# ------------------------------
# Default tag behaviour settings
# ------------------------------

DEFAULT_CHILDREN_MENU_MAX_LEVELS = 1

DEFAULT_SECTION_MENU_MAX_LEVELS = 2

DEFAULT_ADD_SUB_MENUS_INLINE = False

FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS = False

GUESS_TREE_POSITION_FROM_PATH = True


# --------------------------------------
# Menu class and model override settings
# --------------------------------------

CHILDREN_MENU_CLASS = 'wagtailmenus.models.ChildrenMenu'

FLAT_MENU_MODEL = 'wagtailmenus.FlatMenu'

FLAT_MENU_ITEMS_RELATED_NAME = 'menu_items'

MAIN_MENU_MODEL = 'wagtailmenus.MainMenu'

MAIN_MENU_ITEMS_RELATED_NAME = 'menu_items'

SECTION_MENU_CLASS = 'wagtailmenus.models.SectionMenu'


# ----------------------
# Miscellaneous settings
# ----------------------

ACTIVE_CLASS = 'active'

ACTIVE_ANCESTOR_CLASS = 'ancestor'

PAGE_FIELD_FOR_MENU_ITEM_TEXT = 'title'

SECTION_ROOT_DEPTH = 3


# ----------
# Deprecated
# ----------

ADD_EDITOR_OVERRIDE_STYLES = True
