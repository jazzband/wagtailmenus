from django.test import TestCase
from wagtailmenus.errors import RequestUnavailableError
from wagtailmenus.models import Menu, MenuWithMenuItems
try:
    from wagtail.models import Page, Site
except ImportError:
    from wagtail.core.models import Page, Site


class TestMenuGetSite(TestCase):

    def setUp(self):
        super().setUp()
        self.site = Site.objects.get()

    def test_returns_site_from_context(self):
        result = Menu._get_site({'site': self.site})
        self.assertIs(result, self.site)

    def test_returns_site_from_request(self):
        class FakeRequest:
            site = self.site
            _wagtail_site = self.site

        result = Menu._get_site({'request': FakeRequest})
        self.assertIs(result, self.site)

    def test_returns_none_if_request_and_site_not_present(self):
        result = Menu._get_site({})
        self.assertIs(result, None)


class TestMenuWithMenuItemsGetSite(TestCase):

    def setUp(self):
        super().setUp()
        self.site = Site.objects.get()
        self.other_site = Site.objects.create(hostname='other.com', port=80, root_page=Page.objects.first())

    def test_returns_site_from_context(self):
        result = MenuWithMenuItems._get_site({'site': self.site})
        self.assertIs(result, self.site)

    def test_returns_site_from_request(self):
        class FakeRequest:
            site = self.site
            _wagtail_site = self.site

        result = MenuWithMenuItems._get_site({'request': FakeRequest})
        self.assertIs(result, self.site)

    def test_errors_if_request_and_site_not_present_and_multiple_sites_exist(self):
        with self.assertRaises(RequestUnavailableError):
            MenuWithMenuItems._get_site({})

    def test_returns_site_if_request_and_site_not_present_and_single_site_exists(self):
        self.other_site.delete()
        result = MenuWithMenuItems._get_site({})
        self.assertEqual(result, self.site)
