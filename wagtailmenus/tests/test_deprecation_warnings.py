import warnings

from django.test import TestCase, override_settings


class TestDeprecationWarningsRaised(TestCase):

    @override_settings(WAGTAILMENUS_CHILDREN_MENU_CLASS_PATH='wagtailmenus.tests.models.CustomChildrenMenu',)
    def test_warns_when_value_found_using_deprecated_setting_name(self):
        from wagtailmenus.conf import settings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(
                settings.CHILDREN_MENU_CLASS,
                'wagtailmenus.tests.models.CustomChildrenMenu'
            )
        self.assertIn(
            "The WAGTAILMENUS_CHILDREN_MENU_CLASS_PATH setting is "
            "deprecated in favour of using WAGTAILMENUS_CHILDREN_MENU_CLASS",
            str(w[0].message)
        )

    @override_settings(WAGTAILMENUS_CHILDREN_MENU_CLASS_PATH='wagtailmenus.tests.models.CustomChildrenMenu',)
    def test_warns_when_deprecated_setting_referenced_on_settings_module(self):
        from wagtailmenus.conf import settings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(
                settings.CHILDREN_MENU_CLASS_PATH,
                'wagtailmenus.tests.models.CustomChildrenMenu'
            )
        self.assertIn(
            "CHILDREN_MENU_CLASS_PATH is deprecated in favour of using "
            "CHILDREN_MENU_CLASS in app settings",
            str(w[0].message)
        )

    def test_warns_when_app_settings_imported_from_old_location(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from wagtailmenus import app_settings
            from wagtailmenus import conf
            self.assertIs(
                app_settings.CHILDREN_MENU_CLASS,
                conf.settings.CHILDREN_MENU_CLASS
            )
        self.assertIn(
            "The 'wagtailmenus.app_settings' module is deprecated",
            str(w[0].message)
        )

    def test_warns_when_constants_imported_from_old_location(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from wagtailmenus import constants
            from wagtailmenus import conf
            self.assertIs(
                constants.USE_SPECIFIC_OFF,
                conf.constants.USE_SPECIFIC_OFF
            )
        self.assertIn(
            "The 'wagtailmenus.constants' module is deprecated",
            str(w[0].message)
        )
