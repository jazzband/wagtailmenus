from django.test import TestCase

from wagtailmenus.models import ChildrenMenu
from wagtailmenus.tests import base, utils

Page = utils.get_page_model()


class ChildrenMenuTestCase(TestCase):

    def get_test_menu_instance(self):
        return ChildrenMenu(parent_page=Page(), max_levels=3)


class TestGetSubMenuTemplateNames(
    ChildrenMenuTestCase, base.GetSubMenuTemplateNamesMethodTestCase
):
    """
    Tests ChildrenMenu.get_sub_menu_template_names() using common test cases
    from base.GetTemplateNamesMethodTestCase
    """
    expected_default_result_length = 4


class TestGetTemplateNames(
    ChildrenMenuTestCase, base.GetTemplateNamesMethodTestCase
):
    """
    Tests ChildrenMenu.get_template_names() using common test cases from
    base.GetTemplateNamesMethodTestCase
    """
    expected_default_result_length = 3
