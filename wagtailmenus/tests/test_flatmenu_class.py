from django.test import TestCase, override_settings

from wagtailmenus.models import FlatMenu
from wagtailmenus.tests import utils

Page = utils.get_page_model()
Site = utils.get_site_model()


class FlatMenuTestCase(TestCase):
    """A base TestCase class for testing FlatMenu model class methods"""

    def setUp(self):
        self.site = Site.objects.get()
        self.menus = (
            FlatMenu.objects.create(
                site=self.site, handle='test-1', title="Test Menu 1"
            ),
            FlatMenu.objects.create(
                site=self.site, handle='test-2', title="Test Menu 2"
            ),
            FlatMenu.objects.create(
                site=self.site, handle='test-3', title="Test Menu 3"
            )
        )
        for menu in self.menus:
            menu._option_vals = utils.make_optionvals_instance()


class TestGetSubMenuTemplateNames(FlatMenuTestCase):

    # ------------------------------------------------------------------------
    # FlatMenu.get_sub_menu_template_names()
    # ------------------------------------------------------------------------

    expected_default_result_length = 9

    def test_site_specific_templates_not_returned_by_default(self):
        menu = self.menus[0]
        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=self.site
        )
        result = menu.get_sub_menu_template_names()
        self.assertEqual(len(result), self.expected_default_result_length)
        for val in result:
            self.assertFalse(self.site.hostname in val)

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True)
    def test_site_specific_templates_returned_if_setting_is_true_and_current_site_is_in_contextual_vals(self):
        menu = self.menus[0]
        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=self.site
        )
        result = menu.get_sub_menu_template_names()
        self.assertGreater(len(result), self.expected_default_result_length)
        for val in result[:2]:
            self.assertTrue(self.site.hostname in val)

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True)
    def test_site_specific_templates_not_returned_if_current_site_not_in_contextual_vals(self):
        menu = self.menus[0]
        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=None
        )
        result = menu.get_sub_menu_template_names()
        self.assertEqual(len(result), self.expected_default_result_length)
        for val in result:
            self.assertTrue(self.site.hostname not in val)


class TestGetTemplateNamesMethod(FlatMenuTestCase):

    # ------------------------------------------------------------------------
    # FlatMenu.get_template_names()
    # ------------------------------------------------------------------------

    expected_default_result_length = 10

    def test_site_specific_templates_not_returned_by_default(self):
        menu = self.menus[0]
        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=self.site
        )
        result = menu.get_template_names()
        self.assertEqual(len(result), self.expected_default_result_length)
        for val in result:
            self.assertFalse(self.site.hostname in val)

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True)
    def test_site_specific_templates_returned_if_setting_is_true_and_current_site_is_in_contextual_vals(self):
        menu = self.menus[0]
        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=self.site
        )
        result = menu.get_template_names()
        self.assertGreater(len(result), self.expected_default_result_length)
        for val in result[:2]:
            self.assertTrue(self.site.hostname in val)

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True)
    def test_site_specific_templates_not_returned_if_current_site_not_in_contextual_vals(self):
        menu = self.menus[0]
        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=None
        )
        result = menu.get_template_names()
        self.assertEqual(len(result), self.expected_default_result_length)
        for val in result:
            self.assertTrue(self.site.hostname not in val)
