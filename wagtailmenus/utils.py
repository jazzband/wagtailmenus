from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailcore.models import Page
from .models import MenuItem
from . import app_settings


def get_attrs_from_context(context, guess_tree_position=True):
    """
    Gets a bunch of useful things from the context/request and returns them as
    a tuple for use in most menu tags.
    """
    request = context['request']
    site = request.site
    wagtailmenus_vals = context.get('wagtailmenus_vals')
    current_page = wagtailmenus_vals.get('current_page')
    section_root = wagtailmenus_vals.get('section_root')
    ancestor_ids = wagtailmenus_vals.get('current_page_ancestor_ids')
    return (request, site, current_page, section_root, ancestor_ids)


def get_template_names(menu_tag, request, override):
    if override:
        return [override]
    template_names = []
    if app_settings.SITE_SPECIFIC_TEMPLATE_DIRS and getattr(
        request, 'site', None
    ):
        hostname = request.site.hostname
        template_names.extend([
            "menus/%s/%s/menu.html" % (hostname, menu_tag),
            "menus/%s/%s_menu.html" % (hostname, menu_tag),
        ])
    template_names.append("menus/%s/menu.html" % menu_tag)
    if menu_tag == 'main':
        template_names.append(app_settings.DEFAULT_MAIN_MENU_TEMPLATE)
    elif menu_tag == 'section':
        template_names.append(app_settings.DEFAULT_SECTION_MENU_TEMPLATE)
    elif menu_tag == 'children':
        template_names.append(app_settings.DEFAULT_CHILDREN_MENU_TEMPLATE)
    return template_names


def get_sub_menu_template_names(menu_tag, request, override):
    if override:
        return [override]
    template_names = []
    if app_settings.SITE_SPECIFIC_TEMPLATE_DIRS and getattr(
        request, 'site', None
    ):
        hostname = request.site.hostname
        template_names.extend([
            "menus/%s/%s/sub_menu.html" % (hostname, menu_tag),
            "menus/%s/%s_sub_menu.html" % (hostname, menu_tag),
            "menus/%s/sub_menu.html" % hostname,
        ])
    template_names.extend([
        "menus/%s/sub_menu.html" % menu_tag,
        "menus/%s_sub_menu.html" % menu_tag,
        app_settings.DEFAULT_SUB_MENU_TEMPLATE,
    ])
    return template_names


def validate_supplied_values(tag, max_levels=None, use_specific=None,
                             parent_page=None, menuitem_or_page=None):
    if max_levels is not None:
        if max_levels not in (1, 2, 3, 4, 5):
            raise ValueError(_(
                "The `%s` tag expects `max_levels` to be an integer value "
                "between 1 and 5. Please review your template.") % tag)
    if use_specific is not None:
        if use_specific not in (0, 1, 2, 3):
            raise ValueError(_(
                "The `%s` tag expects `use_specific` to be an integer value "
                "between 0 and 3. Please review your template.") % tag)
    if parent_page is not None:
        if not isinstance(parent_page, Page):
            raise ValueError(_(
                "The `%s` tag expects `parent_page` to be a `Page` instance. "
                "A value of type `%s` was supplied.") %
                (tag, parent_page.__class__))
    if menuitem_or_page is not None:
        if not isinstance(menuitem_or_page, (Page, MenuItem)):
            raise ValueError(_(
                "The `%s` tag expects `menuitem_or_page` to be a `Page` or "
                "`MenuItem` instance. A value of type `%s` was supplied.") %
                (tag, menuitem_or_page.__class__))
