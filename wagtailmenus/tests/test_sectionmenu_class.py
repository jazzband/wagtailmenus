from django.test import TestCase, override_settings

from wagtailmenus.models import SectionMenu
from wagtailmenus.tests import utils

Page = utils.get_page_model()


class TestSectionMenuClass(TestCase):

    def test_init_raises_typeerror_if_use_specific_not_supplied(self):
        with self.assertRaises(TypeError):
            SectionMenu(Page(), 1)

    def test_get_sub_menu_template_names_from_setting_returns_none_if_setting_not_set(self):
        self.assertEqual(
            SectionMenu.get_sub_menu_template_names_from_setting(), None
        )

    @override_settings(
        WAGTAILMENUS_DEFAULT_SECTION_MENU_SUB_MENU_TEMPLATES=utils.SUB_MENU_TEMPLATE_LIST
    )
    def test_get_sub_menu_template_names_from_setting_returns_setting_value_when_set(self):
        self.assertEqual(
            SectionMenu.get_sub_menu_template_names_from_setting(),
            utils.SUB_MENU_TEMPLATE_LIST
        )
