from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from wagtail.core.models import Site

from wagtailmenus import get_main_menu_model, get_flat_menu_model
from wagtailmenus import models as default_models
from wagtailmenus.tests import models as test_models


class TestFlatMenuModelOverriding(TestCase):
    """
    Tests the effect of overriding ``WAGTAILMENUS_FLAT_MENU_MODEL``
    """

    def test_default_value(self):
        self.assertEqual(get_flat_menu_model(), default_models.FlatMenu)

    @override_settings(WAGTAILMENUS_FLAT_MENU_MODEL='tests.CustomFlatMenu')
    def test_successful_override(self):
        self.assertEqual(get_flat_menu_model(), test_models.CustomFlatMenu)

    @override_settings(WAGTAILMENUS_FLAT_MENU_MODEL='CustomFlatMenu')
    def test_error_raised_if_format_invalid(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "WAGTAILMENUS_FLAT_MENU_MODEL must be in the format "
            "'app_label.model_name'"
        )):
            get_flat_menu_model()

    @override_settings(WAGTAILMENUS_FLAT_MENU_MODEL='tests.NonExistentFlatMenu')
    def test_error_raised_if_model_not_installed(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "WAGTAILMENUS_FLAT_MENU_MODEL refers to model "
            "'tests.NonExistentFlatMenu' that has not been installed"
        )):
            get_flat_menu_model()


class TestFlatMenuItemOverriding(TestCase):
    """
    Tests the effect of overriding
    ``WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME``
    """

    def setUp(self):
        self.test_menu = default_models.FlatMenu.objects.create(
            site=Site.objects.get(),
            title="Test",
            handle='test'
        )

    def test_default_value(self):
        menu_item_manager = self.test_menu.get_menu_items_manager()
        self.assertEqual(menu_item_manager.model, default_models.FlatMenuItem)

    @override_settings(
        WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME='custom_menu_items'
    )
    def test_successful_override(self):
        menu_item_manager = self.test_menu.get_menu_items_manager()
        self.assertEqual(
            menu_item_manager.model, test_models.FlatMenuCustomMenuItem
        )

    @override_settings(
        WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME='invalid_related_name'
    )
    def test_invalid_value_raises_error(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "'invalid_related_name' isn't a valid relationship name for "
            "accessing menu items from FlatMenu."
        )):
            self.test_menu.get_menu_items_manager()


class TestMainMenuModelOverriding(TestCase):
    """
    Tests the effect of overriding ``WAGTAILMENUS_MAIN_MENU_MODEL``
    """

    def test_default_value(self):
        self.assertEqual(get_main_menu_model(), default_models.MainMenu)

    @override_settings(WAGTAILMENUS_MAIN_MENU_MODEL='tests.CustomMainMenu')
    def test_successful_override(self):
        self.assertEqual(get_main_menu_model(), test_models.CustomMainMenu)

    @override_settings(WAGTAILMENUS_MAIN_MENU_MODEL='CustomMainMenu')
    def test_error_raised_if_format_invalid(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
                "WAGTAILMENUS_MAIN_MENU_MODEL must be in the format "
                "'app_label.model_name'"
        )):
            get_main_menu_model()

    @override_settings(
        WAGTAILMENUS_MAIN_MENU_MODEL='tests.NonExistentMainMenu'
    )
    def test_error_raised_if_model_not_installed(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "WAGTAILMENUS_MAIN_MENU_MODEL refers to model "
            "'tests.NonExistentMainMenu' that has not been installed"
        )):
            get_main_menu_model()


class TestMainMenuItemOverriding(TestCase):
    """
    Tests the effect of overriding
    ``WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME``
    """

    def setUp(self):
        self.test_menu = default_models.MainMenu.objects.create(
            site=Site.objects.get())

    def test_default_value(self):
        menu_item_manager = self.test_menu.get_menu_items_manager()
        self.assertEqual(menu_item_manager.model, default_models.MainMenuItem)

    @override_settings(
        WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME='custom_menu_items'
    )
    def test_successful_override(self):
        menu_item_manager = self.test_menu.get_menu_items_manager()
        self.assertEqual(
            menu_item_manager.model, test_models.MainMenuCustomMenuItem
        )

    @override_settings(
        WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME='invalid_related_name'
    )
    def test_invalid_value_raises_error(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "'invalid_related_name' isn't a valid relationship name for "
            "accessing menu items from MainMenu."
        )):
            self.test_menu.get_menu_items_manager()
