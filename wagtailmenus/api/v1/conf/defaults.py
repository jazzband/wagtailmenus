# NOTE: All supported app settings must be added here

# -----------------------
# Menu serializer classes
# -----------------------

BASE_MAIN_MENU_SERIALIZER = 'wagtailmenus.api.v1.serializers.BaseModelMenuSerializer'

BASE_FLAT_MENU_SERIALIZER = 'wagtailmenus.api.v1.serializers.BaseModelMenuSerializer'

CHILDREN_MENU_SERIALIZER = 'wagtailmenus.api.v1.serializers.ChildrenMenuSerializer'

SECTION_MENU_SERIALIZER = 'wagtailmenus.api.v1.serializers.SectionMenuSerializer'


# ----------------------------
# Util methods
# ----------------------------

CURRENT_SITE_DERIVATION_FUNCTION = 'wagtailmenus.api.utils.derive_current_site'

CURRENT_PAGE_DERIVATION_FUNCTION = 'wagtailmenus.api.utils.derive_current_page'
