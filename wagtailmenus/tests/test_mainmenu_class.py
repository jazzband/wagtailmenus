from django.test import TestCase

from wagtailmenus.models import MainMenu
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
    # MainMenu.top_level_items
    # ------------------------------------------------------------------------

    def test_uses_many_queries_when_menu_items_link_to_pages(self):
        # 6 queries in total:
        # 1. Fetch menu items
        # 2. Fetch vanilla pages
        # 3-7: Fetch specific pages (HomePage, TopLevelPage, LowLevelPage, ArticleListPage, ContactPage)
        menu = self.get_test_menu_instance()
        with self.assertNumQueries(7):
            menu.top_level_items

    def test_uses_a_single_query_when_no_menu_items_link_to_pages(self):
        # Replace any menu items that link to pages with links
        # to custom urls
        menu = self.get_test_menu_instance()
        for i, item in enumerate(
            menu.get_menu_items_manager().all()
        ):
            if item.link_page_id:
                item.link_page = None
                item.link_url = '/test/{}/'.format(i)
                item.save()

        # If no menu items link to pages, no further queries are needed
        with self.assertNumQueries(1):
            menu.top_level_items


class TestGetPagesForDisplay(MainMenuTestCase):

    # ------------------------------------------------------------------------
    # MainMenu.pages_for_display
    # ------------------------------------------------------------------------

    def test_result(self):
        menu = MainMenu.objects.get(pk=1)
        # And a `max_levels` value of 2
        self.assertEqual(menu.max_levels, 2)

        # Every page returned by `pages_for_display` should be a
        # live, not expired and meant to appear in menus
        for p in menu.pages_for_display.values():
            self.assertTrue(p.live)
            self.assertFalse(p.expired)
            self.assertTrue(p.show_in_menus)

        # Their should be 12 pages total, 1 for each item, plus children:
        # 1.  <HomePage: Home>,
        # 2.  <TopLevelPage: About us>
        #     3.  <LowLevelPage: Meet the team>
        #     4.  <LowLevelPage: Our heritage>
        #     5.  <LowLevelPage: Our mission and values>
        # X.  <TopLevelPage: Superheroes> - not included (show_in_menus=False)
        #     6.  <LowLevelPage: Marvel Comics>
        #     7.  <LowLevelPage: D.C. Comics>
        # 8.  <TopLevelPage: News & events>
        #     9.  <LowLevelPage: Latest news>
        #     10. <LowLevelPage: Upcoming events>
        #     11. <LowLevelPage: In the press>
        # 12. <ContactPage: Contact us>
        self.assertEqual(len(menu.pages_for_display), 12)

        # After being called once, pages_for_display should be cached, so
        # accessing it again shouldn't trigger any database queries
        with self.assertNumQueries(0):
            list(menu.pages_for_display.values())


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
