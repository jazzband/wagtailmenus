# NOTE: All supported app settings must be added here

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
