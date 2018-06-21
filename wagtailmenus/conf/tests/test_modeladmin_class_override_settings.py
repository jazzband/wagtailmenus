from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from wagtailmenus.conf import settings
from wagtailmenus.modeladmin import FlatMenuAdmin, MainMenuAdmin
from wagtailmenus.tests.modeladmin import \
    CustomFlatMenuModelAdmin, CustomMainMenuModelAdmin


class TestFlatMenuModelAdminOverriding(TestCase):
    """
    Tests the effect of overriding ``WAGTAILMENUS_FLAT_MENUS_MODELADMIN_CLASS``
    """

    def test_default_value(self):
        self.assertEqual(
            settings.get_object('FLAT_MENUS_MODELADMIN_CLASS'),
            FlatMenuAdmin
        )

    @override_settings(WAGTAILMENUS_FLAT_MENUS_MODELADMIN_CLASS='wagtailmenus.tests.modeladmin.CustomFlatMenuModelAdmin')
    def test_successful_override(self):
        self.assertEqual(
            settings.get_object('FLAT_MENUS_MODELADMIN_CLASS'),
            CustomFlatMenuModelAdmin
        )

    @override_settings(WAGTAILMENUS_FLAT_MENUS_MODELADMIN_CLASS='NonExistentClass')
    def test_invalid_path_raises_error(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "'NonExistentClass' is not a valid import path. "
            "WAGTAILMENUS_FLAT_MENUS_MODELADMIN_CLASS must be a full dotted "
            "python import path e.g. 'project.app.module.Class'"
        )):
            settings.get_object('FLAT_MENUS_MODELADMIN_CLASS')


class TestMainMenuModelAdminOverriding(TestCase):
    """
    Tests the effect of overriding ``WAGTAILMENUS_MAIN_MENUS_MODELADMIN_CLASS``
    """

    def test_default_value(self):
        self.assertEqual(
            settings.get_object('MAIN_MENUS_MODELADMIN_CLASS'),
            MainMenuAdmin
        )

    @override_settings(WAGTAILMENUS_MAIN_MENUS_MODELADMIN_CLASS='wagtailmenus.tests.modeladmin.CustomMainMenuModelAdmin')
    def test_successful_override(self):
        self.assertEqual(
            settings.get_object('MAIN_MENUS_MODELADMIN_CLASS'),
            CustomMainMenuModelAdmin
        )

    @override_settings(WAGTAILMENUS_MAIN_MENUS_MODELADMIN_CLASS='NonExistentClass')
    def test_invalid_path_raises_error(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "'NonExistentClass' is not a valid import path. "
            "WAGTAILMENUS_MAIN_MENUS_MODELADMIN_CLASS must be a full dotted "
            "python import path e.g. 'project.app.module.Class'"
        )):
            settings.get_object('MAIN_MENUS_MODELADMIN_CLASS')
