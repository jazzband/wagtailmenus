from wagtail.wagtailcore import hooks
from django.utils.translation import ugettext_lazy as _
from wagtailmodeladmin.options import ModelAdmin, wagtailmodeladmin_register
from .models import MainMenu, FlatMenu


class MainMenuAdmin(ModelAdmin):
    model = MainMenu
    menu_label = _('Main menu')
    menu_icon = 'link'
    list_filter = ('site', )
    add_to_settings_menu = True


class FlatMenuAdmin(ModelAdmin):
    model = FlatMenu
    menu_label = _('Flat menus')
    menu_icon = 'list-ol'
    list_display = ('title', 'handle', )
    list_filter = ('site', )
    add_to_settings_menu = True

wagtailmodeladmin_register(MainMenuAdmin)
wagtailmodeladmin_register(FlatMenuAdmin)


@hooks.register('before_serve_page')
def wagtailmenu_params_helper(page, request, serve_args, serve_kwargs):
    section_root = request.site.root_page.get_children().ancestor_of(
        page, inclusive=True).first()
    if section_root:
        section_root = section_root.specific
    ancestor_ids = page.get_ancestors().values_list('id', flat=True)
    request.META.update({
        'CURRENT_SECTION_ROOT': section_root,
        'CURRENT_PAGE_ANCESTOR_IDS': ancestor_ids,
    })
