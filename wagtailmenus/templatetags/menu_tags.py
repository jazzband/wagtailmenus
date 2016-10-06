from copy import copy
from django.http import Http404
from django.template import Library
from wagtail.wagtailcore.models import Page
from ..models import MainMenu, FlatMenu
from wagtailmenus import app_settings
flat_menus_fbtdsm = app_settings.FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS

register = Library()


def get_attrs_from_context(context):
    """
    Gets a bunch of useful things from the context/request and returns them as
    a tuple for use in most menu tags. If `identify_section_from_path` is True,
    and `request.META['CURRENT_SECTION_ROOT']` hasn't been set by
    `wagtailmenu_params_helper` (most likely, because it isn't a 'Page'
    being served), attempt to identify a nearby page / section root from the
    request path.
    """
    request = context['request']
    site = request.site
    current_page = context.get('self', None)
    section_root = None
    identified_page = None
    ancestor_ids = []

    # If section_root` or `current_ancestor_ids` have been added to the
    # context by a previous `main_menu`, `section_menu` or `flat_menu`
    # call, then use those values to avoid any more further work
    section_root = context.get('section_root', None)
    ancestor_ids = context.get('current_ancestor_ids', [])

    # Fall back to finding values set by `wagtailmenus_params_helper`.
    if not section_root:
        section_root = request.META.get('CURRENT_SECTION_ROOT')
    if not ancestor_ids:
        ancestor_ids = request.META.get('CURRENT_PAGE_ANCESTOR_IDS', [])

    if not current_page:
        path_components = [pc for pc in request.path.split('/') if pc]
        # Keep trying to find a page using the path components until there are
        # no components left, or a page has been identified
        first_run = True
        while path_components and not identified_page:
            try:
                # NOTE: The route() method is quite inefficient we should
                # think about matching some other way in future.
                identified_page, args, kwargs = site.root_page.specific.route(
                    request, path_components)
                ancestor_ids = identified_page.get_ancestors(
                    inclusive=True).values_list('id', flat=True)
                if first_run:
                    # A page was found matching the exact path, so it's safe to
                    # assume it's the 'current page'
                    current_page = identified_page
            except Http404:
                # No match found, so remove a path component and try again
                path_components.pop()
            first_run = False  # Don't use non-exact matches as 'current_page'

    if not section_root and (current_page or identified_page):
        page = current_page or identified_page
        if page.depth == app_settings.SECTION_ROOT_DEPTH:
            section_root = page
        if page.depth > app_settings.SECTION_ROOT_DEPTH:
            # Attempt to identify the section root page using either the
            # current page from the context, or the one identified above
            section_root = site.root_page.get_descendants().ancestor_of(
                page, inclusive=True
            ).filter(depth__exact=app_settings.SECTION_ROOT_DEPTH).first()
        if section_root and type(section_root) is Page:
            # We need the 'specific' section_root page, so that we can
            # look for / use the page's `modify_submenu_items()` method
            section_root = section_root.specific
    return (request, site, current_page, section_root, ancestor_ids)


def get_children_for_menu(page, original_menu_tag, use_specific):
    qs = page.get_children().live().in_menu()
    if use_specific:
        qs = qs.specific()
    else:
        qs = qs.select_related('content_type')
    return qs


@register.simple_tag(takes_context=True)
def main_menu(
    context, apply_active_classes=True, allow_repeating_parents=True,
    show_multiple_levels=True,
    max_levels=app_settings.DEFAULT_MAIN_MENU_MAX_LEVELS,
    template=app_settings.DEFAULT_MAIN_MENU_TEMPLATE,
    sub_menu_template=app_settings.DEFAULT_SUB_MENU_TEMPLATE,
    use_specific=app_settings.DEFAULT_MAIN_MENU_USE_SPECIFIC,
):
    """Render the MainMenu instance for the current site."""
    r, site, current_page, section_root, ancestor_ids = get_attrs_from_context(
        context)

    menu = MainMenu.get_for_site(site)

    if not show_multiple_levels:
        max_levels = 1

    context.update({
        'apply_active_classes': apply_active_classes,
        'menu_items': prime_menu_items(
            menu_items=menu.menu_items.for_display(),
            current_site=site,
            current_page=current_page,
            current_page_ancestor_ids=ancestor_ids,
            request_path=r.path,
            check_for_children=max_levels > 1,
            allow_repeating_parents=allow_repeating_parents,
            apply_active_classes=apply_active_classes,
            use_specific=use_specific,
            original_menu_tag='main_menu'
        ),
        'allow_repeating_parents': allow_repeating_parents,
        'current_level': 1,
        'max_levels': max_levels,
        'current_template': template,
        'sub_menu_template': sub_menu_template,
        'original_menu_tag': 'main_menu',
        'section_root': section_root,
        'current_ancestor_ids': ancestor_ids,
        'use_specific': use_specific,
    })
    t = context.template.engine.get_template(template)
    return t.render(context)


@register.simple_tag(takes_context=True)
def section_menu(
    context, show_section_root=True, show_multiple_levels=True,
    apply_active_classes=True, allow_repeating_parents=True,
    max_levels=app_settings.DEFAULT_SECTION_MENU_MAX_LEVELS,
    template=app_settings.DEFAULT_SECTION_MENU_TEMPLATE,
    sub_menu_template=app_settings.DEFAULT_SUB_MENU_TEMPLATE,
    use_specific=app_settings.DEFAULT_SECTION_MENU_USE_SPECIFIC,
):
    """Render a section menu for the current section."""
    r, site, current_page, section_root, ancestor_ids = get_attrs_from_context(
        context)

    if not show_multiple_levels:
        max_levels = 1

    if section_root is None:
        # The section root couldn't be identified.
        return ''

    """
    We want `section_root` to have the same attributes as primed menu
    items, so it can be used in the same way in a template if required.
    """
    setattr(section_root, 'text', section_root.title)
    setattr(section_root, 'href', section_root.relative_url(site))

    children_qs = get_children_for_menu(section_root, 'section_menu',
                                        use_specific)
    menu_items = prime_menu_items(
        menu_items=children_qs,
        current_site=site,
        current_page=current_page,
        current_page_ancestor_ids=ancestor_ids,
        request_path=r.path,
        check_for_children=max_levels > 1,
        allow_repeating_parents=allow_repeating_parents,
        original_menu_tag='section_menu'
    )

    """
    If section_root has a `modify_submenu_items` method, call it to modify
    the list of menu_items appropriately.
    """
    if hasattr(section_root, 'modify_submenu_items'):
        menu_items = section_root.modify_submenu_items(
            menu_items, current_page, ancestor_ids, site,
            allow_repeating_parents, apply_active_classes, 'section_menu')

    """
    Now we know the subnav/repetition situation, we can set the `active_class`
    for the section_root page (much like `prime_menu_items` does for pages
    with children.
    """
    if apply_active_classes:
        active_class = ''
        if current_page and section_root.pk == current_page.pk:
            repeat_in_subnav = getattr(section_root, 'repeat_in_subnav', False)
            if (allow_repeating_parents and menu_items and repeat_in_subnav):
                active_class = app_settings.ACTIVE_ANCESTOR_CLASS
            else:
                active_class = app_settings.ACTIVE_CLASS
        elif section_root.pk in ancestor_ids:
            active_class = app_settings.ACTIVE_ANCESTOR_CLASS
        setattr(section_root, 'active_class', active_class)

    context.update({
        'section_root': section_root,
        'show_section_root': show_section_root,
        'apply_active_classes': apply_active_classes,
        'allow_repeating_parents': allow_repeating_parents,
        'menu_items': menu_items,
        'current_level': 1,
        'max_levels': max_levels,
        'current_template': template,
        'sub_menu_template': sub_menu_template,
        'original_menu_tag': 'section_menu',
        'current_ancestor_ids': ancestor_ids,
        'use_specific': use_specific,
    })
    t = context.template.engine.get_template(template)
    return t.render(context)


@register.simple_tag(takes_context=True)
def flat_menu(
    context, handle, show_menu_heading=True, apply_active_classes=False,
    show_multiple_levels=False, allow_repeating_parents=True,
    max_levels=app_settings.DEFAULT_FLAT_MENU_MAX_LEVELS,
    template=app_settings.DEFAULT_FLAT_MENU_TEMPLATE,
    sub_menu_template=app_settings.DEFAULT_SUB_MENU_TEMPLATE,
    use_specific=app_settings.DEFAULT_FLAT_MENU_USE_SPECIFIC,
    fall_back_to_default_site_menus=flat_menus_fbtdsm,
):
    """
    Find a FlatMenu for the current site matching the `handle` provided and
    render it.
    """
    r, site, current_page, section_root, ancestor_ids = get_attrs_from_context(
        context)

    if not show_multiple_levels:
        max_levels = 1

    menu = FlatMenu.get_for_site(
        handle, site, fall_back_to_default_site_menus)
    if not menu:
        # No menu was found matching `handle`, so gracefully render nothing.
        return ''

    menu_items = prime_menu_items(
        menu_items=menu.menu_items.for_display(),
        current_site=site,
        current_page=current_page,
        current_page_ancestor_ids=ancestor_ids,
        request_path=r.path,
        check_for_children=max_levels > 1,
        allow_repeating_parents=allow_repeating_parents,
        apply_active_classes=apply_active_classes,
        use_specific=use_specific,
        original_menu_tag='flat_menu',
    )

    context.update({
        'matched_menu': menu,
        'menu_handle': handle,
        'menu_heading': menu.heading,
        'show_menu_heading': show_menu_heading,
        'apply_active_classes': apply_active_classes,
        'allow_repeating_parents': allow_repeating_parents,
        'menu_items': menu_items,
        'current_level': 1,
        'max_levels': max_levels,
        'current_template': template,
        'sub_menu_template': sub_menu_template,
        'original_menu_tag': 'flat_menu',
        'section_root': section_root,
        'current_ancestor_ids': ancestor_ids,
        'use_specific': use_specific,
    })
    t = context.template.engine.get_template(template)
    return t.render(context)


@register.simple_tag(takes_context=True)
def sub_menu(
    context, menuitem_or_page, stop_at_this_level=None,
    allow_repeating_parents=None, apply_active_classes=None,
    template=None, use_specific=None
):
    """
    Retrieve the children pages for the `menuitem_or_page` provided, turn them
    into menu items, and render them to a template.

    Instead of updating the context directly, we create a copy of it, to avoid
    various sub-menus in the same menu getting confused about the current level
    they're rendering, and whether they should render any further levels
    """
    context = copy(context)
    r, site, current_page, section_root, ancestor_ids = get_attrs_from_context(
        context)
    previous_level = context.get('current_level', 0)
    current_level = previous_level + 1

    try:
        # First, presume we're dealing with a `MenuItem`
        parent_page = menuitem_or_page.link_page.specific
    except AttributeError:
        try:
            # Now assume we're dealing with a `Page` object
            parent_page = menuitem_or_page.specific
        except AttributeError:
            # We can't determine the page, so fail gracefully
            return ''

    max_levels = context.get(
        'max_levels', app_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS)

    if stop_at_this_level is None:
        stop_at_this_level = (current_level >= max_levels)

    if apply_active_classes is None:
        apply_active_classes = context.get('apply_active_classes', True)

    if allow_repeating_parents is None:
        allow_repeating_parents = context.get('allow_repeating_parents', True)

    if use_specific is None:
        use_specific = context.get('use_specific', False)

    if template is None:
        template = context.get(
            'sub_menu_template', app_settings.DEFAULT_SUB_MENU_TEMPLATE)

    original_menu_tag = context.get('original_menu_tag', 'sub_menu')

    children_qs = get_children_for_menu(parent_page, original_menu_tag,
                                        use_specific)
    menu_items = prime_menu_items(
        menu_items=children_qs,
        current_site=site,
        current_page=current_page,
        current_page_ancestor_ids=ancestor_ids,
        request_path=r.path,
        check_for_children=not stop_at_this_level,
        allow_repeating_parents=allow_repeating_parents,
        apply_active_classes=apply_active_classes,
        original_menu_tag=original_menu_tag,
    )

    """
    If parent_page has a `modify_submenu_items` method, call it to modify
    the list of menu_items appropriately.
    """
    if hasattr(parent_page, 'modify_submenu_items'):
        menu_items = parent_page.modify_submenu_items(
            menu_items, current_page, ancestor_ids, site,
            allow_repeating_parents, apply_active_classes, original_menu_tag)

    context.update({
        'parent_page': parent_page,
        'menu_items': menu_items,
        'allow_repeating_parents': allow_repeating_parents,
        'current_level': current_level,
        'max_levels': max_levels,
        'current_template': template,
        'original_menu_tag': original_menu_tag,
    })
    t = context.template.engine.get_template(template)
    return t.render(context)


@register.simple_tag(takes_context=True)
def children_menu(
    context, parent_page=None, allow_repeating_parents=True,
    apply_active_classes=False,
    max_levels=app_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS,
    template=app_settings.DEFAULT_CHILDREN_MENU_TEMPLATE,
    sub_menu_template=app_settings.DEFAULT_SUB_MENU_TEMPLATE,
    use_specific=app_settings.DEFAULT_CHILDREN_MENU_USE_SPECIFIC,
):
    if parent_page is None:
        parent_page = context.get('self')
        if not isinstance(parent_page, Page):
            return ''

    context.update({
        'current_level': 0,
        'max_levels': max_levels,
        'original_menu_tag': 'children_menu',
        'use_specific': use_specific,
        'sub_menu_template': sub_menu_template,
    })
    return sub_menu(
        context,
        menuitem_or_page=parent_page,
        allow_repeating_parents=allow_repeating_parents,
        apply_active_classes=apply_active_classes,
        template=template,
        use_specific=use_specific,
    )


def prime_menu_items(
    menu_items, current_site, current_page, current_page_ancestor_ids,
    request_path, check_for_children=False, allow_repeating_parents=True,
    apply_active_classes=True, use_specific=False, original_menu_tag='',
):
    """
    Prepare a list of menuitem objects or pages for rendering to a menu
    template.
    """
    section_root_depth = app_settings.SECTION_ROOT_DEPTH
    primed_menu_items = []

    for item in menu_items:
        try:
            """
            `menu_items` is a list of `MenuItem` objects, that either links
            to Page instances, or custom URLs
            """
            page = item.link_page
            menuitem = item
            if page and use_specific:
                page = page.specific
            setattr(item, 'text', item.menu_text)
        except AttributeError:
            """
            `menu_items` is a list of `Page` objects, not `MenuItem` objects
            """
            page = item
            menuitem = None
            setattr(item, 'text', page.title)

        has_children_in_menu = False
        if page:
            if (page.depth >= section_root_depth):
                """
                Working out whether this item should have a sub nav is
                expensive, so we try to do the working out only when absolutely
                necessary.
                """
                if (
                    check_for_children and
                    (menuitem is None or menuitem.allow_subnav)
                ):
                    if (
                        hasattr(page, 'has_submenu_items') or
                        hasattr(page.specific_class, 'has_submenu_items')
                    ):
                        """
                        If the page has a `has_submenu_items` method, shift
                        responsibilty for determining `has_children_in_menu`
                        to that. Note that the method will not be accessed
                        if `check_for_children` is False, so the `max_levels`
                        value supplied to the original menu tag will always be
                        respected.
                        """
                        if type(page) is Page:
                            page = page.specific
                        has_children_in_menu = page.has_submenu_items(
                            current_page=current_page,
                            check_for_children=True,
                            allow_repeating_parents=allow_repeating_parents,
                            original_menu_tag=original_menu_tag,
                        )

                    else:
                        """
                        The page has no `has_submenu_items` method. Resort to
                        default behaviour (check if there are any children
                        pages that need representing in a sub menu).
                        """
                        has_children_in_menu = (
                            page.get_children().live().in_menu().exists())

            setattr(item, 'has_children_in_menu', has_children_in_menu)

            """
            Now we know whether this page has a subnav or not, we can look
            for a `repeat_in_subnav` value on the page's specific model
            object, to see if a link to the same page will be repeated as
            the first child. If so, we only want this item to have an
            `ancestor` class at most, as the repeated nav item will be
            given the `active` class.
            """
            repeated_in_subnav = False
            if allow_repeating_parents and has_children_in_menu:
                """
                Only call the page's `specific` property method if we don't
                already have the sub-type.
                """
                if type(page) is Page:
                    page = page.specific
                repeated_in_subnav = getattr(page, 'repeat_in_subnav', False)

            # Now we can figure out which class should be added to this item
            if apply_active_classes:
                active_class = ''
                if current_page and page.pk == current_page.pk:
                    if repeated_in_subnav:
                        active_class = app_settings.ACTIVE_ANCESTOR_CLASS
                    else:
                        active_class = app_settings.ACTIVE_CLASS
                elif(
                    page.depth >= app_settings.SECTION_ROOT_DEPTH and
                    page.pk in current_page_ancestor_ids
                ):
                    active_class = app_settings.ACTIVE_ANCESTOR_CLASS
                setattr(item, 'active_class', active_class)

            """
            If we're dealing with a MenuItem instance, replace `link_page` with
            the page object we have, which may well be a 'specific' page by now
            """
            if menuitem:
                item.link_page = page

            """
            Using `relative_url()` on the `page` object to get a `href` value.
            If `use_specific=True` was used, this will be a 'specific' page
            by now, which is better, as `relative_url()` can be overridden.
            """
            href = page.relative_url(current_site)
            if menuitem:
                href += menuitem.url_append
            setattr(item, 'href', href)
            primed_menu_items.append(item)

        elif page is None:
            setattr(item, 'href', item.link_url + item.url_append)
            if apply_active_classes and item.link_url == request_path:
                setattr(item, 'active_class', app_settings.ACTIVE_CLASS)
            primed_menu_items.append(item)

    return primed_menu_items
