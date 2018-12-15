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

FLAT_MENU_ITEM_SERIALIZER_FIELDS = ('text', 'href', 'handle', 'active_class', 'page', 'children')

MENU_ITEM_SERIALIZER_FIELDS = ('text', 'href', 'active_class', 'page', 'children')

MAIN_MENU_ITEM_SERIALIZER_FIELDS = ('text', 'href', 'handle', 'active_class', 'page', 'children')


# ------------------------------
# Default page serializer fields
# ------------------------------

PARENT_PAGE_SERIALIZER_FIELDS = ('id', 'title', 'slug', 'type')

SECTION_ROOT_SERIALIZER_FIELDS = ('text', 'href', 'active_class', 'page')

MENU_ITEM_PAGE_SERIALIZER_FIELDS = ('id', 'title', 'slug', 'type')
