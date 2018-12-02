# NOTE: All supported app settings must be added here


# -------------------------
# Menu object serialization
# -------------------------

MAIN_MENU_FIELDS = ('site', 'items')

FLAT_MENU_FIELDS = ('site', 'handle', 'title', 'heading', 'items')


# -----------------------
# Menu item serialization
# -----------------------

MENU_ITEM_FIELDS = ('text', 'href', 'active_class', 'page', 'children')

FLAT_MENU_ITEM_FIELDS = ('text', 'href', 'handle', 'active_class', 'page', 'children')

MAIN_MENU_ITEM_FIELDS = ('text', 'href', 'handle', 'active_class', 'page', 'children')


# ------------------
# Page serialization
# ------------------

default_page_fields = ('id', 'title', 'slug', 'type')

SECTION_ROOT_PAGE_FIELDS = default_page_fields

PARENT_PAGE_FIELDS = default_page_fields

MENU_ITEM_PAGE_FIELDS = default_page_fields

MAIN_MENU_ITEM_PAGE_FIELDS = default_page_fields

FLAT_MENU_ITEM_PAGE_FIELDS = default_page_fields


# ----------
# Deprecated
# ----------
