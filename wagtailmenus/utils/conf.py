from importlib import import_module
from django.core.exceptions import ImproperlyConfigured


class AppSettings:

    def __init__(self, prefix, defaults):
        self.prefix = prefix
        self.defaults = defaults

    def __getattr__(self, name):
        try:
            return self.get(name)
        except KeyError:
            return super().__getattr__(name)

    def get(self, setting_name):
        """Returns an app setting value in it's native format, e.g.
        string, integer, boolean. If the setting cannot be found in django
        project settings, the relevant default value from defaults is returned.
        """
        from django.conf import settings  # delay import until needed
        default = self.defaults[setting_name]
        return getattr(settings, self.prefix + setting_name, default)

    def get_class(self, setting_name):
        """Returns a python class, method, module or other object referenced by
        an app setting who's value should be a valid import path string."""
        value = self.get(setting_name)
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
        value = self.get(setting_name)
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
