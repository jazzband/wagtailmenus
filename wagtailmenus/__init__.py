from wagtailmenus.utils.version import get_version, get_stable_branch_name

# major.minor.patch.release.number
# release must be one of alpha, beta, rc, or final
VERSION = (3, 1, 3, "final", 0)
__version__ = get_version(VERSION)
stable_branch_name = get_stable_branch_name(VERSION)

default_app_config = "wagtailmenus.apps.WagtailMenusConfig"


def get_main_menu_model_string():
    """
    Get the dotted ``app.Model`` name for the main menu model as a string.
    Useful for developers extending wagtailmenus, that need to refer to the
    main menu model (such as in foreign keys), but the model itself is not
    required.
    """
    from wagtailmenus.conf import settings

    return settings.MAIN_MENU_MODEL


def get_flat_menu_model_string():
    """
    Get the dotted ``app.Model`` name for the flat menu model as a string.
    Useful for developers extending wagtailmenus, that need to refer to the
    flat menu model (such as in foreign keys), but the model itself is not
    required.
    """
    from wagtailmenus.conf import settings

    return settings.FLAT_MENU_MODEL


def get_main_menu_model():
    """
    Get the model from the ``WAGTAILMENUS_MAIN_MENU_MODEL`` setting.
    Useful for developers extending wagtailmenus, and need the actual model.
    Defaults to the standard :class:`~wagtailmenus.models.MainMenu` model
    if no custom model is defined.
    """
    from wagtailmenus.conf import settings

    return settings.models.MAIN_MENU_MODEL


def get_flat_menu_model():
    """
    Get the model from the ``WAGTAILMENUS_FLAT_MENU_MODEL`` setting.
    Useful for developers extending wagtailmenus, and need to the actual model.
    Defaults to the standard :class:`~wagtailmenus.models.FlatMenu` model
    if no custom model is defined.
    """
    from wagtailmenus.conf import settings

    return settings.models.FLAT_MENU_MODEL
