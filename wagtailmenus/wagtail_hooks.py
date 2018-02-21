from django.conf.urls import url
from django.contrib.admin.utils import quote
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from wagtail import VERSION as WAGTAIL_VERSION
if WAGTAIL_VERSION >= (2, 0):
    from wagtail.core import hooks
else:
    from wagtail.wagtailcore import hooks
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin.helpers import ButtonHelper

from . import app_settings, get_main_menu_model, get_flat_menu_model
from .views import (MainMenuIndexView, MainMenuEditView, FlatMenuCreateView,
                    FlatMenuEditView, FlatMenuCopyView)


class MainMenuAdmin(ModelAdmin):
    model = get_main_menu_model()
    menu_label = _('Main menu')
    menu_icon = app_settings.MAINMENU_MENU_ICON
    index_view_class = MainMenuIndexView
    edit_view_class = MainMenuEditView
    add_to_settings_menu = True

    def get_form_view_extra_css(self):
        if app_settings.ADD_EDITOR_OVERRIDE_STYLES:
            return ['wagtailmenus/css/menu-edit.css']
        return []

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


class FlatMenuButtonHelper(ButtonHelper):

    def copy_button(self, pk, classnames_add=[], classnames_exclude=[]):
        cn = self.finalise_classname(classnames_add, classnames_exclude)
        return {
            'url': self.url_helper.get_action_url('copy', quote(pk)),
            'label': _('Copy'),
            'classname': cn,
            'title': _('Copy this %(model_name)s') % {
                'model_name': self.verbose_name,
            },
        }

    def get_buttons_for_obj(self, obj, exclude=[], classnames_add=[],
                            classnames_exclude=[]):
        ph = self.permission_helper
        usr = self.request.user
        pk = quote(getattr(obj, self.opts.pk.attname))
        btns = super().get_buttons_for_obj(
            obj, exclude, classnames_add, classnames_exclude)
        if('copy' not in exclude and ph.user_can_create(usr)):
            btns.append(
                self.copy_button(pk, classnames_add, classnames_exclude)
            )
        return btns


class FlatMenuAdmin(ModelAdmin):
    model = get_flat_menu_model()
    menu_label = _('Flat menus')
    menu_icon = app_settings.FLATMENU_MENU_ICON
    button_helper_class = FlatMenuButtonHelper
    ordering = ('-site__is_default_site', 'site__hostname', 'handle')
    create_view_class = FlatMenuCreateView
    edit_view_class = FlatMenuEditView
    add_to_settings_menu = True

    def get_form_view_extra_css(self):
        if app_settings.ADD_EDITOR_OVERRIDE_STYLES:
            return ['wagtailmenus/css/menu-edit.css']
        return []

    def copy_view(self, request, instance_pk):
        kwargs = {'model_admin': self, 'instance_pk': instance_pk}
        return FlatMenuCopyView.as_view(**kwargs)(request)

    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        urls += (
            url(self.url_helper.get_action_url_pattern('copy'),
                self.copy_view,
                name=self.url_helper.get_action_url_name('copy')),
        )
        return urls

    def get_list_filter(self, request):
        if self.is_multisite_listing(request):
            return ('site', 'handle')
        return ()

    def get_list_display(self, request):
        if self.is_multisite_listing(request):
            return ('title', 'handle_formatted', 'site', 'items')
        return ('title', 'handle_formatted', 'items')

    def handle_formatted(self, obj):
        return mark_safe('<code>%s</code>' % obj.handle)
    handle_formatted.short_description = _('handle')
    handle_formatted.admin_order_field = 'handle'

    def is_multisite_listing(self, request):
        return self.get_queryset(request).values('site').distinct().count() > 1

    def items(self, obj):
        return obj.get_menu_items_manager().count()
    items.short_description = _('no. of items')


modeladmin_register(FlatMenuAdmin)


@hooks.register('before_serve_page')
def wagtailmenu_params_helper(page, request, serve_args, serve_kwargs):
    section_root = request.site.root_page.get_descendants().ancestor_of(
        page, inclusive=True
    ).filter(depth__exact=app_settings.SECTION_ROOT_DEPTH).first()
    if section_root:
        section_root = section_root.specific
    ancestor_ids = page.get_ancestors().filter(
        depth__gte=app_settings.SECTION_ROOT_DEPTH
    ).values_list('id', flat=True)
    request.META.update({
        'WAGTAILMENUS_CURRENT_SECTION_ROOT': section_root,
        'WAGTAILMENUS_CURRENT_PAGE': page,
        'WAGTAILMENUS_CURRENT_PAGE_ANCESTOR_IDS': ancestor_ids,
    })
