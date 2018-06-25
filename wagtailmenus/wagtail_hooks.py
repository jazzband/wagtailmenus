from wagtail.core import hooks
from wagtail.contrib.modeladmin.options import modeladmin_register

from wagtailmenus.conf import settings
from wagtailmenus.modeladmin import ( # noqa
    MainMenuAdmin, FlatMenuAdmin, FlatMenuButtonHelper
)

if settings.MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN:
    modeladmin_register(settings.objects.MAIN_MENUS_MODELADMIN_CLASS)


if settings.FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN:
    modeladmin_register(settings.objects.FLAT_MENUS_MODELADMIN_CLASS)


@hooks.register('before_serve_page')
def wagtailmenu_params_helper(page, request, serve_args, serve_kwargs):
    section_root = request.site.root_page.get_descendants().ancestor_of(
        page, inclusive=True
    ).filter(depth__exact=settings.SECTION_ROOT_DEPTH).first()
    if section_root:
        section_root = section_root.specific
    ancestor_ids = page.get_ancestors().filter(
        depth__gte=settings.SECTION_ROOT_DEPTH
    ).values_list('id', flat=True)
    request.META.update({
        'WAGTAILMENUS_CURRENT_SECTION_ROOT': section_root,
        'WAGTAILMENUS_CURRENT_PAGE': page,
        'WAGTAILMENUS_CURRENT_PAGE_ANCESTOR_IDS': ancestor_ids,
    })
