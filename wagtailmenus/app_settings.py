from django.utils.translation import ugettext_lazy as _


class AppSettings:
    """Props to django-allauth for the inspiration"""

    USE_SPECIFIC_OFF = 0
    USE_SPECIFIC_AUTO = 1
    USE_SPECIFIC_TOP_LEVEL = 2
    USE_SPECIFIC_ALWAYS = 3
    USE_SPECIFIC_CHOICES = (
        (USE_SPECIFIC_OFF, _("Off (most efficient)")),
        (USE_SPECIFIC_AUTO, _("Auto")),
        (USE_SPECIFIC_TOP_LEVEL, _("Top level")),
        (USE_SPECIFIC_ALWAYS, _("Always (least efficient)")),
    )
    MAX_LEVELS_CHOICES = (
        (1, _('1: No sub-navigation (flat)')),
        (2, _('2: Allow 1 level of sub-navigation')),
        (3, _('3: Allow 2 levels of sub-navigation')),
        (4, _('4: Allow 3 levels of sub-navigation')),
    )

    def __init__(self, prefix):
        from django.conf import settings
        self._prefix = prefix
        self._settings = settings

    def _setting(self, name, default):
        return getattr(self._settings, self._prefix + name, default)

    def class_from_path_setting(self, path_setting_name):
        from importlib import import_module
        from django.core.exceptions import ImproperlyConfigured
        try:
            import_path = getattr(self, path_setting_name)
            module_path, class_name = import_path.rsplit(".", 1)
            return getattr(import_module(module_path), class_name)
        except(ImportError, ValueError):
            raise ImproperlyConfigured(
                "'%s' is not a valid import path. %s%s must be a full "
                "dotted python import path e.g. 'project.app.file.Class'" %
                (import_path, self._prefix, path_setting_name)
            )

    def model_from_path_setting(self, path_setting_name):
        from django.apps import apps
        from django.core.exceptions import ImproperlyConfigured
        model_name = getattr(self, path_setting_name)
        try:
            return apps.get_model(model_name)
        except ValueError:
            raise ImproperlyConfigured(
                "%s%s must be of the form 'app_label.model_name'" %
                (self._prefix, path_setting_name)
            )
        except LookupError:
            raise ImproperlyConfigured(
                "%s%s refers to model '%s' that has not been installed" %
                (self._prefix, path_setting_name, model_name)
            )

    @property
    def ACTIVE_CLASS(self):
        return self._setting('ACTIVE_CLASS', 'active')

    @property
    def ADD_EDITOR_OVERRIDE_STYLES(self):
        return self._setting('ADD_EDITOR_OVERRIDE_STYLES', True)

    @property
    def ACTIVE_ANCESTOR_CLASS(self):
        return self._setting('ACTIVE_ANCESTOR_CLASS', 'ancestor')

    @property
    def MAINMENU_MENU_ICON(self):
        return self._setting('MAINMENU_MENU_ICON', 'list-ol')

    @property
    def FLATMENU_MENU_ICON(self):
        return self._setting('FLATMENU_MENU_ICON', 'list-ol')

    @property
    def USE_CONDENSEDINLINEPANEL(self):
        return self._setting('USE_CONDENSEDINLINEPANEL', True)

    @property
    def SITE_SPECIFIC_TEMPLATE_DIRS(self):
        return self._setting('SITE_SPECIFIC_TEMPLATE_DIRS', False)

    @property
    def SECTION_ROOT_DEPTH(self):
        return self._setting('SECTION_ROOT_DEPTH', 3)

    @property
    def GUESS_TREE_POSITION_FROM_PATH(self):
        return self._setting('GUESS_TREE_POSITION_FROM_PATH', True)

    @property
    def FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS(self):
        return self._setting(
            'FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS', False
        )

    @property
    def DEFAULT_MAIN_MENU_TEMPLATE(self):
        return self._setting(
            'DEFAULT_MAIN_MENU_TEMPLATE', 'menus/main_menu.html'
        )

    @property
    def DEFAULT_FLAT_MENU_TEMPLATE(self):
        return self._setting(
            'DEFAULT_FLAT_MENU_TEMPLATE', 'menus/flat_menu.html'
        )

    @property
    def DEFAULT_SECTION_MENU_TEMPLATE(self):
        return self._setting(
            'DEFAULT_SECTION_MENU_TEMPLATE', 'menus/section_menu.html'
        )

    @property
    def DEFAULT_CHILDREN_MENU_TEMPLATE(self):
        return self._setting(
            'DEFAULT_CHILDREN_MENU_TEMPLATE', 'menus/children_menu.html'
        )

    @property
    def DEFAULT_SUB_MENU_TEMPLATE(self):
        return self._setting(
            'DEFAULT_SUB_MENU_TEMPLATE', 'menus/sub_menu.html'
        )

    @property
    def DEFAULT_SECTION_MENU_MAX_LEVELS(self):
        return self._setting('DEFAULT_SECTION_MENU_MAX_LEVELS', 2)

    @property
    def DEFAULT_CHILDREN_MENU_MAX_LEVELS(self):
        return self._setting('DEFAULT_CHILDREN_MENU_MAX_LEVELS', 1)

    @property
    def DEFAULT_SECTION_MENU_USE_SPECIFIC(self):
        return self._setting(
            'DEFAULT_SECTION_MENU_USE_SPECIFIC', self.USE_SPECIFIC_AUTO
        )

    @property
    def DEFAULT_CHILDREN_MENU_USE_SPECIFIC(self):
        return self._setting(
            'DEFAULT_CHILDREN_MENU_USE_SPECIFIC', self.USE_SPECIFIC_AUTO
        )

    @property
    def FLAT_MENUS_HANDLE_CHOICES(self):
        return self._setting('FLAT_MENUS_HANDLE_CHOICES', None)

    @property
    def PAGE_FIELD_FOR_MENU_ITEM_TEXT(self):
        return self._setting("PAGE_FIELD_FOR_MENU_ITEM_TEXT", 'title')

    @property
    def MAIN_MENU_MODEL(self):
        return self._setting('MAIN_MENU_MODEL', 'wagtailmenus.MainMenu')

    @property
    def MAIN_MENU_MODEL_CLASS(self):
        return self.model_from_path_setting('MAIN_MENU_MODEL')

    @property
    def FLAT_MENU_MODEL(self):
        return self._setting('FLAT_MENU_MODEL', 'wagtailmenus.FlatMenu')

    @property
    def FLAT_MENU_MODEL_CLASS(self):
        return self.model_from_path_setting('FLAT_MENU_MODEL')

    @property
    def MAIN_MENU_ITEMS_RELATED_NAME(self):
        return self._setting('MAIN_MENU_ITEMS_RELATED_NAME', 'menu_items')

    @property
    def FLAT_MENU_ITEMS_RELATED_NAME(self):
        return self._setting('FLAT_MENU_ITEMS_RELATED_NAME', 'menu_items')

    @property
    def CHILDREN_MENU_CLASS_PATH(self):
        return self._setting(
            'CHILDREN_MENU_CLASS_PATH', 'wagtailmenus.models.ChildrenMenu'
        )

    @property
    def CHILDREN_MENU_CLASS(self):
        return self.class_from_path_setting('CHILDREN_MENU_CLASS_PATH')

    @property
    def SECTION_MENU_CLASS_PATH(self):
        return self._setting(
            'SECTION_MENU_CLASS_PATH', 'wagtailmenus.models.SectionMenu'
        )

    @property
    def SECTION_MENU_CLASS(self):
        return self.class_from_path_setting('SECTION_MENU_CLASS_PATH')

    # TODO: To be removed in v2.8.0
    @property
    def USE_BACKEND_SPECIFIC_TEMPLATES(self):
        return self._setting('USE_BACKEND_SPECIFIC_TEMPLATES', False)


import sys  # noqa

app_settings = AppSettings('WAGTAILMENUS_')
app_settings.__name__ = __name__
sys.modules[__name__] = app_settings
