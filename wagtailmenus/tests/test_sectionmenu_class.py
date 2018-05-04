from django.test import TestCase

from wagtailmenus.models import SectionMenu
from wagtailmenus.tests import base, utils

Page = utils.get_page_model()


class SectionMenuTestCase(TestCase):

    def get_test_menu_instance(self):
        return SectionMenu(root_page=Page(), max_levels=3, use_specific=1)


class TestInitRequiredVals(SectionMenuTestCase):

    def test_init_raises_typeerror_if_use_specific_not_supplied(self):
        with self.assertRaises(TypeError):
            SectionMenu(Page(), 1)


class TestGetSubMenuTemplateNames(
    SectionMenuTestCase, base.GetSubMenuTemplateNamesMethodTestCase
):
    """
    Tests SectionMenu.get_sub_menu_template_names() using common test cases
    from base.GetTemplateNamesMethodTestCase
    """
    expected_default_result_length = 4


class TestGetTemplateNames(
    SectionMenuTestCase, base.GetTemplateNamesMethodTestCase
):
    """
    Tests SectionMenu.get_template_names() using common test cases from
    base.GetTemplateNamesMethodTestCase
    """
    expected_default_result_length = 3
