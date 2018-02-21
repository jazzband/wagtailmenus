from django.template import Library
from wagtail import VERSION as WAGTAIL_VERSION
if WAGTAIL_VERSION >= (2, 0):
    from wagtail.core.models import Page
else:
    from wagtail.wagtailcore.models import Page

from wagtailmenus import app_settings
from wagtailmenus.errors import SubMenuUsageError
from wagtailmenus.utils.misc import validate_supplied_values

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
    context, menuitem_or_page, use_specific=None, allow_repeating_parents=None,
    apply_active_classes=None, template='', use_absolute_page_urls=None,
    **kwargs
):
    """
    Retrieve the children pages for the `menuitem_or_page` provided, turn them
    into menu items, and render them to a template.
    """
    validate_supplied_values('sub_menu', use_specific=use_specific,
                             menuitem_or_page=menuitem_or_page)

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
    if original_menu is None:
        raise SubMenuUsageError()

    menu_class = original_menu.get_sub_menu_class()
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
