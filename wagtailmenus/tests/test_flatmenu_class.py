from django.test import TestCase

from wagtailmenus.models import FlatMenu
from wagtailmenus.tests import base, utils

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

    def get_test_menu_instance(self):
        return self.menus[0]


class TestGetSubMenuTemplateNames(
    FlatMenuTestCase, base.GetSubMenuTemplateNamesMethodTestCase
):
    """
    Tests FlatMenu.get_sub_menu_template_names() using common test cases
    from base.GetTemplateNamesMethodTestCase
    """
    expected_default_result_length = 9


class TestGetTemplateNames(
    FlatMenuTestCase, base.GetTemplateNamesMethodTestCase
):
    """
    Tests FlatMenu.get_template_names() using common test cases from
    base.GetTemplateNamesMethodTestCase
    """
    expected_default_result_length = 10
