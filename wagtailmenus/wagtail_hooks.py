from django.conf.urls import url
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.wagtailcore import hooks

from .app_settings import (
    MAINMENU_MENU_ICON, FLATMENU_MENU_ICON, SECTION_ROOT_DEPTH)
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
            url(self.url_helper.get_action_url_pattern('index'),
                self.index_view,
                name=self.url_helper.get_action_url_name('index')),
            url(self.url_helper.get_action_url_pattern('edit'),
                self.edit_view,
                name=self.url_helper.get_action_url_name('edit')),
        )

modeladmin_register(MainMenuAdmin)


class FlatMenuAdmin(ModelAdmin):
    model = FlatMenu
    menu_label = _('Flat menus')
    menu_icon = FLATMENU_MENU_ICON
    list_display = ('title', 'handle_formatted', 'site', 'items')
    list_filter = ('site', 'handle')
    ordering = ('-site__is_default_site', 'site__hostname', 'handle')
    add_to_settings_menu = True

    def handle_formatted(self, obj):
        return mark_safe('<code>%s</code>' % obj.handle)
    handle_formatted.short_description = 'handle'
    handle_formatted.admin_order_field = 'handle'

    def items(self, obj):
        return obj.menu_items.count()
    items.short_description = _('no. of items')


modeladmin_register(FlatMenuAdmin)


@hooks.register('before_serve_page')
def wagtailmenu_params_helper(page, request, serve_args, serve_kwargs):
    section_root = request.site.root_page.get_descendants().ancestor_of(
        page, inclusive=True).filter(depth__exact=SECTION_ROOT_DEPTH).first()
    if section_root:
        section_root = section_root.specific
    ancestor_ids = page.get_ancestors().values_list('id', flat=True)
    request.META.update({
        'CURRENT_SECTION_ROOT': section_root,
        'CURRENT_PAGE_ANCESTOR_IDS': ancestor_ids,
    })
