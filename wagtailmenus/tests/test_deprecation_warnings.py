import warnings

from django.test import TestCase


class TestDeprecationWarningsRaised(TestCase):

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
