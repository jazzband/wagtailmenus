from __future__ import unicode_literals
from copy import copy

from django.template import Library

from wagtailmenus import app_settings
from wagtailmenus.templatetags.menu_tags import get_sub_menu_items_for_page
from wagtailmenus.utils.misc import (
    get_attrs_from_context, validate_supplied_values
)
from wagtailmenus.tests.models import OldStyleChildrenMenu
from wagtailmenus.utils.template import (
    get_template_names, get_sub_menu_template_names
)

register = Library()


@register.simple_tag(takes_context=True)
def custom_children_menu(
    context, parent_page=None, allow_repeating_parents=True,
    apply_active_classes=False,
    max_levels=app_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS,
    template='', sub_menu_template='',
    use_specific=app_settings.DEFAULT_CHILDREN_MENU_USE_SPECIFIC,
    use_absolute_page_urls=False,
):
    validate_supplied_values(
        'children_menu', max_levels=max_levels, use_specific=use_specific,
        parent_page=parent_page)

    request, site, current_page, root, ancestor_ids = get_attrs_from_context(
        context)

    # Use current page as parent_page if no value supplied
    if parent_page is None:
        parent_page = current_page or site.root_page

    # Create a menu instance that can fetch all pages at once and return
    # for subpages for each branch as they are needed
    menu_instance = OldStyleChildrenMenu(parent_page, max_levels, use_specific)
    menu_instance.set_request(request)

    parent_page, menu_items = get_sub_menu_items_for_page(
        request=request,
        page=parent_page,
        current_site=site,
        current_page=current_page,
        ancestor_ids=ancestor_ids,
        menu_instance=menu_instance,
        use_specific=use_specific,
        original_menu_tag='children_menu',
        current_level=1,
        max_levels=max_levels,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents,
        use_absolute_page_urls=use_absolute_page_urls,
    )

    # Identify templates for rendering
    template_names = get_template_names('children', request, template)
    t = context.template.engine.select_template(template_names)
    sub_template_names = get_sub_menu_template_names('children', request,
                                                     sub_menu_template)
    submenu_t = context.template.engine.select_template(sub_template_names)

    # Prepare context and render
    c = copy(context)
    c.update({
        'parent_page': parent_page,
        'menu_instance': menu_instance,
        'menu_items': menu_items,
        'apply_active_classes': apply_active_classes,
        'allow_repeating_parents': allow_repeating_parents,
        'current_level': 1,
        'max_levels': max_levels,
        'original_menu_tag': 'children_menu',
        'current_template': t.name,
        'sub_menu_template': submenu_t.name,
        'use_specific': use_specific,
        'use_absolute_page_urls': use_absolute_page_urls,
    })
    return t.render(c)
