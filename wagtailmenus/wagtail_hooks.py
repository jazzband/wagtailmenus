from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from wagtailmodeladmin.options import ModelAdmin, wagtailmodeladmin_register
from wagtailmodeladmin.helpers import (
    get_url_pattern, get_object_specific_url_pattern, get_url_name)

from wagtail.wagtailcore import hooks

from .app_settings import MAINMENU_MENU_ICON, FLATMENU_MENU_ICON
from .models import MainMenu, FlatMenu
from .views import MainMenuIndexView, MainMenuEditView


class MainMenuAdmin(ModelAdmin):
    model = MainMenu
    menu_label = _('Main menu')
    menu_icon = MAINMENU_MENU_ICON
    index_view_class = MainMenuIndexView
    edit_view_class = MainMenuEditView
    add_to_settings_menu = True

    def get_admin_urls_for_registration(self):
        return (
            url(get_url_pattern(self.opts),
                self.index_view, name=get_url_name(self.opts)),
            url(get_object_specific_url_pattern(self.opts, 'edit'),
                self.edit_view, name=get_url_name(self.opts, 'edit')),
        )


class FlatMenuAdmin(ModelAdmin):
    model = FlatMenu
    menu_label = _('Flat menus')
    menu_icon = FLATMENU_MENU_ICON
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
