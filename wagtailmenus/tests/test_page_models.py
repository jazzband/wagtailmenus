from django.core.exceptions import ValidationError
from django.test import TestCase
from wagtail.models import Site

from wagtailmenus.tests.models import LinkPage


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
        # When the target page is live, both the 'Spiderman' and 'Google' link
        # should appear
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


