from django.test import TestCase

from wagtailmenus.models import FlatMenu
from wagtailmenus.tests import base, utils

Page = utils.get_page_model()
Site = utils.get_site_model()


class FlatMenuTestCase(TestCase):
    """A base TestCase class for testing FlatMenu model class methods"""

    @staticmethod
    def create_test_menus_for_site(site, count=3, set_option_vals=False):
        for i in range(1, count + 1):
            obj = FlatMenu.objects.create(
                site=site, handle='test-%s' % i, title='Test Menu %s' % i
            )
            if set_option_vals:
                obj._option_vals = utils.make_optionvals_instance()
            yield obj

    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.menus = tuple(
            self.create_test_menus_for_site(self.site, set_option_vals=True)
        )

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
