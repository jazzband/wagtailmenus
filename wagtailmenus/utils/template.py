import warnings

from wagtailmenus import app_settings
from .deprecation import RemovedInWagtailMenus27Warning
from .misc import get_site_from_request


def get_template_names(menu_tag, request, override):
    warning_msg = (
        "The 'get_template_names' method wagtailmenus.utils.template has been "
        "deprecated in favour of building this behaviour into the base Menu "
        "class"
    )
    warnings.warn(warning_msg, RemovedInWagtailMenus27Warning)
    if override:
        return [override]
    template_names = []
    site = get_site_from_request(request, fallback_to_default=True)
    if app_settings.SITE_SPECIFIC_TEMPLATE_DIRS and site:
        hostname = site.hostname
        template_names.extend([
            "menus/%s/%s/menu.html" % (hostname, menu_tag),
            "menus/%s/%s_menu.html" % (hostname, menu_tag),
        ])
    template_names.append("menus/%s/menu.html" % menu_tag)
    if menu_tag == 'main':
        template_names.append(app_settings.DEFAULT_MAIN_MENU_TEMPLATE)
    elif menu_tag == 'section':
        template_names.append(app_settings.DEFAULT_SECTION_MENU_TEMPLATE)
    elif menu_tag == 'children':
        template_names.append(app_settings.DEFAULT_CHILDREN_MENU_TEMPLATE)
    return template_names


def get_sub_menu_template_names(menu_tag, request, override):
    warning_msg = (
        "The 'get_sub_menu_template_names' method wagtailmenus.utils.template "
        "has been deprecated in favour of building this behaviour into the "
        "menu classes that need it"
    )
    warnings.warn(warning_msg, RemovedInWagtailMenus27Warning)
    if override:
        return [override]
    template_names = []
    if app_settings.SITE_SPECIFIC_TEMPLATE_DIRS and getattr(
        request, 'site', None
    ):
        hostname = request.site.hostname
        template_names.extend([
            "menus/%s/%s/sub_menu.html" % (hostname, menu_tag),
            "menus/%s/%s_sub_menu.html" % (hostname, menu_tag),
            "menus/%s/sub_menu.html" % hostname,
        ])
    template_names.extend([
        "menus/%s/sub_menu.html" % menu_tag,
        "menus/%s_sub_menu.html" % menu_tag,
        app_settings.DEFAULT_SUB_MENU_TEMPLATE,
    ])
    return template_names
