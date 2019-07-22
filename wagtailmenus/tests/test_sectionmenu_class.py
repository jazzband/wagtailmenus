from django.test import TestCase

from wagtailmenus.models import SectionMenu
from wagtailmenus.tests import base, utils

Page = utils.get_page_model()


class SectionMenuTestCase(TestCase):

    def get_test_menu_instance(self):
        return SectionMenu(root_page=Page(), max_levels=3)


class TestSectionMenuGeneralMethods(SectionMenuTestCase):

    def test_get_from_collected_values_is_not_implemented(self):
        # Non model-based menus use create_from_collected_values() instead of
        # get_from_collected_values(), because there's no 'getting' involved.
        menu = self.get_test_menu_instance()
        with self.assertRaises(NotImplementedError):
            menu.get_from_collected_values(None, None)


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
