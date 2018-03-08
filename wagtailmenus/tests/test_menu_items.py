from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from wagtailmenus.models import AbstractMenuItem
from wagtailmenus import app_settings


class TestMenuItemsForRequest(TestCase):
    """
    Tests active classes rendered for menu items where
    `WAGTAILMENUS_CUSTOM_URL_SMART_ACTIVE_CLASSES == False`
    """

    def setUp(self):
        self.rf = RequestFactory()

    def test_menu_item_exact_match(self):
        menu_item = AbstractMenuItem()
        menu_item.link_url = '/some-page/'
        request = self.rf.get('/some-page/')

        active_class = menu_item.get_active_class_for_request(request)
        self.assertEqual(active_class, app_settings.ACTIVE_CLASS)

    def test_menu_item_with_query_params(self):
        menu_item = AbstractMenuItem()
        menu_item.link_url = '/some-page/?some_param=foo'
        request = self.rf.get('/some-page/')

        active_class = menu_item.get_active_class_for_request(request)
        self.assertEqual(active_class, '')


@override_settings(WAGTAILMENUS_CUSTOM_URL_SMART_ACTIVE_CLASSES=True)
class TestMenuItemsForRequestWithSmartClasses(TestCase):

    def setUp(self):
        self.rf = RequestFactory()

    def test_menu_item_with_query_params(self):
        menu_item = AbstractMenuItem()
        menu_item.link_url = '/some-page/?some_param=foo'
        request = self.rf.get('/some-page/?some_other_param=foo')

        active_class = menu_item.get_active_class_for_request(request)
        self.assertEqual(active_class, app_settings.ACTIVE_CLASS)

    def test_menu_item_with_hash_fragment(self):
        menu_item = AbstractMenuItem()
        menu_item.link_url = '/some-page/#some_fragment'
        request = self.rf.get('/some-page/#some_other_hash_fragment')

        active_class = menu_item.get_active_class_for_request(request)
        self.assertEqual(active_class, app_settings.ACTIVE_CLASS)

    def test_menu_item_ancestor(self):
        menu_item = AbstractMenuItem()
        menu_item.link_url = '/some-page/'
        request = self.rf.get('/some-page/some-child-page')

        active_class = menu_item.get_active_class_for_request(request)
        self.assertEqual(active_class, app_settings.ACTIVE_ANCESTOR_CLASS)

    def test_menu_item_with_netloc(self):
        menu_item = AbstractMenuItem()
        menu_item.link_url = 'https://example.com/some-page'
        request = self.rf.get('/some-page/')

        active_class = menu_item.get_active_class_for_request(request)
        self.assertEqual(active_class, '')
