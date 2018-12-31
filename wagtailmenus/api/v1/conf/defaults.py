# NOTE: All supported app settings must be added here

# -----------------------
# Menu serializer classes
# -----------------------

CHILDREN_MENU_SERIALIZER = 'wagtailmenus.api.v1.serializers.ChildrenMenuSerializer'

FLAT_MENU_SERIALIZER = 'wagtailmenus.api.v1.serializers.FlatMenuSerializer'

MAIN_MENU_SERIALIZER = 'wagtailmenus.api.v1.serializers.MainMenuSerializer'

SECTION_MENU_SERIALIZER = 'wagtailmenus.api.v1.serializers.SectionMenuSerializer'


# ----------------------------
# Menu item serializer classes
# ----------------------------

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
