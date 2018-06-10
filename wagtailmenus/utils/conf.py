import warnings
from importlib import import_module
from django.core.exceptions import ImproperlyConfigured


class AppSettings:

    def __init__(self, prefix, defaults):
        from django.conf import settings  # delay import until needed
        self.prefix = prefix
        self.defaults = defaults
        self._django_settings = settings

    def __getattr__(self, name):
        try:
            return self.get(name)
        except KeyError:
            return super().__getattr__(name)

    def get(self, setting_name):
        """
        Returns the value of the app setting named by ``setting_name``. If
        the setting is unavailable in the Django settings module, then the
        default value from the ``defaults`` dictionary is returned.
        """
        default = self.defaults[setting_name]
        attr_name = self.prefix + setting_name
        return getattr(self._django_settings, attr_name, default)

    def get_or_try_deprecated_name(
        self, new_setting_name, deprecated_setting_name, warning_category=None
    ):
        """
        As get(), but if no setting can be found in the Django settings
        module matching ``new_setting_name``, will also attempt to find
        a setting matching ``deprecated_setting_name``, before resulting to
        returning the relevant default value from the ``defaults`` dictionary.

        If a setting is found matching ``deprecated_setting_name``, a sensibly
        worded deprecation warning is raised. The ``warning_category``
        argument can be used to specify the warning categry class to use
        for this warning (The built-in ``DeprecationWarning`` is used by
        default).
        """
        prefixed_new_name = self.prefix + new_setting_name
        prefixed_deprecated_name = self.prefix + deprecated_setting_name
        try:
            return getattr(self._django_settings, prefixed_new_name)
        except AttributeError:
            pass
        try:
            value = getattr(self._django_settings, prefixed_deprecated_name)
            warnings.warn(
                "The {deprecated_name} setting is deprecated in favour of "
                "using {new_name}. Please update your settings module to "
                "use the new setting name.".format(
                    deprecated_name=prefixed_deprecated_name,
                    new_name=prefixed_new_name,
                ),
                category=warning_category or DeprecationWarning
            )
            return value
        except AttributeError:
            pass
        return self.defaults[new_setting_name]

    def get_class(self, setting_name):
        """Returns a python class, method, module or other object referenced by
        an app setting who's value should be a valid import path string."""
        value = getattr(self, setting_name)
        try:
            module_path, class_name = value.rsplit(".", 1)
            return getattr(import_module(module_path), class_name)
        except(ImportError, ValueError):
            raise ImproperlyConfigured(
                "'%s' is not a valid import path. %s%s must be a full "
                "dotted python import path e.g. 'project.app.module.Class'" %
                (value, self.prefix, setting_name)
            )

    def get_model(self, setting_name):
        """Returns a Django model referenced by an app setting who's value
        should be a 'model' string in the format 'app_label.model_name'."""
        from django.apps import apps  # delay import until needed
        value = getattr(self, setting_name)
        try:
            return apps.get_model(value)
        except ValueError:
            raise ImproperlyConfigured(
                "%s%s must be in the format 'app_label.model_name'" %
                (self.prefix, setting_name)
            )
        except LookupError:
            raise ImproperlyConfigured(
                "%s%s refers to model '%s' that has not been installed" %
                (self.prefix, setting_name, value)
            )
