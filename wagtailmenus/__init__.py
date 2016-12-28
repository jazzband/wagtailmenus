from __future__ import absolute_import, unicode_literals
from django.core.exceptions import ImproperlyConfigured
from .app_settings import Settings

__version__ = '2.1.0'

app_settings = Settings()


def get_main_menu_model_string():
    """
    Get the dotted ``app.Model`` name for the main menu model as a string.
    Useful for developers extending wagtailmenus, that need to refer to the
    main menu model (such as in foreign keys), but the model itself is not
    required.
    """
    return app_settings.MAIN_MENU_MODEL


def get_flat_menu_model_string():
    """
    Get the dotted ``app.Model`` name for the flat menu model as a string.
    Useful for developers extending wagtailmenus, that need to refer to the
    flat menu model (such as in foreign keys), but the model itself is not
    required.
    """
    return app_settings.FLAT_MENU_MODEL


def get_main_menu_model():
    """
    Get the image model from the ``WAGTAILMENUS_MAIN_MENU_MODEL`` setting.
    Useful for developers extending wagtailmenus, and need the actaul model.
    Defaults to the standard :class:`~wagtailmenus.models.MainMenu` model
    if no custom model is defined.
    """
    from django.apps import apps
    model_string = get_main_menu_model_string()
    try:
        return apps.get_model(model_string)
    except ValueError:
        raise ImproperlyConfigured(
            "WAGTAILMENUS_MAIN_MENU_MODEL must be of the form "
            "'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "WAGTAILMENUS_MAIN_MENU_MODEL refers to model '%s' that has not "
            "been installed" % model_string
        )


def get_flat_menu_model():
    """
    Get the image model from the ``WAGTAILMENUS_FLAT_MENU_MODEL`` setting.
    Useful for developers extending wagtailmenus, and need to the actual model.
    Defaults to the standard :class:`~wagtailmenus.models.FlatMenu` model
    if no custom model is defined.
    """
    from django.apps import apps
    model_string = get_flat_menu_model_string()
    try:
        return apps.get_model(model_string)
    except ValueError:
        raise ImproperlyConfigured(
            "WAGTAILMENUS_FLAT_MENU_MODEL must be of the form "
            "'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "WAGTAILMENUS_FLAT_MENU_MODEL refers to model '%s' that has not "
            "been installed" % model_string
        )
