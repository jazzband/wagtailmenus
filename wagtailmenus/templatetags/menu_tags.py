from django.template import Library
from wagtailmenus.conf import constants, settings
from wagtailmenus.errors import SubMenuUsageError
from wagtailmenus.utils.misc import validate_supplied_values
try:
    from wagtail.models import Page
except ImportError:
    from wagtail.core.models import Page

register = Library()


def split_if_string(val, separator=','):
    if isinstance(val, str):
        return tuple(item.strip() for item in val.split(separator))
    return val


@register.simple_tag(takes_context=True)
def main_menu(
    context, max_levels=None, apply_active_classes=True,
    allow_repeating_parents=True, show_multiple_levels=True,
    template='', sub_menu_template='', sub_menu_templates=None,
    use_absolute_page_urls=False, add_sub_menus_inline=None,
    **kwargs
):
    validate_supplied_values('main_menu', max_levels=max_levels)

    if not show_multiple_levels:
        max_levels = 1

    menu_class = settings.models.MAIN_MENU_MODEL
    return menu_class.render_from_tag(
        context=context,
        max_levels=max_levels,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents,
        use_absolute_page_urls=use_absolute_page_urls,
        add_sub_menus_inline=add_sub_menus_inline,
        template_name=template,
        sub_menu_template_name=sub_menu_template,
        sub_menu_template_names=split_if_string(sub_menu_templates),
        **kwargs
    )


@register.simple_tag(takes_context=True)
def flat_menu(
    context, handle, max_levels=None, show_menu_heading=False,
    apply_active_classes=False, allow_repeating_parents=True,
    show_multiple_levels=True, template='', sub_menu_template='',
    sub_menu_templates=None, fall_back_to_default_site_menus=None,
    use_absolute_page_urls=False, add_sub_menus_inline=None,
    **kwargs
):
    validate_supplied_values('flat_menu', max_levels=max_levels)

    if fall_back_to_default_site_menus is None:
        fall_back_to_default_site_menus = settings.FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS

    if not show_multiple_levels:
        max_levels = 1

    menu_class = settings.models.FLAT_MENU_MODEL
    return menu_class.render_from_tag(
        context=context,
        handle=handle,
        fall_back_to_default_site_menus=fall_back_to_default_site_menus,
        max_levels=max_levels,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents,
        use_absolute_page_urls=use_absolute_page_urls,
        add_sub_menus_inline=add_sub_menus_inline,
        template_name=template,
        sub_menu_template_name=sub_menu_template,
        sub_menu_template_names=split_if_string(sub_menu_templates),
        show_menu_heading=show_menu_heading,
        **kwargs
    )


@register.simple_tag(takes_context=True)
def section_menu(
    context, show_section_root=True, show_multiple_levels=True,
    apply_active_classes=True, allow_repeating_parents=True,
    max_levels=settings.DEFAULT_SECTION_MENU_MAX_LEVELS,
    template='', sub_menu_template='', sub_menu_templates=None,
    use_absolute_page_urls=False, add_sub_menus_inline=None,
    **kwargs
):
    """Render a section menu for the current section."""
    validate_supplied_values('section_menu', max_levels=max_levels)

    if not show_multiple_levels:
        max_levels = 1

    menu_class = settings.objects.SECTION_MENU_CLASS
    return menu_class.render_from_tag(
        context=context,
        max_levels=max_levels,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents,
        use_absolute_page_urls=use_absolute_page_urls,
        add_sub_menus_inline=add_sub_menus_inline,
        template_name=template,
        sub_menu_template_name=sub_menu_template,
        sub_menu_template_names=split_if_string(sub_menu_templates),
        show_section_root=show_section_root,
        **kwargs
    )


@register.simple_tag(takes_context=True)
def children_menu(
    context, parent_page=None, allow_repeating_parents=True,
    apply_active_classes=False,
    max_levels=settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS,
    template='', sub_menu_template='', sub_menu_templates=None,
    use_absolute_page_urls=False, add_sub_menus_inline=None,
    **kwargs
):
    validate_supplied_values(
        'children_menu',
        max_levels=max_levels,
        parent_page=parent_page,
    )

    menu_class = settings.objects.CHILDREN_MENU_CLASS
    return menu_class.render_from_tag(
        context=context,
        parent_page=parent_page,
        max_levels=max_levels,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents,
        use_absolute_page_urls=use_absolute_page_urls,
        add_sub_menus_inline=add_sub_menus_inline,
        template_name=template,
        sub_menu_template_name=sub_menu_template,
        sub_menu_template_names=split_if_string(sub_menu_templates),
        **kwargs
    )


@register.simple_tag(takes_context=True)
def sub_menu(
    context, menuitem_or_page, allow_repeating_parents=None,
    apply_active_classes=None, template='', use_absolute_page_urls=None,
    add_sub_menus_inline=None, **kwargs
):
    """
    Retrieve the children pages for the `menuitem_or_page` provided, turn them
    into menu items, and render them to a template.
    """
    validate_supplied_values('sub_menu', menuitem_or_page=menuitem_or_page)

    max_levels = context.get(
        'max_levels', settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS
    )

    if apply_active_classes is None:
        apply_active_classes = context.get('apply_active_classes', True)

    if allow_repeating_parents is None:
        allow_repeating_parents = context.get('allow_repeating_parents', True)

    if use_absolute_page_urls is None:
        use_absolute_page_urls = context.get('use_absolute_page_urls', False)

    if add_sub_menus_inline is None:
        add_sub_menus_inline = context.get('add_sub_menus_inline', False)

    if isinstance(menuitem_or_page, Page):
        parent_page = menuitem_or_page
    else:
        parent_page = menuitem_or_page.link_page

    original_menu = context.get('original_menu_instance')
    if original_menu is None:
        raise SubMenuUsageError()

    menu_class = original_menu.get_sub_menu_class()
    return menu_class.render_from_tag(
        context=context,
        parent_page=parent_page,
        max_levels=max_levels,
        apply_active_classes=apply_active_classes,
        allow_repeating_parents=allow_repeating_parents,
        use_absolute_page_urls=use_absolute_page_urls,
        add_sub_menus_inline=add_sub_menus_inline,
        template_name=template,
        **kwargs
    )
