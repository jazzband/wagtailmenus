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
    'wagtailmenus.api.v1.renderers.BrowsableAPIWithArgumentFormRenderer',
]


# -----------------------
# Menu serializer classes
# -----------------------

CHILDREN_MENU_SERIALIZER = 'wagtailmenus.api.v1.serializers.ChildrenMenuSerializer'

SECTION_MENU_SERIALIZER = 'wagtailmenus.api.v1.serializers.SectionMenuSerializer'


# --------------
# View behaviour
# --------------

SINGLE_SITE_MODE = False

CURRENT_SITE_DERIVATION_FUNCTION = 'wagtailmenus.api.utils.derive_current_site'

CURRENT_PAGE_DERIVATION_FUNCTION = 'wagtailmenus.api.utils.derive_current_page'
