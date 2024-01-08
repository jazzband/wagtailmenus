from wagtail import hooks
from wagtail.snippets.models import register_snippet

from wagtailmenus.conf import settings
from wagtailmenus.utils.misc import derive_section_root

if settings.MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN:
    register_snippet(settings.objects.MAIN_MENUS_ADMIN_CLASS)

if settings.FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN:
    register_snippet(settings.objects.FLAT_MENUS_ADMIN_CLASS)


@hooks.register('before_serve_page')
def wagtailmenu_params_helper(page, request, serve_args, serve_kwargs):
    request.META.update({
        'WAGTAILMENUS_CURRENT_PAGE': page,
        'WAGTAILMENUS_CURRENT_SECTION_ROOT': derive_section_root(page),
    })
