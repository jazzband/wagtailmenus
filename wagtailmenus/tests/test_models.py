from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from django.core.exceptions import ValidationError

from wagtail.wagtailcore.models import Page, Site
from wagtailmenus.models import MainMenu, MainMenuItem, FlatMenu
from wagtailmenus.tests.models import LinkPage


class TestModels(TestCase):
    fixtures = ['test.json']

    def test_mainmenuitem_clean_missing_link_text(self):
        menu = MainMenu.objects.get(pk=1)
        new_item = MainMenuItem(menu=menu, link_url='test/')
        self.assertRaisesMessage(
            ValidationError,
            "This field is required when linking to a custom URL",
            new_item.clean)

    def test_mainmenuitem_clean_missing_link_url(self):
        menu = MainMenu.objects.get(pk=1)
        new_item = MainMenuItem(menu=menu)
        self.assertRaisesMessage(
            ValidationError,
            "Please choose an internal page or provide a custom URL",
            new_item.clean)

    def test_mainmenuitem_clean_link_url_and_link_page(self):
        menu = MainMenu.objects.get(pk=1)
        new_item = MainMenuItem(
            menu=menu,
            link_text='Test',
            link_url='test/',
            link_page=Page.objects.get(pk=6))
        self.assertRaisesMessage(
            ValidationError,
            "Linking to both a page and custom URL is not permitted",
            new_item.clean)

    def test_mainmenuitem_str(self):
        menu = MainMenu.objects.get(pk=1)
        item_1 = menu.menu_items.first()
        self.assertEqual(item_1.__str__(), 'Home')

    def test_flatmenuitem_str(self):
        menu = FlatMenu.objects.get(handle='contact')
        item_1 = menu.menu_items.first()
        self.assertEqual(item_1.__str__(), 'Call us')

    def test_mainmenu_top_level_items(self):
        menu = MainMenu.objects.get(pk=1)
        # This menu has a `use_specific` value of 1 (AUTO)
        self.assertEqual(menu.use_specific, 1)

        # So, the top-level items it return should all just be custom links
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

    def test_mainmenu_pages_for_display(self):
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


class TestLinkPage(TestCase):
    fixtures = ['test.json']

    def setUp(self):
        # Create a few of link pages for testing
        site = Site.objects.select_related('root_page').get(is_default_site=True)
        self.site = site

        linkpage_to_page = LinkPage(
            title='Find out about Spiderman',
            link_page_id=30,
            url_append='?somevar=value'
        )
        site.root_page.add_child(instance=linkpage_to_page)

        # Check that the above page was saved and has field values we expect
        self.assertTrue(linkpage_to_page.id)
        self.assertTrue(linkpage_to_page.show_in_menus)
        self.assertTrue(linkpage_to_page.show_in_menus_custom())
        self.assertEqual(linkpage_to_page.get_sitemap_urls(), [])
        self.linkpage_to_page = linkpage_to_page

        linkpage_to_url = LinkPage(
            title='Do a google search',
            link_url="https://www.google.co.uk",
            url_append='?somevar=value',
            extra_classes='google external',
        )
        site.root_page.add_child(instance=linkpage_to_url)

        # Check that the above page was saved and has field values we expect
        self.assertTrue(linkpage_to_url.id)
        self.assertTrue(linkpage_to_url.show_in_menus)
        self.assertTrue(linkpage_to_url.show_in_menus_custom())
        self.assertEqual(linkpage_to_url.get_sitemap_urls(), [])
        self.linkpage_to_url = linkpage_to_url

        linkpage_to_non_routable_page = LinkPage(
            title='Go to this unroutable page',
            link_page_id=2,
            url_append='?somevar=value'
        )
        site.root_page.add_child(instance=linkpage_to_non_routable_page)
        self.linkpage_to_non_routable_page = linkpage_to_non_routable_page

    def test_url_methods(self):
        # When linking to a page
        self.assertEqual(
            self.linkpage_to_page.relative_url(self.site),
            '/superheroes/marvel-comics/spiderman/?somevar=value'
        )
        self.assertEqual(
            self.linkpage_to_page.full_url,
            'http://www.wagtailmenus.co.uk:8000/superheroes/marvel-comics/spiderman/?somevar=value'
        )

        # When linking to a non-routable page
        self.assertEqual(self.linkpage_to_non_routable_page.relative_url(self.site), '')
        self.assertEqual(self.linkpage_to_non_routable_page.full_url, '')

        # When linking to a custom url
        self.assertEqual(
            self.linkpage_to_url.relative_url(self.site), 'https://www.google.co.uk?somevar=value'
        )
        self.assertEqual(
            self.linkpage_to_url.full_url, 'https://www.google.co.uk?somevar=value'
        )

    def test_linkpage_visibility(self):
        page_link_html = (
            '<a href="/superheroes/marvel-comics/spiderman/?somevar=value">Find out about Spiderman</a>'
        )

        url_link_html = (
            '<li class="google external"><a href="https://www.google.co.uk?somevar=value">Do a google search</a></li>'
        )
        # When the target page is live, both the 'Spiderman' and 'Google' link should appear 
        response = self.client.get('/')
        self.assertContains(response, page_link_html, html=True)
        self.assertContains(response, url_link_html, html=True)

        # When the target page is not live, the linkpage shouldn't appear
        target_page = self.linkpage_to_page.link_page
        target_page.live = False
        target_page.save()
        response = self.client.get('/')
        self.assertNotContains(response, page_link_html, html=True)

        # When the target page isn't set to appear in menus, the linkpage
        # shouldn't appear
        target_page.live = True
        target_page.show_in_menus = False
        target_page.save()
        response = self.client.get('/')
        self.assertNotContains(response, page_link_html, html=True)

        # When the target page is 'expired', the linkpage shouldn't appear
        target_page.show_in_menus = True
        target_page.expired = True
        target_page.save()
        response = self.client.get('/')
        self.assertNotContains(response, page_link_html, html=True)

    def test_linkpage_clean(self):
        linkpage = self.linkpage_to_page
        linkpage.link_url = 'https://www.rkh.co.uk/'
        self.assertRaisesMessage(
            ValidationError,
            "Linking to both a page and custom URL is not permitted",
            linkpage.clean
        )

        linkpage.link_url = ''
        linkpage.link_page = None
        self.assertRaisesMessage(
            ValidationError,
            "Please choose an internal page or provide a custom URL",
            linkpage.clean
        )

        linkpage.link_page = linkpage
        self.assertRaisesMessage(
            ValidationError,
            "A link page cannot link to another link page",
            linkpage.clean
        )

    def test_linkpage_redirects_when_served(self):
        response = self.client.get('/find-out-about-spiderman/')
        self.assertRedirects(
            response,
            '/superheroes/marvel-comics/spiderman/?somevar=value'
        )
