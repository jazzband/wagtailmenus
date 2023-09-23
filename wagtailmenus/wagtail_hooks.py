from wagtail import hooks
try:
    from wagtail_modeladmin.options import modeladmin_register
except ModuleNotFoundError:
    from wagtail.contrib.modeladmin.options import modeladmin_register

from wagtailmenus.conf import settings
from wagtailmenus.utils.misc import derive_section_root

if settings.MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN:
    modeladmin_register(settings.objects.MAIN_MENUS_MODELADMIN_CLASS)


if settings.FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN:
    modeladmin_register(settings.objects.FLAT_MENUS_MODELADMIN_CLASS)


@hooks.register('before_serve_page')
def wagtailmenu_params_helper(page, request, serve_args, serve_kwargs):
    request.META.update({
        'WAGTAILMENUS_CURRENT_PAGE': page,
        'WAGTAILMENUS_CURRENT_SECTION_ROOT': derive_section_root(page),
    })
