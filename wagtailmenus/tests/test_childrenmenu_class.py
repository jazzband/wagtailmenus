from django.test import TestCase

from wagtailmenus.models import ChildrenMenu
from wagtailmenus.tests import base, utils

Page = utils.get_page_model()


class ChildrenMenuTestCase(TestCase):

    def get_test_menu_instance(self):
        return ChildrenMenu(parent_page=Page(), max_levels=3, use_specific=1)


class TestInitRequiredVals(ChildrenMenuTestCase):

    def test_init_raises_typeerror_if_max_levels_not_supplied(self):
        msg_extract = "'max_levels' must be provided when creating"
        with self.assertRaisesRegex(TypeError, msg_extract):
            ChildrenMenu(Page(), use_specific=1)

    def test_init_raises_typeerror_if_use_specific_not_supplied(self):
        msg_extract = "'use_specific' must be provided when creating"
        with self.assertRaisesRegex(TypeError, msg_extract):
            ChildrenMenu(Page(), max_levels=1)


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
