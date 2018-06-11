import warnings
from importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.utils.translation import ugettext_lazy as _


class BaseAppSettingsHelper:

    prefix = ''

    def __init__(self, defaults):
        from django.conf import settings
        self._defaults = defaults
        self._django_settings = settings
        self._import_cache = {}
        self._model_cache = {}
        setting_changed.connect(self.clear_caches, dispatch_uid=id(self))

    def __getattr__(self, name):
        if hasattr(self._defaults, name):
            return self.get(name)
        raise AttributeError

    def clear_caches(self, **kwargs):
        self._import_cache = {}
        self._model_cache = {}

    def get_default_value(self, setting_name):
        return getattr(self._defaults, setting_name)

    def get_user_defined_value(self, setting_name):
        attr_name = self.prefix + setting_name
        return getattr(self._django_settings, attr_name)

    def is_overridden(self, setting_name):
        return hasattr(self._django_settings, self.prefix + setting_name)

    def get(self, setting_name):
        """
        Returns the value of the app setting named by ``setting_name``. If
        the setting is unavailable in the Django settings module, then the
        default value from the ``defaults`` dictionary is returned.
        """
        if self.is_overridden(setting_name):
            return self.get_user_defined_value(setting_name)
        return self.get_default_value(setting_name)

    def get_or_try_other(self, setting_name, other_setting_name):
        """
        Returns a tuple containing two values:

        1. The setting value itself, which may have come from the Django
           settings, or may also be the default value.
        2. A boolean indicating whether the value was found in the Django
           settings module with a name matching ``other_setting_name``.
        """
        if self.is_overridden(setting_name):
            return self.get_user_defined_value(setting_name), False
        if self.is_overridden(other_setting_name):
            return self.get_user_defined_value(other_setting_name), True
        return self.get_default_value(setting_name), False

    def get_or_try_deprecated_name(
        self, setting_name, deprecated_setting_name, warning_category=None
    ):
        """
        Use this instead of get() when an established app setting is renamed,
        and you wish to continue to respect settings defined using the old name
        for a time, before forcing developers to use the new one.

        If a setting is found matching ``deprecated_setting_name``, a sensibly
        worded deprecation warning is raised. The ``warning_category``
        argument can be used to specify the warning categry class to use
        for this warning. If not supplied the built-in ``DeprecationWarning``
        class is used.
        """
        setting_value, value_from_deprecated_setting = self.get_or_try_other(
            setting_name, deprecated_setting_name)
        if not value_from_deprecated_setting:
            return setting_value
        warnings.warn(_(
            "The {deprecated_setting_name} setting is deprecated in favour "
            "of using {new_setting_name}. Please update your project's "
            "settings module to use the new setting name."
        ).format(
            deprecated_setting_name=self.prefix + deprecated_setting_name,
            new_setting_name=self.prefix + setting_name
        ), category=warning_category or DeprecationWarning)
        return setting_value

    def get_class(self, setting_name):
        """
        Returns a python class, method, module or other object referenced by
        an app setting who's value should be a valid import path string. Raises
        an ``ImproperlyConfigured`` error if the setting value is not a valid
        import path.
        """
        if setting_name in self._import_cache:
            return self._import_cache[setting_name]

        setting_value = getattr(self, setting_name)
        try:
            module_path, class_name = setting_value.rsplit(".", 1)
            result = getattr(import_module(module_path), class_name)
            self._import_cache[setting_name] = result
            return result
        except(ImportError, ValueError):
            raise ImproperlyConfigured(_(
                "'{value}' is not a valid import path. {setting_name} must be "
                "a full dotted python import path e.g. "
                "'project.app.module.Class'."
            ).format(
                value=setting_value,
                setting_name=self.prefix + setting_name,
            ))

    def get_model(self, setting_name):
        """
        Returns a Django model referenced by an app setting who's value should
        be a 'model string' in the format 'app_label.model_name'. Raises an
        ``ImproperlyConfigured`` error if the setting value is not in the
        correct format, or does not refers to a model that is not available.
        """
        if setting_name in self._model_cache:
            return self._model_cache[setting_name]

        from django.apps import apps  # delay import until needed
        setting_value = getattr(self, setting_name)
        try:
            result = apps.get_model(setting_value)
            self._model_cache[setting_name] = result
            return result
        except ValueError:
            raise ImproperlyConfigured(_(
                "{setting_name} must be in the format 'app_label.model_name'."
            ).format(setting_name=self.prefix + setting_name))
        except LookupError:
            raise ImproperlyConfigured(_(
                "{setting_name} refers to model '{model_string}' that has not "
                "been installed."
            ).format(
                model_string=setting_value,
                setting_name=self.prefix + setting_name,
            ))
