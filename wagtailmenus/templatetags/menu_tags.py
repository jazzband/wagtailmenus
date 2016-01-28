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


def prime_menu_items(menu_items, current_page, current_site,
                     check_for_children=False):
    """
    Takes a list of MenuItem objects and does a little evaluation on each item,
    adding additional attributes to each item to store extra data to use in
    menu templates
    """
    primed_menu_items = []
    for item in menu_items:
        setattr(item, 'has_children_in_menu', False)
        if item.link_page and item.link_page.show_in_menus:
            setattr(item, 'url', item.link_page.relative_url(current_site))
            if current_page:
                active_class = ''
                if item.link_page.id == current_page.id:
                    active_class = 'active'
                else:
                    ancestor_ids = current_page.get_ancestors().values_list(
                        'id', flat=True)
                    if all([
                        item.link_page,
                        item.link_page.depth > 2,
                        item.link_page.pk in ancestor_ids
                    ]):
                        active_class = 'ancestor'
                setattr(item, 'active_class', active_class)
            if check_for_children and item.show_children_menu:
                has_children = has_children_in_menu(item.link_page)
                setattr(item, 'has_children_in_menu', has_children)
            primed_menu_items.append(item)
        elif not item.link_page:
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
        setattr(page, 'url', page.relative_url(current_site))
        if current_page:  # if current page exists in the database
            active_class = ''
            if page.id == current_page.id:
                active_class = 'active'
            else:
                ancestor_ids = current_page.get_ancestors().values_list(
                    'id', flat=True)
                if page.pk in ancestor_ids:
                    active_class = 'ancestor'
            setattr(page, 'active_class', active_class)
        if check_for_children:
            has_children = has_children_in_menu(page)
        else:
            has_children = False
        setattr(page, 'has_children_in_menu', has_children)
    return page_list


def get_children_menu_items(parent, current_page, current_site,
                            stop_at_this_level=False):
    check_for_children = not stop_at_this_level
    menu_items = prime_page_list(
        page_list=parent.get_children().live().in_menu(),
        current_page=current_page,
        current_site=current_site,
        check_for_children=check_for_children,
    )
    return {
        'parent': parent,
        'menu_items': menu_items,
    }


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
def children_menu(context, parent, stop_at_this_level=False):
    """
    Retrieves the children menu items and renders them as a simple ul list
    """
    current_site = get_site_from_context(context)
    current_page = context.get('self')
    context.update(
        get_children_menu_items(parent, current_page, current_site,
                                stop_at_this_level)
    )
    return context


@register.inclusion_tag('menus/children_menu_dropdown.html',
                        takes_context=True)
def children_menu_dropdown(context, parent, stop_at_this_level=True):
    """
    Retrieves the children menu items and renders them as a dropdown ul list
    with added accessibility attributes
    """
    current_site = get_site_from_context(context)
    current_page = context.get('self')
    context.update(
        get_children_menu_items(parent, current_page, current_site,
                                stop_at_this_level)
    )
    return context
