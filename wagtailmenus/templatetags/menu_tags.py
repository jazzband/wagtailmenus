from __future__ import unicode_literals
import warnings

from django.template import Library
from wagtail.wagtailcore.models import Page

from wagtailmenus import app_settings
from ..errors import SubMenuUsageError
from ..models import AbstractLinkPage, MenuItem, SubMenu
from ..utils.deprecation import RemovedInWagtailMenus27Warning
from ..utils.misc import validate_supplied_values

flat_menus_fbtdsm = app_settings.FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS

register = Library()


@register.simple_tag(takes_context=True)
def main_menu(
    context, max_levels=None, use_specific=None, apply_active_classes=True,
    allow_repeating_parents=True, show_multiple_levels=True,
    template='', sub_menu_template='', use_absolute_page_urls=False, **kwargs
):
    validate_supplied_values('main_menu', max_levels=max_levels,
                             use_specific=use_specific)

    if not show_multiple_levels:
        max_levels = 1

    return app_settings.MAIN_MENU_MODEL_CLASS.render_from_tag(
        context=context,
        max_levels=max_levels,
        use_specific=use_specific,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents,
        use_absolute_page_urls=use_absolute_page_urls,
        template_name=template,
        sub_menu_template_name=sub_menu_template,
        **kwargs
    )


@register.simple_tag(takes_context=True)
def flat_menu(
    context, handle, max_levels=None, use_specific=None,
    show_menu_heading=False, apply_active_classes=False,
    allow_repeating_parents=True, show_multiple_levels=True,
    template='', sub_menu_template='',
    fall_back_to_default_site_menus=flat_menus_fbtdsm,
    use_absolute_page_urls=False, **kwargs
):
    validate_supplied_values('flat_menu', max_levels=max_levels,
                             use_specific=use_specific)

    if not show_multiple_levels:
        max_levels = 1

    return app_settings.FLAT_MENU_MODEL_CLASS.render_from_tag(
        context=context,
        handle=handle,
        fall_back_to_default_site_menus=fall_back_to_default_site_menus,
        max_levels=max_levels,
        use_specific=use_specific,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents,
        use_absolute_page_urls=use_absolute_page_urls,
        template_name=template,
        sub_menu_template_name=sub_menu_template,
        show_menu_heading=show_menu_heading,
        **kwargs
    )


@register.simple_tag(takes_context=True)
def section_menu(
    context, show_section_root=True, show_multiple_levels=True,
    apply_active_classes=True, allow_repeating_parents=True,
    max_levels=app_settings.DEFAULT_SECTION_MENU_MAX_LEVELS,
    template='', sub_menu_template='',
    use_specific=app_settings.DEFAULT_SECTION_MENU_USE_SPECIFIC,
    use_absolute_page_urls=False, **kwargs
):
    """Render a section menu for the current section."""

    validate_supplied_values('section_menu', max_levels=max_levels,
                             use_specific=use_specific)

    if not show_multiple_levels:
        max_levels = 1

    return app_settings.SECTION_MENU_CLASS.render_from_tag(
        context=context,
        max_levels=max_levels,
        use_specific=use_specific,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents,
        use_absolute_page_urls=use_absolute_page_urls,
        template_name=template,
        sub_menu_template_name=sub_menu_template,
        show_section_root=show_section_root,
        **kwargs
    )


@register.simple_tag(takes_context=True)
def children_menu(
    context, parent_page=None, allow_repeating_parents=True,
    apply_active_classes=False,
    max_levels=app_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS,
    template='', sub_menu_template='',
    use_specific=app_settings.DEFAULT_CHILDREN_MENU_USE_SPECIFIC,
    use_absolute_page_urls=False, **kwargs
):
    validate_supplied_values(
        'children_menu', max_levels=max_levels, use_specific=use_specific,
        parent_page=parent_page)

    return app_settings.CHILDREN_MENU_CLASS.render_from_tag(
        context=context,
        parent_page=parent_page,
        max_levels=max_levels,
        use_specific=use_specific,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents,
        use_absolute_page_urls=use_absolute_page_urls,
        template_name=template,
        sub_menu_template_name=sub_menu_template,
        **kwargs
    )


@register.simple_tag(takes_context=True)
def sub_menu(
    context, menuitem_or_page, stop_at_this_level=None, use_specific=None,
    allow_repeating_parents=None, apply_active_classes=None, template='',
    use_absolute_page_urls=None, **kwargs
):
    """
    Retrieve the children pages for the `menuitem_or_page` provided, turn them
    into menu items, and render them to a template.
    """
    validate_supplied_values('sub_menu', use_specific=use_specific,
                             menuitem_or_page=menuitem_or_page)

    if stop_at_this_level is not None:
        warning_msg = (
            "The 'stop_at_this_level' argument for 'sub_menu' no longer "
            "has any effect on output and is deprecated. View the 2.5 release "
            "notes for more info: "
            "http://wagtailmenus.readthedocs.io/en/stable/releases/2.5.0.html"
        )
        warnings.warn(warning_msg, RemovedInWagtailMenus27Warning)

    max_levels = context.get(
        'max_levels', app_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS
    )

    if use_specific is None:
        use_specific = context.get(
            'use_specific', app_settings.USE_SPECIFIC_AUTO)

    if apply_active_classes is None:
        apply_active_classes = context.get('apply_active_classes', True)

    if allow_repeating_parents is None:
        allow_repeating_parents = context.get('allow_repeating_parents', True)

    if use_absolute_page_urls is None:
        use_absolute_page_urls = context.get('use_absolute_page_urls', False)

    if isinstance(menuitem_or_page, Page):
        parent_page = menuitem_or_page
    else:
        parent_page = menuitem_or_page.link_page

    original_menu = context.get('original_menu_instance')
    if not original_menu:
        raise SubMenuUsageError()

    menu_class = original_menu.get_sub_menu_class() or SubMenu

    return menu_class.render_from_tag(
        context=context,
        parent_page=parent_page,
        max_levels=max_levels,
        use_specific=use_specific,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents,
        use_absolute_page_urls=use_absolute_page_urls,
        template_name=template,
        **kwargs
    )


def get_sub_menu_items_for_page(
    request, page, current_site, current_page, ancestor_ids, menu_instance,
    use_specific, apply_active_classes, allow_repeating_parents,
    current_level=1, max_levels=2, original_menu_tag='',
    use_absolute_page_urls=False,
):
    warning_msg = (
        "The 'get_sub_menu_items_for_page' method in templatetags.menu_tags "
        "is deprecated in favour of rendering behaviour being built into Menu "
        "classes"
    )
    warnings.warn(warning_msg, RemovedInWagtailMenus27Warning)

    # The menu items will be the children of the provided `page`
    children_pages = menu_instance.get_children_for_page(page)

    # Call `prime_menu_items` to prepare the children pages for output. This
    # will add `href`, `text`, `active_class` and `has_children_in_menu`
    # attributes to each item, to use in menu templates.
    menu_items = prime_menu_items(
        request=request,
        menu_items=children_pages,
        current_site=current_site,
        current_page=current_page,
        current_page_ancestor_ids=ancestor_ids,
        use_specific=use_specific,
        original_menu_tag=original_menu_tag,
        menu_instance=menu_instance,
        check_for_children=current_level < max_levels,
        allow_repeating_parents=allow_repeating_parents,
        apply_active_classes=apply_active_classes,
        use_absolute_page_urls=use_absolute_page_urls,
    )

    """
    If `page` has a `modify_submenu_items` method, send the primed
    menu_items list to that for further modification (e.g. adding a copy of
    `page` as the first item, using fields from `MenuPage`)
    """
    if (
        use_specific and (
            hasattr(page, 'modify_submenu_items') or
            hasattr(page.specific_class, 'modify_submenu_items')
        )
    ):
        if type(page) is Page:
            page = page.specific

        # Call `modify_submenu_items` using the above kwargs dict
        menu_items = page.modify_submenu_items(
            menu_items=menu_items,
            current_page=current_page,
            current_ancestor_ids=ancestor_ids,
            current_site=current_site,
            allow_repeating_parents=allow_repeating_parents,
            apply_active_classes=apply_active_classes,
            original_menu_tag=original_menu_tag,
            menu_instance=menu_instance,
            use_absolute_page_urls=use_absolute_page_urls,
            request=request,
        )

    return page, menu_items


def prime_menu_items(
    request, menu_items, current_site, current_page, current_page_ancestor_ids,
    use_specific, original_menu_tag, menu_instance, check_for_children=False,
    allow_repeating_parents=True, apply_active_classes=True,
    use_absolute_page_urls=False,
):
    """
    Prepare a list of `MenuItem` or `Page` objects for rendering to a menu
    template.
    """
    warning_msg = (
        "The 'prime_menu_items' method in templatetags.menu_tags is "
        "deprecated in favour of rendering behaviour being built into Menu "
        "classes"
    )
    warnings.warn(warning_msg, RemovedInWagtailMenus27Warning)

    primed_menu_items = []

    for item in menu_items:

        if isinstance(item, MenuItem):
            """
            `menu_items` is a list of `MenuItem` objects from
            `Menu.top_level_items`. Any `link_page` values will have been
            replaced with specific pages if necessary
            """
            page = item.link_page
            menuitem = item
            setattr(item, 'text', item.menu_text)

        elif issubclass(item.specific_class, AbstractLinkPage):
            """
            Special treatment for link pages
            """
            if type(item) is Page:
                item = item.specific
            if item.show_in_menus_custom(
                request, current_site, menu_instance, original_menu_tag
            ):
                setattr(item, 'active_class', item.extra_classes)
                setattr(item, 'text', item.menu_text(request))
                if use_absolute_page_urls:
                    url = item.get_full_url(request=request)
                else:
                    url = item.relative_url(current_site, request)
                setattr(item, 'href', url)
                primed_menu_items.append(item)
            continue

        else:
            """
            `menu_items` is a list of `Page` objects
            """
            page = item
            menuitem = None
            text = getattr(
                page, app_settings.PAGE_FIELD_FOR_MENU_ITEM_TEXT, page.title
            )
            setattr(item, 'text', text)

        if page:
            """
            Work out whether this item should be flagged as needing
            a sub-menu. It can be expensive, so we try to only do the working
            out when absolutely necessary.
            """
            has_children_in_menu = False
            if (
                check_for_children and
                page.depth >= app_settings.SECTION_ROOT_DEPTH and
                (menuitem is None or menuitem.allow_subnav)
            ):
                if (
                    use_specific and (
                        hasattr(page, 'has_submenu_items') or
                        hasattr(page.specific_class, 'has_submenu_items')
                    )
                ):
                    if type(page) is Page:
                        page = page.specific
                    """
                    If the page has a `has_submenu_items` method, give
                    responsibilty for determining `has_children_in_menu`
                    to that.
                    """

                    # Create dict of kwargs to send to `has_submenu_items`
                    method_kwargs = {
                        'current_page': current_page,
                        'allow_repeating_parents': allow_repeating_parents,
                        'original_menu_tag': original_menu_tag,
                        'menu_instance': menu_instance,
                        'request': request,
                    }
                    # Call `has_submenu_items` using the above kwargs dict
                    has_children_in_menu = page.has_submenu_items(
                        **method_kwargs)

                else:
                    has_children_in_menu = menu_instance.page_has_children(
                        page)

            setattr(item, 'has_children_in_menu', has_children_in_menu)

            if apply_active_classes:
                active_class = ''
                if(current_page and page.pk == current_page.pk):
                    # This is the current page, so the menu item should
                    # probably have the 'active' class
                    active_class = app_settings.ACTIVE_CLASS
                    if (
                        allow_repeating_parents and use_specific and
                        has_children_in_menu
                    ):
                        if type(page) is Page:
                            page = page.specific
                        if getattr(page, 'repeat_in_subnav', False):
                            active_class = app_settings.ACTIVE_ANCESTOR_CLASS
                elif page.pk in current_page_ancestor_ids:
                    active_class = app_settings.ACTIVE_ANCESTOR_CLASS
                setattr(item, 'active_class', active_class)

        elif page is None:
            """
            This is a `MenuItem` for a custom URL. It can be classed as
            'active' if the URL matches the request path.
            """
            request_path = getattr(request, 'path', '')
            if apply_active_classes and item.link_url == request_path:
                setattr(item, 'active_class', app_settings.ACTIVE_CLASS)

        # In case the specific page was fetched during the above operations
        # We'll set `MenuItem.link_page` to that specific page.
        if menuitem and page:
            menuitem.link_page = page

        if use_absolute_page_urls:
            # Pages only have `get_full_url` from Wagtail 1.11 onwards
            if hasattr(item, 'get_full_url'):
                url = item.get_full_url(request=request)
            # Fallback for Wagtail versions prior to 1.11
            else:
                url = item.full_url
        else:
            # Both `Page` and `MenuItem` objects have a `relative_url` method
            # that we can use to calculate a value for the `href` attribute.
            url = item.relative_url(current_site)
        setattr(item, 'href', url)
        primed_menu_items.append(item)

    return primed_menu_items
