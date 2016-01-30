from django import template

register = template.Library()

from wagtail.wagtailcore.models import Page
from ..models import FlatMenu


def get_site_from_context(context):
    return context['request'].site


def get_site_root_from_context(context):
    return context['request'].site.root_page


def has_children_in_menu(page):
    return bool(page.get_children().live().in_menu().count())


def get_active_class(item, current_page, has_children=False,
                     potentially_repeat_in_children_menu=False):
    try:
        page = item.link_page
        is_menuitem = True
    except AttributeError:
        page = item
        is_menuitem = False
    if current_page:
        if page.id == current_page.id:
            if (
                is_menuitem and potentially_repeat_in_children_menu and
                item.has_children_in_menu and item.repeat_in_children_menu
            ):
                """
                Here, we have a menuitem that is set to repeat in it's own
                children menu. Best we let the repeated version get the
                'active' class, rather than the both.
                """
                return 'ancestor'
            else:
                return 'active'
        elif page.depth > 2:
            if page.pk in current_page.get_ancestors().values_list(
                'id', flat=True
            ):
                return 'ancestor'
    return ''


def prime_menu_items(menu_items, current_page, current_site,
                     check_for_children=False):
    """
    Takes a list of `MenuItem` objects and does a little evaluation on each
    item, adding additional attributes `href`, `has_children_in_menu` and
    `active_class` for use in templates
    """
    primed_menu_items = []
    for item in menu_items:
        setattr(item, 'has_children_in_menu', False)
        """
        If linking to a page, we only want to include this item
        in the resulting list if that page is set to appear in menus.
        """
        if item.link_page and item.link_page.show_in_menus:
            """
            Since we have access to current_site, let's bypass the need
            for the `pageurl` templatetag and get the relative_url of the page
            here to use for `href`.
            """
            relative_url = item.link_page.relative_url(current_site)
            setattr(item, 'href', relative_url)

            """
            Now we check if the menuitem should have a children menu. The
            function variable `check_for_children` and `show_children_menu` on
            the menuitem must both evaluate to True before we run further
            queries to check for children.
            """
            if check_for_children and item.show_children_menu:
                has_children = has_children_in_menu(item.link_page)
                setattr(item, 'has_children_in_menu', has_children)

            setattr(item, 'active_class', get_active_class(
                item, current_page, item.has_children_in_menu, True
            ))
            primed_menu_items.append(item)
        elif not item.link_page:
            """
            The menuitem has a custom URL instead of referencing a page. In
            which case, we just set `href` to that custom URL
            """
            setattr(item, 'href', item.link_url)
            primed_menu_items.append(item)
    return primed_menu_items


def prime_page_list(page_list, current_page, current_site,
                    check_for_children=True):
    """
    Takes a list of Page objects and does a little evaluation on each item,
    adding additional attributes to each item to store extra data to use in
    menu templates
    """
    for page in page_list:
        relative_url = page.relative_url(current_site)
        setattr(page, 'href', relative_url)

        if check_for_children:
            has_children = has_children_in_menu(page)
        else:
            has_children = False
        setattr(page, 'has_children_in_menu', has_children)
        setattr(page, 'active_class', get_active_class(
            page, current_page, has_children, True
        ))
    return page_list


@register.assignment_tag(takes_context=True)
def get_section_root(context, current_page):
    root_page = get_site_root_from_context(context)
    return root_page.get_children().ancestor_of(current_page, inclusive=True)


@register.inclusion_tag('menus/main_menu.html', takes_context=True)
def main_menu(context, show_multiple_levels=True):
    site = get_site_from_context(context)
    current_page = context.get('self')
    menu = site.main_menu
    menu_items = prime_menu_items(
        menu_items=menu.menu_items.all().select_related('link_page'),
        current_page=current_page,
        current_site=site,
        check_for_children=show_multiple_levels,
    )
    context.update({'menu_items': menu_items})
    return context


@register.inclusion_tag('menus/section_menu.html', takes_context=True)
def section_menu(context, show_section_root=True, show_multiple_levels=True):
    site = get_site_from_context(context)
    current_page = context.get('self')
    if current_page:
        try:
            section_root = get_section_root(context, current_page).get()
            if current_page and section_root == current_page:
                active_class = 'active'
            else:
                active_class = 'ancestor'
            setattr(section_root, 'active_class', active_class)

            menu_items = prime_page_list(
                page_list=section_root.get_children().live().in_menu(),
                current_page=current_page,
                current_site=site,
                check_for_children=show_multiple_levels)

            context.update({
                'show_section_root': show_section_root,
                'section_root': section_root,
                'menu_items': menu_items,
            })
            return context
        except Page.DoesNotExist:
            pass

    context.update({
        'show_section_root': show_section_root,
        'section_root': None,
        'menu_items': None,
    })
    return context


@register.inclusion_tag('menus/flat_menu.html', takes_context=True)
def flat_menu(context, handle, show_menu_heading=True):
    site = get_site_from_context(context)
    current_page = context.get('self')
    try:
        menu = site.flat_menus.get(handle__exact=handle)

        menu_items = prime_menu_items(
            menu_items=menu.menu_items.all().select_related('link_page'),
            current_page=current_page,
            current_site=site,
            check_for_children=False)

        context.update({
            'matched_menu': menu,
            'menu_heading': menu.heading,
            'menu_handle': handle,
            'menu_items': menu_items,
            'show_menu_heading': show_menu_heading,
        })

    except FlatMenu.DoesNotExist:
        context.update({
            'matched_menu': None,
            'menu_heading': '',
            'menu_handle': handle,
            'menu_items': [],
            'show_menu_heading': show_menu_heading,
        })
    return context


@register.inclusion_tag('menus/children_menu.html', takes_context=True)
def children_menu(context, menuitem_or_page, stop_at_this_level=False):
    """
    Retrieves the children menu items and renders them as a simple ul list
    """
    current_site = get_site_from_context(context)
    current_page = context.get('self')
    parent_menuitem = None
    try:
        """
        A `MenuItem` was provided for `menuitem_or_page`, so we check whether
        it needs to be repeated in the children nav. If it does, we add it to
        the context as `parent_menuitem`, so it can be used in the template.
        """
        parent_page = menuitem_or_page.link_page
        if menuitem_or_page.repeat_in_children_menu:
            parent_menuitem = menuitem_or_page
            setattr(parent_menuitem, 'active_class', get_active_class(
                parent_menuitem, current_page, False, False
            ))
    except AttributeError:
        """
        A `Page` was provided for `menuitem_or_page`. `parent_menuitem` will
        remain a None value.
        """
        parent_page = menuitem_or_page

    menu_items = prime_page_list(
        page_list=parent_page.get_children().live().in_menu(),
        current_page=current_page,
        current_site=current_site,
        check_for_children=not stop_at_this_level,
    )
    context.update({
        'parent_page': parent_page,
        'parent_menuitem': parent_menuitem,
        'menu_items': menu_items,
    })
    return context


@register.inclusion_tag('menus/children_menu_dropdown.html',
                        takes_context=True)
def children_menu_dropdown(context, menuitem_or_page, stop_at_this_level=True):
    """
    Retrieves the children menu items and renders them as a dropdown ul list
    with added accessibility attributes
    """
    return children_menu(context, menuitem_or_page, stop_at_this_level)
