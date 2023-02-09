from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.client import RequestFactory
from wagtail.models import Page

from wagtailmenus.conf import settings
from wagtailmenus.models import FlatMenu, FlatMenuItem, MainMenu, MainMenuItem


class MenuItemModelTestMixin:
    """
    Defines a generic set of tests to be run against either MainMenuItem or
    FlatMenuItem model classes
    """
    fixtures = ['test.json']
    menu_model = None
    menu_item_model = None

    def setUp(self):
        self.menu = self.menu_model.objects.all().first()
        self.page = Page.objects.all().first()

    def test_meta_class(self):
        opts = self.menu_item_model._meta
        self.assertEqual(opts.verbose_name, 'menu item')
        self.assertEqual(opts.verbose_name_plural, 'menu items')
        self.assertEqual(opts.ordering, ('sort_order',))

    def test_menu_text_returns_link_text_value_over_page_title(self):
        link_text = "i want to be menu text"
        obj = self.menu_item_model(
            menu=self.menu,
            link_page=self.page,
            link_text=link_text
        )
        self.assertNotEqual(self.page.title, link_text)
        self.assertEqual(obj.menu_text, link_text)

    def test_menu_text_returns_page_title_if_no_link_text_is_set(self):
        obj = self.menu_item_model(menu=self.menu, link_page=self.page)
        self.assertEqual(obj.menu_text, self.page.title)

    def test_menu_text_returns_blank_string_if_neither_link_text_or_link_page_are_set(self):
        obj = self.menu_item_model(menu=self.menu)
        self.assertEqual(obj.menu_text, '')

    def test_str_returns_same_value_as_menu_text(self):
        for obj in self.menu_item_model.objects.all():
            self.assertEqual(str(obj), obj.menu_text)

    def test_clean_errors_when_link_url_is_set_without_link_text(self):
        obj = self.menu_item_model(menu=self.menu, link_url='test/')
        self.assertRaisesMessage(
            ValidationError,
            "This field is required when linking to a custom URL",
            obj.clean)

    def test_clean_errors_when_both_link_url_and_link_page_are_set(self):
        obj = self.menu_item_model(
            menu=self.menu,
            link_url='test/',
            link_page=self.page
        )
        self.assertRaisesMessage(
            ValidationError,
            "Linking to both a page and custom URL is not permitted",
            obj.clean
        )

    def test_clean_errors_when_nethier_link_url_or_link_page_are_set(self):
        obj = self.menu_item_model(
            menu=self.menu,
            link_text='Test',
        )
        self.assertRaisesMessage(
            ValidationError,
            "Please choose an internal page or provide a custom URL",
            obj.clean
        )


class TestMainMenuItemGeneralMethods(MenuItemModelTestMixin, TestCase):
    """
    Runs the tests from MenuItemModelTestMixin for the MainMenuItem model
    """
    menu_model = MainMenu
    menu_item_model = MainMenuItem


class TestFlatMenuItemGeneralMethods(MenuItemModelTestMixin, TestCase):
    """
    Runs the tests from MenuItemModelTestMixin for the FlatMenuItem model
    """
    menu_model = FlatMenu
    menu_item_model = FlatMenuItem


class TestMenuItemsForRequest(TestCase):
    """
    Tests active classes rendered for menu items
    """
    def setUp(self):
        self.rf = RequestFactory()

    def test_menu_item_exact_match(self):
        menu_item = MainMenuItem()
        menu_item.link_url = '/some-page/'
        request = self.rf.get('/some-page/')

        active_class = menu_item.get_active_class_for_request(request)
        self.assertEqual(active_class, settings.ACTIVE_CLASS)

    def test_menu_item_with_query_params(self):
        menu_item = MainMenuItem()
        menu_item.link_url = '/some-page/?some_param=foo'
        request = self.rf.get('/some-page/?some_other_param=foo')

        active_class = menu_item.get_active_class_for_request(request)
        self.assertEqual(active_class, settings.ACTIVE_CLASS)

    def test_menu_item_with_hash_fragment(self):
        menu_item = MainMenuItem()
        menu_item.link_url = '/some-page/#some_fragment'
        request = self.rf.get('/some-page/#some_other_hash_fragment')

        active_class = menu_item.get_active_class_for_request(request)
        self.assertEqual(active_class, settings.ACTIVE_CLASS)

    def test_menu_item_ancestor(self):
        menu_item = MainMenuItem()
        menu_item.link_url = '/some-page/'
        request = self.rf.get('/some-page/some-child-page')

        active_class = menu_item.get_active_class_for_request(request)
        self.assertEqual(active_class, settings.ACTIVE_ANCESTOR_CLASS)

    def test_menu_item_with_netloc(self):
        menu_item = MainMenuItem()
        menu_item.link_url = 'https://example.com/some-page'
        request = self.rf.get('/some-page/')

        active_class = menu_item.get_active_class_for_request(request)
        self.assertEqual(active_class, '')
