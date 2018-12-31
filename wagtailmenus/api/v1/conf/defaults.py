# NOTE: All supported app settings must be added here

# -----------------------
# Menu serializer classes
# -----------------------

# A ``None`` value means  "Use the default serializer class for the
# version of the API I'm using". Because this can vary between versions,
# default values are not added here.

CHILDREN_MENU_SERIALIZER = None

FLAT_MENU_SERIALIZER = None

MAIN_MENU_SERIALIZER = None

SECTION_MENU_SERIALIZER = None


# ----------------------------
# Menu item serializer classes
# ----------------------------

# A ``None`` value means  "Use the default serializer class for the
# version of the API being used". Because this can vary between versions,
# default values are not added here.

FLAT_MENU_ITEM_SERIALIZER = None

MAIN_MENU_ITEM_SERIALIZER = None

SECTION_MENU_ITEM_SERIALIZER = None

CHILDREN_MENU_ITEM_SERIALIZER = None


# -----------------------
# Page serializer classes
# -----------------------

PARENT_PAGE_SERIALIZER = None

SECTION_ROOT_SERIALIZER = None

MENU_ITEM_PAGE_SERIALIZER = None


# -----------------------------------
# Default menu item serializer fields
# -----------------------------------

MENU_ITEM_SERIALIZER_FIELDS = ('text', 'href', 'active_class', 'page', 'children')

FLAT_MENU_ITEM_SERIALIZER_FIELDS = None

MAIN_MENU_ITEM_SERIALIZER_FIELDS = None

SECTION_MENU_ITEM_SERIALIZER_FIELDS = None

CHILDREN_MENU_ITEM_SERIALIZER_FIELDS = None

# ------------------------------
# Default page serializer fields
# ------------------------------

PARENT_PAGE_SERIALIZER_FIELDS = None

SECTION_ROOT_SERIALIZER_FIELDS = None

MENU_ITEM_PAGE_SERIALIZER_FIELDS = ('id', 'title', 'slug', 'type')

MAIN_MENU_ITEM_PAGE_SERIALIZER_FIELDS = None

FLAT_MENU_ITEM_PAGE_SERIALIZER_FIELDS = None

CHILDREN_MENU_ITEM_PAGE_SERIALIZER_FIELDS = None

SECTION_MENU_ITEM_PAGE_SERIALIZER_FIELDS = None
