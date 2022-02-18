# NOTE: All supported app settings must be added here

# --------------------
# REST Framework views
# --------------------

# Use the REST framework defaults by default
AUTHENTICATION_CLASSES = None

# Use the REST framework defaults by default
PERMISSION_CLASSES = None

# Use custom renderer by default. Override this setting to hide the browsable
# API in production
RENDERER_CLASSES = [
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]

# -------------------------
# Option serializer classes
# -------------------------

CHILDREN_MENU_OPTION_SERIALIZER = 'wagtailmenus.api.v1.serializers.ChildrenMenuOptionSerializer'

SECTION_MENU_OPTION_SERIALIZER = 'wagtailmenus.api.v1.serializers.SectionMenuOptionSerializer'

MAIN_MENU_OPTION_SERIALIZER = 'wagtailmenus.api.v1.serializers.MainMenuOptionSerializer'

FLAT_MENU_OPTION_SERIALIZER = 'wagtailmenus.api.v1.serializers.FlatMenuOptionSerializer'

# -----------------------
# Menu serializer classes
# -----------------------

CHILDREN_MENU_SERIALIZER = 'wagtailmenus.api.v1.serializers.ChildrenMenuSerializer'

SECTION_MENU_SERIALIZER = 'wagtailmenus.api.v1.serializers.SectionMenuSerializer'

MAIN_MENU_BASE_SERIALIZER = 'wagtailmenus.api.v1.serializers.BaseModelMenuSerializer'

FLAT_MENU_BASE_SERIALIZER = 'wagtailmenus.api.v1.serializers.BaseModelMenuSerializer'

# --------------
# View behaviour
# --------------

SINGLE_SITE_MODE = False

CURRENT_SITE_DERIVATION_FUNCTION = 'wagtailmenus.api.utils.derive_current_site'

CURRENT_PAGE_DERIVATION_FUNCTION = 'wagtailmenus.api.utils.derive_current_page'
