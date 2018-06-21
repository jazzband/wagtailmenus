from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from wagtailmenus.conf import settings
from wagtailmenus import models as default_models
from wagtailmenus.tests import models as test_models


class TestChildrenMenuClassOverriding(TestCase):
    """
    Tests the effect of overriding ``WAGTAILMENUS_CHILDREN_MENU_CLASS``
    """

    def test_default_value(self):
        self.assertEqual(
            settings.get_object('CHILDREN_MENU_CLASS'),
            default_models.ChildrenMenu
        )

    @override_settings(WAGTAILMENUS_CHILDREN_MENU_CLASS='wagtailmenus.tests.models.CustomChildrenMenu')
    def test_successful_override(self):
        self.assertEqual(
            settings.get_object('CHILDREN_MENU_CLASS'),
            test_models.CustomChildrenMenu
        )

    @override_settings(WAGTAILMENUS_CHILDREN_MENU_CLASS='CustomChildrenMenu')
    def test_invalid_path_raises_error(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "'CustomChildrenMenu' is not a valid import path. "
            "WAGTAILMENUS_CHILDREN_MENU_CLASS must be a full dotted "
            "python import path e.g. 'project.app.module.Class'"
        )):
            settings.get_object('CHILDREN_MENU_CLASS')


class TestSectionMenuClassOverriding(TestCase):
    """
    Tests the effect of overriding ``WAGTAILMENUS_SECTION_MENU_CLASS``
    """

    def test_default_value(self):
        self.assertEqual(
            settings.get_object('SECTION_MENU_CLASS'),
            default_models.SectionMenu
        )

    @override_settings(WAGTAILMENUS_SECTION_MENU_CLASS='wagtailmenus.tests.models.CustomSectionMenu')
    def test_successful_override(self):
        self.assertEqual(
            settings.get_object('SECTION_MENU_CLASS'),
            test_models.CustomSectionMenu
        )

    @override_settings(WAGTAILMENUS_SECTION_MENU_CLASS='CustomSectionMenu')
    def test_invalid_path_raises_error(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "'CustomSectionMenu' is not a valid import path. "
            "WAGTAILMENUS_SECTION_MENU_CLASS must be a full dotted "
            "python import path e.g. 'project.app.module.Class'"
        )):
            settings.get_object('SECTION_MENU_CLASS')
