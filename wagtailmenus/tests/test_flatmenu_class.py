from django.test import TestCase, override_settings

from wagtailmenus.models import FlatMenu
from wagtailmenus.tests import utils

Page = utils.get_page_model()
Site = utils.get_site_model()

TEMPLATE_LIST_DEFAULT = ('default_1.html', 'default_2.html')
TEMPLATE_LIST_TEST_1 = ('test-1a.html', 'test-1b.html')
TEMPLATE_LIST_TEST_2 = ('test-2a.html', 'test-2b.html')
TEMPLATE_LISTS_DICT_WITHOUT_DEFAULT = {
    'test-1': TEMPLATE_LIST_TEST_1,
    'test-2': TEMPLATE_LIST_TEST_2,
}
TEMPLATE_LISTS_DICT_WITH_DEFAULT = dict(TEMPLATE_LISTS_DICT_WITHOUT_DEFAULT)
TEMPLATE_LISTS_DICT_WITH_DEFAULT['default'] = TEMPLATE_LIST_DEFAULT


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


class TestGetSubMenuTemplateNamesFromSetting(FlatMenuTestCase):

    # ------------------------------------------------------------------------
    # FlatMenu.get_sub_menu_template_names_from_setting()
    # ------------------------------------------------------------------------

    def test_none_returned_if_setting_not_set(self):
        for menu in self.menus:
            self.assertEqual(
                menu.get_sub_menu_template_names_from_setting(), None
            )

    @override_settings(
        WAGTAILMENUS_DEFAULT_FLAT_MENU_SUB_MENU_TEMPLATES=TEMPLATE_LIST_DEFAULT
    )
    def test_same_list_returned_when_the_setting_value_is_as_single_list(self):
        for menu in self.menus:
            self.assertEqual(
                menu.get_sub_menu_template_names_from_setting(), TEMPLATE_LIST_DEFAULT
            )

    @override_settings(
        WAGTAILMENUS_DEFAULT_FLAT_MENU_SUB_MENU_TEMPLATES=TEMPLATE_LISTS_DICT_WITH_DEFAULT
    )
    def test_handle_specific_list_returned_when_menu_handle_key_is_present(self):
        menu = self.menus[0]
        self.assertIn(menu.handle, TEMPLATE_LISTS_DICT_WITH_DEFAULT.keys())
        self.assertEqual(menu.get_sub_menu_template_names_from_setting(), TEMPLATE_LIST_TEST_1)

        menu = self.menus[1]
        self.assertIn(menu.handle, TEMPLATE_LISTS_DICT_WITH_DEFAULT.keys())
        self.assertEqual(menu.get_sub_menu_template_names_from_setting(), TEMPLATE_LIST_TEST_2)

    @override_settings(
        WAGTAILMENUS_DEFAULT_FLAT_MENU_SUB_MENU_TEMPLATES=TEMPLATE_LISTS_DICT_WITH_DEFAULT
    )
    def test_default_list_returned_if_menu_handle_key_not_present(self):
        menu = self.menus[2]
        self.assertNotIn(menu.handle, TEMPLATE_LISTS_DICT_WITH_DEFAULT)
        self.assertEqual(TEMPLATE_LISTS_DICT_WITH_DEFAULT['default'], TEMPLATE_LIST_DEFAULT)
        self.assertEqual(menu.get_sub_menu_template_names_from_setting(), TEMPLATE_LIST_DEFAULT)

    @override_settings(
        WAGTAILMENUS_DEFAULT_FLAT_MENU_SUB_MENU_TEMPLATES=TEMPLATE_LISTS_DICT_WITHOUT_DEFAULT
    )
    def test_none_returned_if_neither_menu_handle_or_default_keys_are_present(self):
        menu = self.menus[2]
        self.assertNotIn(menu.handle, TEMPLATE_LISTS_DICT_WITHOUT_DEFAULT)
        self.assertNotIn('default', TEMPLATE_LISTS_DICT_WITHOUT_DEFAULT)
        self.assertEqual(menu.get_sub_menu_template_names_from_setting(), None)


class TestGetSubMenuTemplateNames(FlatMenuTestCase):

    # ------------------------------------------------------------------------
    # FlatMenu.get_sub_menu_template_names()
    # ------------------------------------------------------------------------

    def test_site_specific_templates_not_returned_by_default(self):
        menu = self.menus[0]
        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=self.site
        )
        result = menu.get_sub_menu_template_names()
        self.assertEqual(len(result), 11)
        for val in result:
            self.assertFalse(self.site.hostname in val)

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True)
    def test_site_specific_templates_returned_if_setting_is_true_and_current_site_is_in_contextual_vals(self):
        menu = self.menus[0]
        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=self.site
        )
        result = menu.get_sub_menu_template_names()
        self.assertEqual(len(result), 22)
        for val in result[:8]:
            self.assertTrue(self.site.hostname in val)

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True)
    def test_site_specific_templates_not_returned_if_current_site_not_in_contextual_vals(self):
        menu = self.menus[0]
        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=None
        )
        result = menu.get_sub_menu_template_names()
        self.assertEqual(len(result), 11)
        for val in result:
            self.assertTrue(self.site.hostname not in val)


class TestGetTemplateNamesMethod(FlatMenuTestCase):

    # ------------------------------------------------------------------------
    # FlatMenu.get_template_names()
    # ------------------------------------------------------------------------

    def test_site_specific_templates_not_returned_by_default(self):
        menu = self.menus[0]
        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=self.site
        )
        result = menu.get_template_names()
        self.assertEqual(len(result), 11)
        for val in result:
            self.assertFalse(self.site.hostname in val)

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True)
    def test_site_specific_templates_returned_if_setting_is_true_and_current_site_is_in_contextual_vals(self):
        menu = self.menus[0]
        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=self.site
        )
        result = menu.get_template_names()
        self.assertEqual(len(result), 22)
        for val in result[:7]:
            self.assertTrue(self.site.hostname in val)

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True)
    def test_site_specific_templates_not_returned_if_current_site_not_in_contextual_vals(self):
        menu = self.menus[0]
        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=None
        )
        result = menu.get_template_names()
        self.assertEqual(len(result), 11)
        for val in result:
            self.assertTrue(self.site.hostname not in val)
