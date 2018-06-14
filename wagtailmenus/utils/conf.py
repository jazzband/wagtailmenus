import warnings
from importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed


class BaseAppSettingsHelper:

    prefix = ''
    defaults = None
    deprecations = ()

    def __init__(self, prefix=None, defaults=None, deprecations=None):
        from django.conf import settings
        self._prefix = prefix or self.__class__.prefix
        self._defaults = defaults or self.__class__.defaults
        self._django_settings = settings
        self._import_cache = {}
        self._model_cache = {}
        self._deprecations = deprecations or self.__class__.deprecations
        self.perepare_deprecation_data()
        setting_changed.connect(self.clear_caches, dispatch_uid=id(self))

    def in_defaults(self, setting_name):
        return hasattr(self._defaults, setting_name)

    def perepare_deprecation_data(self):
        """
        Cycles through the list of AppSettingDeprecation instances set on
        ``self._deprecations`` and creates two new dictionaries on it:

        ``self._deprecated_settings``:
            Uses the deprecated setting names as keys, and will be
            used to identify if a requested setting value if for a deprecated
            setting.

        ``self._replacement_settings``:
            Uses the 'replacement setting' names as keys (if supplied), and
            allows us to temporarily support user-defined settings using the
            old name when the new setting is requested.
        """
        if not isinstance(self._deprecations, (list, tuple)):
            raise ImproperlyConfigured(
                "'deprecations' must be a list or tuple, not {}.".format(
                    type(self._deprecations).__name__
                )
            )

        self._deprecated_settings = {}
        self._replacement_settings = {}

        for item in self._deprecations:
            item.prefix = self._prefix
            self._deprecated_settings[item.setting_name] = item
            if not self.in_defaults(item.setting_name):
                raise ImproperlyConfigured(
                    "'{setting_name}' cannot be found in the defaults module. "
                    "A value should remain present there until the end of the "
                    "setting's deprecation period.".format(
                        setting_name=item.setting_name,
                    )
                )
            if item.replacement_name:
                self._replacement_settings[item.replacement_name] = item
                if not self.in_defaults(item.replacement_name):
                    raise ImproperlyConfigured(
                        "'{replacement_name}' is not a valid replacement "
                        "for {setting_name}. Please ensure {replacement_name} "
                        "has been added to the defaults module.".format(
                            replacement_name=item.replacement_name,
                            setting_name=item.setting_name,
                        )
                    )

    def __getattr__(self, name):
        if hasattr(self._defaults, name):
            return self.get(name)
        raise AttributeError("'{}' object has no attribute '{}'".format(
            self.__class__.__name__, name))

    def clear_caches(self, **kwargs):
        self._import_cache = {}
        self._model_cache = {}

    def get_default_value(self, setting_name):
        if self.in_defaults(setting_name):
            return getattr(self._defaults, setting_name)
        raise ImproperlyConfigured(
            "'{setting_name}' could not be found in the defaults module."
            .format(setting_name=setting_name)
        )

    def get_user_defined_value(self, setting_name):
        attr_name = self._prefix + setting_name
        return getattr(self._django_settings, attr_name)

    def is_overridden(self, setting_name):
        return hasattr(self._django_settings, self._prefix + setting_name)

    def get(self, setting_name):
        """
        Returns the value of the app setting named by ``setting_name``.
        If the setting is unavailable in the Django settings module, then the
        default value from the ``defaults`` dictionary is returned.

        If the setting is deprecated, a suitable deprecation warning will be
        raised, to help inform developers of the change.

        If the named setting replaces a deprecated setting, and no user defined
        setting name is defined using the new name, the method will look for a
        user defined setting using the old name, and return that if found. A
        deprecation warning will also be raised.
        """
        if setting_name in self._deprecated_settings:
            depr = self._deprecated_settings[setting_name]
            depr.warn_if_referenced_directly()

        if self.is_overridden(setting_name):
            return self.get_user_defined_value(setting_name)

        if setting_name in self._replacement_settings:
            depr = self._replacement_settings[setting_name]
            if self.is_overridden(depr.setting_name):
                depr.warn_if_deprecated_value_used_by_replacement()
                return self.get_user_defined_value(depr.setting_name)

        return self.get_default_value(setting_name)

    def get_object(self, setting_name):
        """
        Returns a python class, method, module or other object referenced by
        an app setting who's value should be a string representation of a valid
        python import path.

        Will not work for relative paths.

        Raises an ``ImproperlyConfigured`` error if the setting value is not
        a valid import path.
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
            raise ImproperlyConfigured(
                "'{value}' is not a valid import path. {setting_name} must be "
                "a full dotted python import path e.g. "
                "'project.app.module.Class'.".format(
                    value=setting_value,
                    setting_name=self._prefix + setting_name,
                ))

    def get_model(self, setting_name):
        """
        Returns a Django model referenced by an app setting who's value should
        be a 'model string' in the format 'app_label.model_name'.

        Raises an ``ImproperlyConfigured`` error if the setting value is not
        in the correct format, or refers to a model that is not available.
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
            raise ImproperlyConfigured(
                "{setting_name} must be in the format 'app_label.model_name'."
                .format(setting_name=self._prefix + setting_name))
        except LookupError:
            raise ImproperlyConfigured(
                "{setting_name} refers to model '{model_string}' that has not "
                "been installed.".format(
                    model_string=setting_value,
                    setting_name=self._prefix + setting_name,
                ))


class AppSettingDeprecation:
    """
    A class to store details about a deprecated app setting, and to help
    raise deprecation warnings when the deprecated setting is used somehow.
    """
    def __init__(self, setting_name, replaced_by=None, warning_category=None):
        self.setting_name = setting_name
        self.replacement_name = replaced_by
        self.warning_category = warning_category or DeprecationWarning
        self._prefix = ''

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        self._prefix = value

    def warn_if_referenced_directly(self):
        if self.replacement_name is not None:
            msg = (
                "{setting_name} is deprecated in favour of using "
                "{replacement_name} in app settings. Please update your code "
                "to reference this new attribute on the module instead of "
                "the deprecated one."
            )
        else:
            msg = "The {setting_name} app setting is deprecated."

        warnings.warn(
            msg.format(
                setting_name=self.setting_name,
                replacement_name=self.replacement_name,
            ),
            category=self.warning_category
        )

    def warn_if_deprecated_value_used_by_replacement(self):
        warnings.warn(
            "The {setting_name} setting is deprecated in favour of "
            "using {replacement_name}. Please update your project's "
            "Django settings to use the new setting name.".format(
                setting_name=self.prefix + self.setting_name,
                replacement_name=self.prefix + self.replacement_name,
            ),
            category=self.warning_category
        )
