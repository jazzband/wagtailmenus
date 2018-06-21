import warnings

from django.test import TestCase, override_settings
from wagtailmenus.conf import settings


class TestDeprecationWarningsRaised(TestCase):

    @override_settings(WAGTAILMENUS_CHILDREN_MENU_CLASS_PATH='wagtailmenus.tests.models.CustomChildrenMenu')
    def test_warns_when_children_menu_specified_with_deprecated_setting_name(self):
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

    @override_settings(WAGTAILMENUS_CHILDREN_MENU_CLASS_PATH='wagtailmenus.tests.models.CustomChildrenMenu')
    def test_warns_when_deprecated_children_menu_setting_referenced(self):
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

    @override_settings(WAGTAILMENUS_SECTION_MENU_CLASS_PATH='wagtailmenus.tests.models.CustomSectionMenu')
    def test_warns_when_section_menu_specified_with_deprecated_setting_name(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(
                settings.SECTION_MENU_CLASS,
                'wagtailmenus.tests.models.CustomSectionMenu'
            )
        self.assertIn(
            "The WAGTAILMENUS_SECTION_MENU_CLASS_PATH setting is "
            "deprecated in favour of using WAGTAILMENUS_SECTION_MENU_CLASS",
            str(w[0].message)
        )

    @override_settings(WAGTAILMENUS_SECTION_MENU_CLASS_PATH='wagtailmenus.tests.models.CustomSectionMenu')
    def test_warns_when_deprecated_section_menu_setting_referenced(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(
                settings.SECTION_MENU_CLASS_PATH,
                'wagtailmenus.tests.models.CustomSectionMenu'
            )
        self.assertIn(
            "SECTION_MENU_CLASS_PATH is deprecated in favour of using "
            "SECTION_MENU_CLASS in app settings",
            str(w[0].message)
        )
