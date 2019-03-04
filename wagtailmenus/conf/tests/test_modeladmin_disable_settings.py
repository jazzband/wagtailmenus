from importlib import reload
from unittest.mock import call, patch

from django.test import TestCase, override_settings

from wagtailmenus.modeladmin import FlatMenuAdmin, MainMenuAdmin
from wagtailmenus import wagtail_hooks


class TestDisablingFlatMenusInWagtailCMS(TestCase):
    """
    Tests if modeladmin is registered based on settings.
    """
    @patch('wagtail.contrib.modeladmin.options.modeladmin_register')
    def test_modeladmin_registered_by_default(self, mock_modeladmin_register):
        reload(wagtail_hooks)
        self.assertIn(
            call(FlatMenuAdmin),
            mock_modeladmin_register.mock_calls
        )

    @override_settings(
        WAGTAILMENUS_FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN=False,
    )
    @patch('wagtail.contrib.modeladmin.options.modeladmin_register')
    def test_modeladmin_not_registered_if_disabled(self, mock_modeladmin_register):
        """
        Disabling the 'Flat menu' via setting should prevent registering the
        FlatMenuAdmin, but MainMenuAdmin should still be registered.
        """
        reload(wagtail_hooks)
        self.assertNotIn(
            call(FlatMenuAdmin),
            mock_modeladmin_register.mock_calls
        )
        mock_modeladmin_register.assert_called_with(MainMenuAdmin)


class TestDisablingMainMenusInWagtailCMS(TestCase):

    @patch('wagtail.contrib.modeladmin.options.modeladmin_register')
    def test_modeladmin_registered_by_default(self, mock_modeladmin_register):
        reload(wagtail_hooks)
        self.assertIn(
            call(MainMenuAdmin),
            mock_modeladmin_register.mock_calls
        )

    @override_settings(
        WAGTAILMENUS_MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN=False,
    )
    @patch('wagtail.contrib.modeladmin.options.modeladmin_register')
    def test_disable_main_menus(self, mock_modeladmin_register):
        """
        Disabling the 'Main menu' via setting should prevent registering the
        MainMenuAdmin, but FlatMenuAdmin should still be registered.
        """
        reload(wagtail_hooks)
        self.assertNotIn(
            call(MainMenuAdmin),
            mock_modeladmin_register.mock_calls
        )
        mock_modeladmin_register.assert_called_with(FlatMenuAdmin)
