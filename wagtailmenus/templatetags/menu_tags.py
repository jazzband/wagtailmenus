from __future__ import unicode_literals

from copy import copy
from django.template import Library
from wagtail.wagtailcore.models import Page

from wagtailmenus import app_settings
from wagtailmenus.models import MenuFromRootPage
from wagtailmenus.utils.misc import (
    get_attrs_from_context, validate_supplied_values
)
from wagtailmenus.utils.template import (
    get_template_names, get_sub_menu_template_names
)
flat_menus_fbtdsm = app_settings.FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS

register = Library()


@register.simple_tag(takes_context=True)
def main_menu(
    context, max_levels=None, use_specific=None, apply_active_classes=True,
    allow_repeating_parents=True, show_multiple_levels=True,
    template='', sub_menu_template=''
):
    validate_supplied_values('main_menu', max_levels=max_levels,
                             use_specific=use_specific)

    # Variabalise relevant attributes from context
    request, site, current_page, root, ancestor_ids = get_attrs_from_context(
        context, guess_tree_position=True)

    # Find a matching menu
    menu = app_settings.MAIN_MENU_MODEL_CLASS.get_for_site(site)

    if not show_multiple_levels:
        max_levels = 1

    if max_levels is not None:
        menu.set_max_levels(max_levels)

    if use_specific is not None:
        menu.set_use_specific(use_specific)

    # Identify templates for rendering
    template_names = get_template_names('main', request, template)
    t = context.template.engine.select_template(template_names)
    sub_template_names = get_sub_menu_template_names('main', request,
                                                     sub_menu_template)
    submenu_t = context.template.engine.select_template(sub_template_names)

    c = copy(context)
    c.update({
        'menu_items': prime_menu_items(
            menu_items=menu.top_level_items,
            current_site=site,
            current_page=current_page,
            current_page_ancestor_ids=ancestor_ids,
            request_path=getattr(request, 'path', ''),
            use_specific=menu.use_specific,
            original_menu_tag='main_menu',
            menu_instance=menu,
            check_for_children=menu.max_levels > 1,
            allow_repeating_parents=allow_repeating_parents,
            apply_active_classes=apply_active_classes
        ),
        'main_menu': menu,
        'use_specific': menu.use_specific,
        'max_levels': menu.max_levels,
        'apply_active_classes': apply_active_classes,
        'allow_repeating_parents': allow_repeating_parents,
        'current_level': 1,
        'current_template': t.name,
        'sub_menu_template': submenu_t.name,
        'original_menu_tag': 'main_menu',
        'section_root': root,
        'current_ancestor_ids': ancestor_ids
    })
    return t.render(c)


@register.simple_tag(takes_context=True)
def flat_menu(
    context, handle, max_levels=None, use_specific=None,
    show_menu_heading=False, apply_active_classes=False,
    allow_repeating_parents=True, show_multiple_levels=True,
    template='', sub_menu_template='',
    fall_back_to_default_site_menus=flat_menus_fbtdsm,
):
    validate_supplied_values('flat_menu', max_levels=max_levels,
                             use_specific=use_specific)

    # Variabalise relevant attributes from context
    request, site, current_page, root, ancestor_ids = get_attrs_from_context(
        context, guess_tree_position=False)

    # Find a matching menu
    menu = app_settings.FLAT_MENU_MODEL_CLASS.get_for_site(
        handle, site, fall_back_to_default_site_menus
    )
    if not menu:
        # No menu was found matching `handle`, so gracefully render nothing.
        return ''

    if not show_multiple_levels:
        max_levels = 1

    if max_levels is not None:
        menu.set_max_levels(max_levels)

    if use_specific is not None:
        menu.set_use_specific(use_specific)

    template_names = menu.get_template_names(request, template)
    t = context.template.engine.select_template(template_names)

    sub_template_names = menu.get_sub_menu_template_names(request,
                                                          sub_menu_template)
    submenu_t = context.template.engine.select_template(sub_template_names)

    c = copy(context)
    c.update({
        'menu_items': prime_menu_items(
            menu_items=menu.top_level_items,
            current_site=site,
            current_page=current_page,
            current_page_ancestor_ids=ancestor_ids,
            request_path=getattr(request, 'path', ''),
            use_specific=menu.use_specific,
            original_menu_tag='flat_menu',
            menu_instance=menu,
            check_for_children=menu.max_levels > 1,
            allow_repeating_parents=allow_repeating_parents,
            apply_active_classes=apply_active_classes
        ),
        'matched_menu': menu,
        'menu_handle': handle,
        'menu_heading': menu.heading,
        'use_specific': menu.use_specific,
        'max_levels': menu.max_levels,
        'show_menu_heading': show_menu_heading,
        'apply_active_classes': apply_active_classes,
        'allow_repeating_parents': allow_repeating_parents,
        'current_level': 1,
        'current_template': t.name,
        'sub_menu_template': submenu_t.name,
        'original_menu_tag': 'flat_menu',
        'current_ancestor_ids': ancestor_ids
    })
    return t.render(c)


def get_sub_menu_items_for_page(
    page, request, current_site, current_page, ancestor_ids, menu_instance,
    use_specific, apply_active_classes, allow_repeating_parents,
    current_level=1, max_levels=2, original_menu_tag=''
):
    # The menu items will be the children of the provided `page`
    children_pages = menu_instance.get_children_for_page(page)

    # Call `prime_menu_items` to prepare the children pages for output. This
    # will add `href`, `text`, `active_class` and `has_children_in_menu`
    # attributes to each item, to use in menu templates.
    menu_items = prime_menu_items(
        menu_items=children_pages,
        current_site=current_site,
        current_page=current_page,
        current_page_ancestor_ids=ancestor_ids,
        request_path=getattr(request, 'path', ''),
        use_specific=use_specific,
        original_menu_tag=original_menu_tag,
        menu_instance=menu_instance,
        check_for_children=current_level < max_levels,
        allow_repeating_parents=allow_repeating_parents,
        apply_active_classes=apply_active_classes
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
        menu_items = page.modify_submenu_items(
            menu_items=menu_items,
            current_page=current_page,
            current_ancestor_ids=ancestor_ids,
            current_site=current_site,
            allow_repeating_parents=allow_repeating_parents,
            apply_active_classes=apply_active_classes,
            original_menu_tag=original_menu_tag,
            menu_instance=menu_instance
        )
    return page, menu_items


@register.simple_tag(takes_context=True)
def sub_menu(
    context, menuitem_or_page, stop_at_this_level=None, use_specific=None,
    allow_repeating_parents=None, apply_active_classes=None, template=''
):
    """
    Retrieve the children pages for the `menuitem_or_page` provided, turn them
    into menu items, and render them to a template.
    """
    validate_supplied_values('sub_menu', use_specific=use_specific,
                             menuitem_or_page=menuitem_or_page)

    # Variabalise relevant attributes from context
    request, site, current_page, root, ancestor_ids = get_attrs_from_context(
        context, guess_tree_position=False)

    max_levels = context.get(
        'max_levels', app_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS)
    previous_level = context.get('current_level', 2)
    current_level = previous_level + 1

    if use_specific is None:
        use_specific = context.get(
            'use_specific', app_settings.USE_SPECIFIC_AUTO)

    if apply_active_classes is None:
        apply_active_classes = context.get('apply_active_classes', True)

    if allow_repeating_parents is None:
        allow_repeating_parents = context.get('allow_repeating_parents', True)

    if not template:
        template = context.get(
            'sub_menu_template', app_settings.DEFAULT_SUB_MENU_TEMPLATE)

    original_menu_tag = context.get('original_menu_tag', 'sub_menu')

    if original_menu_tag == 'main_menu':
        menu_instance = context.get('main_menu')
    elif original_menu_tag == 'flat_menu':
        menu_instance = context.get('matched_menu')
    else:
        menu_instance = context.get('menu_instance')

    # Identify the Page that we need to get children for
    if isinstance(menuitem_or_page, Page):
        parent_page = menuitem_or_page
    else:
        parent_page = menuitem_or_page.link_page

    parent_page, menu_items = get_sub_menu_items_for_page(
        page=parent_page,
        request=request,
        current_site=site,
        current_page=current_page,
        ancestor_ids=ancestor_ids,
        menu_instance=menu_instance,
        use_specific=use_specific,
        original_menu_tag=original_menu_tag,
        current_level=current_level,
        max_levels=max_levels,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents
    )

    # Prepare context and render
    context = copy(context)
    context.update({
        'parent_page': parent_page,
        'menu_items': menu_items,
        'apply_active_classes': apply_active_classes,
        'allow_repeating_parents': allow_repeating_parents,
        'current_level': current_level,
        'max_levels': max_levels,
        'current_template': template,
        'original_menu_tag': original_menu_tag
    })
    t = context.template.engine.get_template(template)
    return t.render(context)


@register.simple_tag(takes_context=True)
def section_menu(
    context, show_section_root=True, show_multiple_levels=True,
    apply_active_classes=True, allow_repeating_parents=True,
    max_levels=app_settings.DEFAULT_SECTION_MENU_MAX_LEVELS,
    template='', sub_menu_template='',
    use_specific=app_settings.DEFAULT_SECTION_MENU_USE_SPECIFIC,
):
    """Render a section menu for the current section."""

    validate_supplied_values('section_menu', max_levels=max_levels,
                             use_specific=use_specific)

    # Variabalise relevant attributes from context
    request, site, current_page, root, ancestor_ids = get_attrs_from_context(
        context, guess_tree_position=True)

    if root is None:
        return ''

    if not show_multiple_levels:
        max_levels = 1

    # Create a menu instance that can fetch all pages at once and return
    # for subpages for each branch as they are needed
    menu_instance = MenuFromRootPage(root, max_levels, use_specific)

    section_root, menu_items = get_sub_menu_items_for_page(
        page=root,
        request=request,
        current_site=site,
        current_page=current_page,
        ancestor_ids=ancestor_ids,
        menu_instance=menu_instance,
        use_specific=use_specific,
        original_menu_tag='section_menu',
        current_level=1,
        max_levels=max_levels,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents
    )

    """
    We want `section_root` to have the same attributes as primed menu
    items, so it can be used in the same way in a template if required.
    """
    setattr(section_root, 'text', section_root.title)
    setattr(section_root, 'href', section_root.relative_url(site))
    if apply_active_classes:
        active_class = app_settings.ACTIVE_ANCESTOR_CLASS
        if current_page and section_root.pk == current_page.pk:
            # `section_root` is the current page, so should probably have
            # the 'active' class.
            active_class = app_settings.ACTIVE_CLASS
            # But not if there's a 'repeated item' in menu_items that already
            # has the 'active' class.
            if allow_repeating_parents and use_specific and menu_items:
                # TODO: We might want to make this check more than just the
                # first item
                if(
                    getattr(menu_items[0], 'active_class', '') ==
                    app_settings.ACTIVE_CLASS
                ):
                    active_class = app_settings.ACTIVE_ANCESTOR_CLASS
        setattr(section_root, 'active_class', active_class)

    # Identify templates for rendering
    template_names = get_template_names('section', request, template)
    t = context.template.engine.select_template(template_names)
    sub_template_names = get_sub_menu_template_names('section', request,
                                                     sub_menu_template)
    submenu_t = context.template.engine.select_template(sub_template_names)

    # Prepare context and render
    c = copy(context)
    c.update({
        'section_root': section_root,
        'menu_instance': menu_instance,
        'menu_items': menu_items,
        'show_section_root': show_section_root,
        'apply_active_classes': apply_active_classes,
        'allow_repeating_parents': allow_repeating_parents,
        'current_level': 1,
        'max_levels': max_levels,
        'current_template': t.name,
        'sub_menu_template': submenu_t.name,
        'original_menu_tag': 'section_menu',
        'current_ancestor_ids': ancestor_ids,
        'use_specific': use_specific
    })
    return t.render(c)


@register.simple_tag(takes_context=True)
def children_menu(
    context, parent_page=None, allow_repeating_parents=True,
    apply_active_classes=False,
    max_levels=app_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS,
    template='', sub_menu_template='',
    use_specific=app_settings.DEFAULT_CHILDREN_MENU_USE_SPECIFIC,
):
    validate_supplied_values(
        'children_menu', max_levels=max_levels, use_specific=use_specific,
        parent_page=parent_page)

    request, site, current_page, root, ancestor_ids = get_attrs_from_context(
        context, guess_tree_position=False)

    # Use current page as parent_page if no value supplied
    if parent_page is None:
        parent_page = context.get('self')
    if not parent_page:
        return ''

    # Create a menu instance that can fetch all pages at once and return
    # for subpages for each branch as they are needed
    menu_instance = MenuFromRootPage(parent_page, max_levels, use_specific)

    parent_page, menu_items = get_sub_menu_items_for_page(
        page=parent_page,
        request=request,
        current_site=site,
        current_page=current_page,
        ancestor_ids=ancestor_ids,
        menu_instance=menu_instance,
        use_specific=use_specific,
        original_menu_tag='children_menu',
        current_level=1,
        max_levels=max_levels,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents
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
        'use_specific': use_specific
    })
    return t.render(c)


def prime_menu_items(
    menu_items, current_site, current_page, current_page_ancestor_ids,
    request_path, use_specific, original_menu_tag, menu_instance,
    check_for_children=False, allow_repeating_parents=True,
    apply_active_classes=True
):
    """
    Prepare a list of `MenuItem` or `Page` objects for rendering to a menu
    template.
    """
    primed_menu_items = []

    for item in menu_items:
        try:
            """
            `menu_items` is a list of `MenuItem` objects from
            `Menu.top_level_items`. Any `link_page` values will have been
            replaced with specific pages if necessary
            """
            page = item.link_page
            menuitem = item
            setattr(item, 'text', item.menu_text)
        except AttributeError:
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
            First we work out whether this item should be flagged as needing
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
                    has_children_in_menu = page.has_submenu_items(
                        current_page=current_page,
                        allow_repeating_parents=allow_repeating_parents,
                        original_menu_tag=original_menu_tag,
                        menu_instance=menu_instance
                    )
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
            if apply_active_classes and item.link_url == request_path:
                setattr(item, 'active_class', app_settings.ACTIVE_CLASS)

        # In case the specific page was fetched during the above operations
        # We'll set `MenuItem.link_page` to that specific page.
        if menuitem and page:
            menuitem.link_page = page

        # Both `Page` and `MenuItem` objects have a `relative_url` method
        # we can use to calculate a value for the `href` attribute.
        setattr(item, 'href', item.relative_url(current_site))
        primed_menu_items.append(item)

    return primed_menu_items
