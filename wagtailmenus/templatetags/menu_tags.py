from copy import deepcopy
from django.template import Library
from django.db.models import Q
from ..models import MainMenu, FlatMenu
from wagtailmenus import app_settings


register = Library()

"""
In all menu templates, menu items are always assigned the following attributes
for you to output in the template:

    * `href`: the value to use for the `href` attribute on the <a> element
    * `text`: the text to use for the link
    * `active_class`: a class to be applied to the <li> element (values are
      `ancestor` if the page is an ancestor of the current page or `active` if
      the page is the current_page)
    * `has_children_in_menu`: a boolean value that will let you know if the
      item has children that should be output as a submenu.
"""


@register.simple_tag(takes_context=True)
def main_menu(
    context, show_multiple_levels=True, allow_repeating_parents=True,
    apply_active_classes=True, template=DEFAULT_MAIN_MENU_TEMPLATE
):
    """Render the MainMenu instance for the current site."""
    request = context['request']
    site = request.site
    try:
        menu = site.main_menu
    except MainMenu.DoesNotExist:
        menu = MainMenu.objects.create(site=site)
    ancestor_ids = request.META.get('CURRENT_PAGE_ANCESTOR_IDS', [])

    context.update({
        'apply_active_classes': apply_active_classes,
        'menu_items': tuple(prime_menu_items(
            menu_items=menu.menu_items.for_display(),
            current_page=context.get('self'),
            current_page_ancestor_ids=ancestor_ids,
            current_site=site,
            check_for_children=show_multiple_levels,
            allow_repeating_parents=allow_repeating_parents,
            apply_active_classes=apply_active_classes,
        ))
    })
    t = context.template.engine.get_template(template)
    return t.render(context)


@register.simple_tag(takes_context=True)
def section_menu(
    context, show_section_root=True, show_multiple_levels=True,
    allow_repeating_parents=True, apply_active_classes=True,
    template=DEFAULT_SECTION_MENU_TEMPLATE
):
    """Render a section menu for the current section."""
    request = context['request']
    current_site = request.site
    current_page = context.get('self')
    section_root = request.META.get('CURRENT_SECTION_ROOT')
    ancestor_ids = request.META.get('CURRENT_PAGE_ANCESTOR_IDS', [])

    if section_root:
        menu_items = prime_menu_items(
            menu_items=section_root.get_children().live().in_menu(),
            current_page=current_page,
            current_page_ancestor_ids=ancestor_ids,
            current_site=current_site,
            check_for_children=show_multiple_levels,
            allow_repeating_parents=allow_repeating_parents,
            apply_active_classes=apply_active_classes,
        )

        """
        We want `section_root` to have the same attributes as primed menu
        items, so it can be used in the same way in a template if required.
        """
        setattr(section_root, 'text', section_root.title)
        setattr(section_root, 'href', section_root.relative_url(current_site))

        """
        Before we can work out an `active_class` for `section_root`, we need
        to find out if it's going to be repeated alongside it's children in a
        subnav.
        """
        extra = None
        if (
            allow_repeating_parents and menu_items and
            getattr(section_root, 'repeat_in_subnav', False)
        ):
            """
            The page should be repeated alongside children in the
            subnav, so we create a new item and add it to the existing
            menu_items
            """
            extra = deepcopy(section_root)
            text = section_root.repeated_item_text or section_root.title
            setattr(extra, 'text', text)
            if apply_active_classes and extra.pk == current_page.pk:
                setattr(extra, 'active_class', ACTIVE_CLASS)
            menu_items.insert(0, extra)
        
        """
        Now we know the subnav/repetition situation, we can set the
        `active_class` for `section_root`
        """
        if apply_active_classes:
            active_class = ACTIVE_ANCESTOR_CLASS
            if(
                (extra is None or not hasattr(extra, 'active_class')) and
                section_root.pk == current_page.pk
            ):
                active_class = ACTIVE_CLASS
            setattr(section_root, 'active_class', active_class)
    else:
        menu_items = []

    context.update({
        'section_root': section_root,
        'apply_active_classes': apply_active_classes,
        'show_section_root': show_section_root,
        'menu_items': tuple(menu_items),
    })
    t = context.template.engine.get_template(template)
    return t.render(context)


@register.simple_tag(takes_context=True)
def flat_menu(
    context, handle, show_menu_heading=True, apply_active_classes=False,
    template=DEFAULT_FLAT_MENU_TEMPLATE
):
    """
    Find a FlatMenu for the current site matching the `handle` provided and
    render it.
    """
    request = context['request']
    current_site = request.site
    ancestor_ids = request.META.get('CURRENT_PAGE_ANCESTOR_IDS', [])

    context.update({
        'menu_handle': handle,
        'show_menu_heading': show_menu_heading,
        'apply_active_classes': apply_active_classes,
    })

    try:
        menu = current_site.flat_menus.get(handle__exact=handle)
        context.update({
            'matched_menu': menu,
            'menu_heading': menu.heading,
            'menu_items': tuple(prime_menu_items(
                menu_items=menu.menu_items.for_display(),
                current_page=context.get('self'),
                current_page_ancestor_ids=ancestor_ids,
                current_site=current_site,
                check_for_children=False,
                apply_active_classes=apply_active_classes,
            )),
        })
    except FlatMenu.DoesNotExist:
        context.update({
            'matched_menu': None,
            'menu_heading': '',
            'menu_items': [],
        })
    t = context.template.engine.get_template(template)
    return t.render(context)


@register.simple_tag(takes_context=True)
def children_menu(
    context, menuitem_or_page, stop_at_this_level=False,
    allow_repeating_parents=None, apply_active_classes=None,
    template=DEFAULT_CHILDREN_MENU_TEMPLATE
):
    """
    Retrieve the children menu items for the `menuitem_or_page` provided, and
    render them as a simple ul list
    """
    request = context['request']
    current_site = request.site
    ancestor_ids = request.META.get('CURRENT_PAGE_ANCESTOR_IDS', [])
    current_page = context.get('self')
    try:
        parent_page = menuitem_or_page.link_page.specific
    except AttributeError:
        parent_page = menuitem_or_page

    if apply_active_classes is None:
        apply_active_classes = context.get('apply_active_classes', True)

    menu_items = prime_menu_items(
        menu_items=parent_page.get_children().live().in_menu(),
        current_page=current_page,
        current_page_ancestor_ids=ancestor_ids,
        current_site=current_site,
        check_for_children=not stop_at_this_level,
        allow_repeating_parents=allow_repeating_parents,
        apply_active_classes=apply_active_classes
    )

    if allow_repeating_parents is None:
        allow_repeating_parents = context.get('allow_repeating_parents', True)

    try:
        if allow_repeating_parents and parent_page.repeat_in_subnav:
            extra_item = deepcopy(parent_page)
            href = parent_page.relative_url(current_site)
            text = parent_page.repeated_item_text or parent_page.title
            setattr(extra_item, 'href', href)
            setattr(extra_item, 'text', text)
            if apply_active_classes and parent_page.pk == current_page.pk:
                setattr(extra_item, 'active_class', ACTIVE_CLASS)
            menu_items.insert(0, extra_item)
    except AttributeError:
            pass

    context.update({
        'parent_page': parent_page,
        'menu_items': tuple(menu_items),
        'allow_repeating_parents': allow_repeating_parents,
        'current_template': template,
    })
    t = context.template.engine.get_template(template)
    return t.render(context)


def prime_menu_items(
    menu_items, current_page, current_page_ancestor_ids, current_site,
    check_for_children=False, allow_repeating_parents=True,
    apply_active_classes=True
):
    """
    Prepare a list of menuitem objects or pages for rendering to a menu
    template.
    """
    primed_menu_items = []
    for item in menu_items:

        """
        `MenuItem` and `Page` both have the relative_url method, which we use
        to get a URL relative to the current site root.
        """
        setattr(item, 'href', item.relative_url(current_site))

        try:
            """
            `menu_items` is a list of `MenuItem` objects, that either links
            to a Page, or a custom URL
            """
            page = item.link_page
            menuitem = item
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
            """
            If linking to a page, we only want to include this item
            in the resulting list if that page is set to appear in menus.
            """
            if check_for_children and page.depth > 2:
                """
                Working out whether this item should have a sub nav is
                expensive, so we try to do the working out where absolutely
                necessary.
                """
                if ((menuitem and menuitem.allow_subnav) or menuitem is None):
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
            page_is_repeated_in_subnav = False
            if allow_repeating_parents and has_children_in_menu:
                page = page.specific
                page_is_repeated_in_subnav = getattr(page, 'repeat_in_subnav',
                                                     False)

            """
            Now we can figure out which class should be added to this item
            """
            if apply_active_classes:
                if current_page and page.pk == current_page.pk:
                    if page_is_repeated_in_subnav:
                        setattr(item, 'active_class', ACTIVE_ANCESTOR_CLASS)
                    else:
                        setattr(item, 'active_class', ACTIVE_CLASS)
                elif page.depth > 2 and page.pk in current_page_ancestor_ids:
                    setattr(item, 'active_class', ACTIVE_ANCESTOR_CLASS)

            primed_menu_items.append(item)

        elif page is None:
            primed_menu_items.append(item)
    return primed_menu_items
