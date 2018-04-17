# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.test import TestCase, override_settings
from mock import call, patch

from wagtailmenus import wagtail_hooks

try:
    from importlib import reload  # Python 3.4+
except ImportError:
    try:
        from imp import reload  # Python 3
    except ImportError:
        import reload  # Python 2.x


class TestDisablingMenusInWagtailCMS(TestCase):
    """
    Tests if modeladmin is registered based on settings.
    """
    @override_settings(
        WAGTAILMENUS_MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN=True,
        WAGTAILMENUS_FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN=True,
    )
    @patch('wagtail.contrib.modeladmin.options.modeladmin_register')
    def test_enabled_both_menus(self, mock_modeladmin_register):
        """
        Enabling both wagtailmenus should register both modeladmins.
        """
        reload(wagtail_hooks)
        self.assertIn(
            call(wagtail_hooks.MainMenuAdmin),
            mock_modeladmin_register.mock_calls)
        self.assertIn(
            call(wagtail_hooks.FlatMenuAdmin),
            mock_modeladmin_register.mock_calls)

    @override_settings(
        WAGTAILMENUS_MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN=False,
    )
    @patch('wagtail.contrib.modeladmin.options.modeladmin_register')
    def test_disable_main_menus(self, mock_modeladmin_register):
        """
        Disabling the 'Main menu' via setting should prevent registering the
        MainMenuAdmin.
        """
        reload(wagtail_hooks)
        self.assertNotIn(
            call(wagtail_hooks.MainMenuAdmin),
            mock_modeladmin_register.mock_calls)
        mock_modeladmin_register.assert_called_once_with(
            wagtail_hooks.FlatMenuAdmin)

    @override_settings(
        WAGTAILMENUS_FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN=False,
    )
    @patch('wagtail.contrib.modeladmin.options.modeladmin_register')
    def test_disable_flat_menus(self, mock_modeladmin_register):
        """
        Disabling the 'Flat menu' via setting should prevent registering the
        FlatMenuAdmin.
        """
        reload(wagtail_hooks)
        self.assertNotIn(
            call(wagtail_hooks.FlatMenuAdmin),
            mock_modeladmin_register.mock_calls)
        mock_modeladmin_register.assert_called_once_with(
            wagtail_hooks.MainMenuAdmin)
