import warnings
from unittest import mock
from django.test import TestCase

from wagtailmenus.conf import constants
from wagtailmenus.models import MainMenu, MainMenuItem
from wagtailmenus.tests import base, utils

Page = utils.get_page_model()


class MainMenuTestCase(TestCase):
    """A base TestCase class for testing MainMenu model class methods"""

    fixtures = ['test.json']

    def get_random_menu_instance_with_opt_vals_set(self):
        obj = MainMenu.objects.order_by('?').first()
        obj._option_vals = utils.make_optionvals_instance()
        return obj

    def get_test_menu_instance(self):
        return MainMenu.objects.first()


class TestMainMenuGeneralMethods(MainMenuTestCase):

    def test_create_from_collected_values_is_not_implemented(self):
        # Model-based menus use get_from_collected_values() instead of
        # create_from_collected_values(), because existing objects are reused,
        # rather than recreated each time
        menu = self.get_test_menu_instance()
        with self.assertRaises(NotImplementedError):
            menu.create_from_collected_values(None, None)


class TestTopLevelItems(MainMenuTestCase):

    # ------------------------------------------------------------------------
    # MainMenu.top_level_items()
    # ------------------------------------------------------------------------

    def test_setting_and_clearing_of_cache_values(self):
        menu = MainMenu.objects.get(pk=1)
        # This menu has a `use_specific` value of 1 (AUTO)
        self.assertEqual(menu.use_specific, 1)

        # So, the top-level items it returns should all just be custom links
        # or have a `link_page` that is just a vanilla Page object.
        for item in menu.top_level_items:
            self.assertTrue(item.link_page is None or type(item.link_page) is Page)

        # After being called once, top_level_options should be cached, so
        # accessing it again shouldn't trigger any database queries
        with self.assertNumQueries(0):
            for item in menu.top_level_items:
                self.assertTrue(item.link_page or item.link_url)

        # Lets change `use_specific` to 2 (TOP_LEVEL)
        menu.set_use_specific(2)

        # The above should clear the cached value, so if we call
        # top_level_items again, we should get a fresh list of specific pages
        for item in menu.top_level_items:
            self.assertTrue(item.link_page is None or type(item.link_page) is not Page)

        # Lets change `use_specific` to 0 (OFF) again
        menu.set_use_specific(0)

        # Because the work has already been done to fetch specific items, even
        # though we might not need specific items, the cached value should
        # remain in-tact, with no more queries being triggered on recall.
        with self.assertNumQueries(0):
            for item in menu.top_level_items:
                assert item.link_page is None or type(item.link_page) is not Page

    def test_method_initiates_one_query_when_no_menu_items_link_to_pages(self):
        # First, let's replace any menu items that link to pages with links
        # to custom urls
        for i, item in enumerate(
            MainMenu.objects.get(pk=1).get_menu_items_manager().all()
        ):
            if item.link_page_id:
                item.link_page = None
                item.link_url = '/test/{}/'.format(i)
                item.save()

        menu = MainMenu.objects.get(pk=1)
        with self.assertNumQueries(1):
            menu.get_top_level_items()

    def test_method_initiates_two_queries_when_vanilla_page_data_is_required(self, menu_obj=None):
        menu = menu_obj or MainMenu.objects.get(pk=1)
        menu.use_specific = constants.USE_SPECIFIC_AUTO
        with self.assertNumQueries(2):
            menu.get_top_level_items()


class TestPagesForDisplay(MainMenuTestCase):

    # ------------------------------------------------------------------------
    # MainMenu.pages_for_display()
    # ------------------------------------------------------------------------

    def test_setting_and_clearing_of_cache_values(self):
        menu = MainMenu.objects.get(pk=1)
        # This menu has a `use_specific` value of 1 (AUTO)
        self.assertEqual(menu.use_specific, 1)
        # And a `max_levels` value of 2
        self.assertEqual(menu.max_levels, 2)

        # So, every page returned by `pages_for_display` should just be a
        # vanilla Page object, that is live, not expired and meant to
        # appear in menus
        for p in menu.pages_for_display:
            self.assertEqual(type(p), Page)
            self.assertTrue(p.live)
            self.assertFalse(p.expired)
            self.assertTrue(p.show_in_menus)

        # Their should be 6 pages total
        self.assertEqual(len(menu.pages_for_display), 6)

        # After being called once, pages_for_display should be cached, so
        # accessing it again shouldn't trigger any database queries
        with self.assertNumQueries(0):
            for p in menu.pages_for_display:
                self.assertTrue(p.title)

        # Lets change `use_specific` to 3 (ALWAYS)
        menu.set_use_specific(3)

        # The above should clear the cached value, so if we call
        # pages_for_display again, we should get a fresh list of specific pages
        for p in menu.pages_for_display:
            self.assertNotEqual(type(p), Page)

        # Lets change `max_levels` to 1
        menu.set_max_levels(1)

        # The above should clear the cached value, so if we call
        # pages_for_display again, we it should provide an empty queryset
        self.assertQuerysetEqual(menu.pages_for_display, Page.objects.none())

        # Lets change `max_levels` to 3
        menu.set_max_levels(3)

        # The above should cleare the cached value, and now pages_for_display
        # should reurn 12 pages total to display
        self.assertEqual(len(menu.pages_for_display), 9)

        # As with `top_level_items` Even is we set `use_specific` to a lower
        # value, the cached `pages_for_display` value will not be cleared, as
        # it specific is better than not.
        menu.set_use_specific(1)

        # Because the work has already been done to fetch specific pages, even
        # though we might not need specific items, the cached value should
        # remain in-tact, with no more queries being triggered on recall.
        with self.assertNumQueries(0):
            for p in menu.pages_for_display:
                assert type(p) is not Page


class TestAddMenuItemsForPages(MainMenuTestCase):

    # ------------------------------------------------------------------------
    # MainMenu.add_menu_items_for_pages()
    # ------------------------------------------------------------------------

    def test_add_menu_items_for_pages(self):
        menu = MainMenu.objects.get(pk=1)
        # The current number of menu items is 6
        self.assertEqual(menu.get_menu_items_manager().count(), 6)

        # 'Superheroes' has 2 children: 'D.C. Comics' & 'Marvel Comics'
        superheroes_page = Page.objects.get(title="Superheroes")
        children_of_superheroes = superheroes_page.get_children()
        self.assertEqual(children_of_superheroes.count(), 2)

        # Use 'add_menu_items_for_pages' to add pages for the above pages
        menu.add_menu_items_for_pages(children_of_superheroes)

        # The number of menu items should now be 8
        self.assertEqual(menu.get_menu_items_manager().count(), 8)

        # Evaluate menu items to a list
        menu_items = list(menu.get_menu_items_manager().all())

        # The last item should be a link to the 'D.C. Comics' page, and the
        # sort_order on the item should be 7
        dc_item = menu_items.pop()
        self.assertEqual(dc_item.link_page.title, 'D.C. Comics')
        self.assertEqual(dc_item.sort_order, 7)

        # The '2nd to last' item should be a link to the 'Marvel Comics' page,
        # and the sort_order on the item should be 6
        marvel_item = menu_items.pop()
        self.assertEqual(marvel_item.link_page.title, 'Marvel Comics')
        self.assertEqual(marvel_item.sort_order, 6)


class TestGetSpecifiedSubMenuTemplateName(MainMenuTestCase):

    # ------------------------------------------------------------------------
    # MainMenu._get_specified_sub_menu_template_name()
    # (inherited from mixins.DefinesSubMenuTemplatesMixin)
    # ------------------------------------------------------------------------

    def test_returns_none_if_no_templates_specified(self):
        menu = self.get_random_menu_instance_with_opt_vals_set()
        self.assertEqual(
            menu._get_specified_sub_menu_template_name(level=2), None
        )
        self.assertEqual(
            menu._get_specified_sub_menu_template_name(level=3), None
        )
        self.assertEqual(
            menu._get_specified_sub_menu_template_name(level=4), None
        )

    def test_returns_last_template_when_no_template_specified_for_level(self):
        menu = MainMenu.objects.all().first()
        menu._option_vals = utils.make_optionvals_instance(
            sub_menu_template_names=('single_template.html',)
        )
        self.assertEqual(
            menu._get_specified_sub_menu_template_name(level=2),
            'single_template.html'
        )
        self.assertEqual(
            menu._get_specified_sub_menu_template_name(level=3),
            'single_template.html'
        )

    def test_preference_order_of_specified_values(self):
        menu = MainMenu.objects.all().first()
        menu._option_vals = utils.make_optionvals_instance(
            sub_menu_template_name='single_template_as_option.html',
            sub_menu_template_names=('option_one.html', 'option_two.html')
        )
        menu.sub_menu_template_name = 'single_template_as_attr.html'
        menu.sub_menu_template_names = utils.SUB_MENU_TEMPLATE_LIST

        # While both 'sub_menu_template_name' and 'sub_menu_template_names' are
        # specified as option values, the 'sub_menu_template_name' value will
        # be preferred
        self.assertEqual(
            menu._get_specified_sub_menu_template_name(level=4),
            'single_template_as_option.html'
        )

        # If only 'sub_menu_template_names' is specified as an option value,
        # that will be preferred
        menu._option_vals = utils.make_optionvals_instance(
            sub_menu_template_name=None,
            sub_menu_template_names=('option_one.html', 'option_two.html')
        )
        self.assertEqual(
            menu._get_specified_sub_menu_template_name(level=4),
            'option_two.html',
        )

        # If no templates have been specified via options, the
        # 'sub_menu_template_name' attribute is preferred
        menu._option_vals = utils.make_optionvals_instance(
            sub_menu_template_name=None,
            sub_menu_template_names=None
        )
        self.assertEqual(
            menu._get_specified_sub_menu_template_name(level=4),
            'single_template_as_attr.html'
        )

        # If the 'sub_menu_template_name' attribute is None, the method
        # should prefer the 'sub_menu_template_names' attribute
        menu.sub_menu_template_name = None
        self.assertEqual(
            menu._get_specified_sub_menu_template_name(level=4),
            menu.sub_menu_template_names[1]
        )


class TestGetSubMenuTemplateNames(
    MainMenuTestCase, base.GetSubMenuTemplateNamesMethodTestCase
):
    """
    Tests MainMenu.get_sub_menu_template_names() using common test cases
    from base.GetTemplateNamesMethodTestCase
    """
    expected_default_result_length = 4


class TestGetTemplateNames(
    MainMenuTestCase, base.GetTemplateNamesMethodTestCase
):
    """
    Tests MainMenu.get_template_names() using common test cases from
    base.GetTemplateNamesMethodTestCase
    """
    expected_default_result_length = 3


def mock_relative_url_method(self, site=None):
    return ''


class TestMenuItemDeprecationWarning(MainMenuTestCase):

    @mock.patch.object(MainMenuItem, 'relative_url', mock_relative_url_method)
    def test_warns_when_custom_menuitem_relative_url_does_not_accept_request(self):
        menu = self.get_test_menu_instance()
        menu._option_vals = utils.make_optionvals_instance()
        menu._contextual_vals = utils.make_contextualvals_instance(url='/test')
        menu.request = menu._contextual_vals.request

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            menu.get_menu_items_for_rendering()
        self.assertEqual(
            str(w[0].message),
            "The relative_url() method on custom MenuItem classes must accept "
            "a 'request' keyword argument. Please update the method signature "
            "on your MainMenuItem class. It will be mandatory in Wagtail 2.13."
        )
