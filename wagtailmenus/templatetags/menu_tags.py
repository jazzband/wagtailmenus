from copy import deepcopy
from django.template import Library
from django.db.models import Q
from wagtail.wagtailcore.models import Page
from ..models import MainMenu, FlatMenu
from wagtailmenus import app_settings


register = Library()

"""
In all menu templates, menu items are always assigned the following attributes
for you to use in the template:

    * `href`: The value to use for the `href` attribute on the <a> element
    * `text`: The text to use for the link
    * `active_class`: A class to be applied to the <li> element (values are
      `ancestor` If the page is an ancestor of the current page or `active` if
      the page is the current_page)
    * `has_children_in_menu`: A boolean value that will let you know if the
      item has children that should be output as a submenu.

The following variables will also be added to the context for you to make use
of:

    * `current_level`: The current 'level' being rendered. This starts at 1 for
      the initial template tag call, then increments each time `sub_menu`
      is called recursively.
    * `current_template`: The name of the template currently being rendered.
      This is most useful when rendering a `sub_menu` template that
      calls `sub_menu` recursively, and you wish to use the same template
      for all recursions.
"""


@register.simple_tag(takes_context=True)
def main_menu(
    context, apply_active_classes=True, allow_repeating_parents=True,
    show_multiple_levels=True,
    max_levels=app_settings.DEFAULT_MAIN_MENU_MAX_LEVELS,
    template=app_settings.DEFAULT_MAIN_MENU_TEMPLATE
):
    """Render the MainMenu instance for the current site."""
    request = context['request']
    site = request.site
    try:
        menu = site.main_menu
    except MainMenu.DoesNotExist:
        menu = MainMenu.objects.create(site=site)
    ancestor_ids = request.META.get('CURRENT_PAGE_ANCESTOR_IDS', [])

    if not show_multiple_levels:
        max_levels = 1

    context.update({
        'apply_active_classes': apply_active_classes,
        'menu_items': prime_menu_items(
            menu_items=menu.menu_items.for_display(),
            current_site=site,
            current_page=context.get('self'),
            current_page_ancestor_ids=ancestor_ids,
            check_for_children=max_levels > 1,
            allow_repeating_parents=allow_repeating_parents,
            apply_active_classes=apply_active_classes,
        ),
        'allow_repeating_parents': allow_repeating_parents,
        'current_level': 1,
        'max_levels': max_levels,
        'current_template': template,
    })
    t = context.template.engine.get_template(template)
    return t.render(context)


@register.simple_tag(takes_context=True)
def section_menu(
    context, show_section_root=True, show_multiple_levels=True,
    apply_active_classes=True, allow_repeating_parents=True,
    max_levels=app_settings.DEFAULT_SECTION_MENU_MAX_LEVELS,
    template=app_settings.DEFAULT_SECTION_MENU_TEMPLATE
):
    """Render a section menu for the current section."""
    request = context['request']
    current_site = request.site
    current_page = context.get('self')
    section_root = request.META.get('CURRENT_SECTION_ROOT')
    ancestor_ids = request.META.get('CURRENT_PAGE_ANCESTOR_IDS', [])

    if not show_multiple_levels:
        max_levels = 1

    if section_root is None:
        # The section root couldn't be identified. Likely because it's not 
        # a 'Page' being served, and `wagtail_hooks.wagtailmenu_params_helper`
        # isn't running.
        return ''

    """
    We want `section_root` to have the same attributes as primed menu
    items, so it can be used in the same way in a template if required.
    """
    setattr(section_root, 'text', section_root.title)
    setattr(section_root, 'href', section_root.relative_url(current_site))

    menu_items = prime_menu_items(
        menu_items=section_root.get_children().live().in_menu(),
        current_site=current_site,
        current_page=current_page,
        current_page_ancestor_ids=ancestor_ids,
        check_for_children=max_levels > 1,
        allow_repeating_parents=allow_repeating_parents,
        apply_active_classes=apply_active_classes,
    )

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
            setattr(extra, 'active_class', app_settings.ACTIVE_CLASS)
        menu_items.insert(0, extra)
    
    """
    Now we know the subnav/repetition situation, we can set the
    `active_class` for `section_root`
    """
    if apply_active_classes:
        active_class = app_settings.ACTIVE_ANCESTOR_CLASS
        if(
            (extra is None or not hasattr(extra, 'active_class')) and
            section_root.pk == current_page.pk
        ):
            active_class = app_settings.ACTIVE_CLASS
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
    })
    t = context.template.engine.get_template(template)
    return t.render(context)


@register.simple_tag(takes_context=True)
def flat_menu(
    context, handle, show_menu_heading=True, apply_active_classes=False,
    show_multiple_levels=False, allow_repeating_parents=True,
    max_levels=app_settings.DEFAULT_FLAT_MENU_MAX_LEVELS,
    template=app_settings.DEFAULT_FLAT_MENU_TEMPLATE
):
    """
    Find a FlatMenu for the current site matching the `handle` provided and
    render it.
    """
    request = context['request']
    current_site = request.site
    current_page = context.get('self')
    ancestor_ids = request.META.get('CURRENT_PAGE_ANCESTOR_IDS', [])
    
    if not show_multiple_levels:
        max_levels = 1

    try:
        menu = current_site.flat_menus.get(handle__exact=handle)
    except FlatMenu.DoesNotExist:
        # No menu was found matching `handle`, so gracefully render nothing.
        return ''

    menu_items = prime_menu_items(
        menu_items=menu.menu_items.for_display(),
        current_site=current_site,
        current_page=current_page,
        current_page_ancestor_ids=ancestor_ids,
        check_for_children=max_levels > 1,
        allow_repeating_parents=allow_repeating_parents,
        apply_active_classes=apply_active_classes,
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
    })
    t = context.template.engine.get_template(template)
    return t.render(context)


@register.simple_tag(takes_context=True)
def sub_menu(
    context, menuitem_or_page, stop_at_this_level=None,
    allow_repeating_parents=None, apply_active_classes=None,
    template=app_settings.DEFAULT_CHILDREN_MENU_TEMPLATE
):
    """
    Retrieve the children pages for the `menuitem_or_page` provided, turn them
    into menu items, and render them to a template
    """
    request = context['request']
    previous_level = context.get('current_level', 0)
    current_level = previous_level + 1
    current_site = request.site
    ancestor_ids = request.META.get('CURRENT_PAGE_ANCESTOR_IDS', [])
    current_page = context.get('self')

    try:
        # menuitem_or_page is a page
        parent_page = menuitem_or_page.specific
    except AttributeError:
        try:
            # menuitem_or_page is a menuitem linking to a page
            parent_page = menuitem_or_page.link_page.specific
        except AttributeError:
            # menuitem_or_page wasn't a menuitem or page
            return ''

    max_levels = context.get(
        'max_levels', app_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS)

    if stop_at_this_level is None:
        stop_at_this_level = (current_level >= max_levels)

    if apply_active_classes is None:
        apply_active_classes = context.get('apply_active_classes', True)

    if allow_repeating_parents is None:
        allow_repeating_parents = context.get('allow_repeating_parents', True)

    menu_items = prime_menu_items(
        menu_items=parent_page.get_children().live().in_menu(),
        current_site=current_site,
        current_page=current_page,
        current_page_ancestor_ids=ancestor_ids,
        check_for_children=not stop_at_this_level,
        allow_repeating_parents=allow_repeating_parents,
        apply_active_classes=apply_active_classes
    )

    if allow_repeating_parents:
        if getattr(parent_page, 'repeat_in_subnav', False):
            extra_item = deepcopy(parent_page)
            href = parent_page.relative_url(current_site)
            text = parent_page.repeated_item_text or parent_page.title
            setattr(extra_item, 'href', href)
            setattr(extra_item, 'text', text)
            if apply_active_classes:
                if parent_page.pk == getattr(current_page, 'pk', 0):
                    active_css_class = app_settings.ACTIVE_CLASS
                    setattr(extra_item, 'active_class', active_css_class)
            menu_items.insert(0, extra_item)
  
    context.update({
        'parent_page': parent_page,
        'menu_items': menu_items,
        'allow_repeating_parents': allow_repeating_parents,
        'current_level': current_level,
        'max_levels': max_levels,
        'current_template': template,
    })
    t = context.template.engine.get_template(template)
    return t.render(context)


@register.simple_tag(takes_context=True)
def children_menu(
    context, parent_page=None, allow_repeating_parents=True,
    apply_active_classes=False,
    max_levels=app_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS,
    template=app_settings.DEFAULT_CHILDREN_MENU_TEMPLATE
):
    if parent_page is None:
        parent_page = context.get('self')
        if not isinstance(parent_page, Page):
            return ''

    context.update({
        'current_level': 0,
        'max_levels': max_levels,
    })
    return sub_menu(
        context,
        menuitem_or_page=parent_page,
        stop_at_this_level=None,
        allow_repeating_parents=allow_repeating_parents,
        apply_active_classes=apply_active_classes,
        template=template,
    )


def prime_menu_items(
    menu_items, current_site, current_page, current_page_ancestor_ids,
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
                if (menuitem is None or menuitem.allow_subnav):
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
                ancestor_class = app_settings.ACTIVE_ANCESTOR_CLASS
                active_class = app_settings.ACTIVE_CLASS
                if current_page and page.pk == current_page.pk:
                    if page_is_repeated_in_subnav:
                        setattr(item, 'active_class', ancestor_class)
                    else:
                        setattr(item, 'active_class', active_class)
                elif page.depth > 2 and page.pk in current_page_ancestor_ids:
                    setattr(item, 'active_class', ancestor_class)

            primed_menu_items.append(item)

        elif page is None:
            primed_menu_items.append(item)
    return primed_menu_items
