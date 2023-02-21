from django.test import RequestFactory, TestCase, modify_settings
from wagtail.models import Page, Site

from wagtailmenus.conf import defaults
from wagtailmenus.tests.models import (ArticleListPage, ArticlePage,
                                       LowLevelPage, TopLevelPage)
from wagtailmenus.utils.misc import (derive_page, derive_section_root,
                                     get_fake_request, get_site_from_request)


class TestGetFakeRequest(TestCase):
    """Ensures the value returned by get_fake_request() is compatible
    with Page url methods."""

    fixtures = ['test.json']

    def setUp(self):
        self.page = Page.objects.last()
        self.site = self.page.get_site()
        self.relative_page_url = self.page.get_url(current_site=self.site)
        self.full_page_url = self.page.full_url
        self.fake_request = get_fake_request()

    def test_works_with_get_url(self):
        result = self.page.get_url(self.fake_request, self.site)
        self.assertEqual(result, self.relative_page_url)

    def test_works_with_relative_url(self):
        result = self.page.relative_url(self.site, request=self.fake_request)
        self.assertEqual(result, self.relative_page_url)

    def test_works_with_full_url(self):
        result = self.page.get_full_url(request=self.fake_request)
        self.assertEqual(result, self.full_page_url)


class TestDerivePage(TestCase):
    """Tests for wagtailmenus.utils.misc.derive_page()"""
    fixtures = ['test.json']

    def setUp(self):
        # Every test needs access to the request factory.
        self.rf = RequestFactory()
        self.site = Site.objects.select_related('root_page').first()
        # Prefetch the specific page, so that it doesn't count
        # toward the counted queries
        self.site.root_page.specific

    def _run_test(
        self, url, expected_page, expected_num_queries, full_url_match_expected,
        accept_best_match=True, max_subsequent_route_failures=3
    ):
        request = self.rf.get(url)
        # Set these to improve efficiency
        request.site = self.site
        request._wagtail_cached_site_root_paths = Site.get_site_root_paths()
        # Run tests
        with self.assertNumQueries(expected_num_queries):
            page, full_url_match = derive_page(
                request,
                self.site,
                accept_best_match,
                max_subsequent_route_failures,
            )
            self.assertEqual(page, expected_page)
            self.assertIs(full_url_match, full_url_match_expected)

    def test_simple_full_url_match(self):
        """
        Routing should use 4 queries here:
        1. Look up 'superheroes' from site root
        2. Fetch specific version of 'superheroes'
        3. Look up 'marvel-comics' from 'superheroes'
        4. Fetch specific version of 'marvel-comics'
        """
        self._run_test(
            url='/superheroes/marvel-comics/',
            expected_page=LowLevelPage.objects.get(slug='marvel-comics'),
            expected_num_queries=4,
            full_url_match_expected=True,
        )

    def test_article_list_full_url_match(self):
        """
        Routing should use 4 queries here:
        1. Look up 'news-and-events' from site root
        2. Fetch specific version of 'news-and-events'
        3. Look up 'latest-news' from 'news-and-events'
        4. Fetch specific version of 'latest-news'
        """
        self._run_test(
            url='/news-and-events/latest-news/2016/04/',
            expected_page=ArticleListPage.objects.get(slug='latest-news'),
            expected_num_queries=4,
            full_url_match_expected=True,
        )

    def test_article_full_url_match(self):
        """
        Routing should use 5 queries here:
        1. Look up 'news-and-events' from site root
        2. Fetch specific version of 'news-and-events'
        3. Look up 'latest-news' from 'news-and-events'
        4. Fetch specific version of 'latest-news'
        5. Look up 'article-one' from 'latest-news'
        """
        self._run_test(
            url='/news-and-events/latest-news/2016/04/18/article-one/',
            expected_page=ArticlePage.objects.get(slug='article-one'),
            expected_num_queries=5,
            full_url_match_expected=True,
        )

    def test_simple_partial_match(self):
        """
        Routing should use 4 queries here:
        1. Look up 'about-us' from site root
        2. Fetch specific version of 'about-us'
        3. Attempt to look up 'blah' from 'about-us'
        """
        self._run_test(
            url='/about-us/blah/',
            expected_page=TopLevelPage.objects.get(slug='about-us'),
            expected_num_queries=3,
            full_url_match_expected=False,
        )

    def test_article_list_partial_match(self):
        """
        Routing should use 4 queries here:
        1. Look up 'news-and-events' from site root
        2. Fetch specific version of 'news-and-events'
        3. Look up 'latest-news' from 'news-and-events'
        4. Fetch specific version of 'latest-news'
        5. Attempt to look up 'blah' from 'latest-news'
        6. Attempt to look up 'blah/blah/' from 'latest-news'
        """
        self._run_test(
            url='/news-and-events/latest-news/2016/04/01/blah/blah/',
            expected_page=ArticleListPage.objects.get(slug='latest-news'),
            expected_num_queries=6,
            full_url_match_expected=False,
        )

    def test_partial_match_with_max_subsequent_route_failures(self):
        """
        Routing should use 5 queries here:
        1. Look up 'about-us' from site root
        2. Fetch specific version of 'about-us'
        3. Attempt to look up 'blah' from 'about-us'
        4. Attempt to look up 'blah/blah/' from 'about-us'
        5. Attempt to look up 'blah/blah/blah/' from 'about-us'
        """
        self._run_test(
            url='/about-us/blah/blah/blah/blah/blah',
            expected_page=TopLevelPage.objects.get(slug='about-us'),
            expected_num_queries=5,
            full_url_match_expected=False,
        )

    def test_no_match(self):
        """
        This test also shows that using the ``max_subsequent_route_failures`` option
        directly affects the number of route() attempts that will be made, even when
        """
        common_test_kwargs = {
            'url': '/blah/blah/blah/blah/blah',
            'expected_page': None,
            'full_url_match_expected': False,
        }
        for i in range(1, 3):
            self._run_test(
                expected_num_queries=i,
                max_subsequent_route_failures=i,
                **common_test_kwargs
            )

    def test_exact_match_only_with_success(self):
        self._run_test(
            url='/about-us/',
            expected_page=TopLevelPage.objects.get(slug='about-us'),
            expected_num_queries=2,
            full_url_match_expected=True,
            accept_best_match=False
        )

    def test_exact_match_only_without_success(self):
        self._run_test(
            url='/blah/blah/blah/blah/blah',
            expected_page=None,
            expected_num_queries=1,
            full_url_match_expected=False,
            accept_best_match=False
        )


class TestDeriveSectionRoot(TestCase):
    """Tests for wagtailmenus.utils.misc.derive_section_root()"""
    fixtures = ['test.json']

    def setUp(self):
        self.page_with_depth_of_2 = Page.objects.get(
            depth=2, url_path='/home/'
        )
        self.page_with_depth_of_3 = Page.objects.get(
            depth=3, url_path='/home/about-us/'
        )
        self.page_with_depth_of_4 = Page.objects.get(
            depth=4, url_path='/home/about-us/meet-the-team/'
        )
        self.page_with_depth_of_5 = Page.objects.get(
            depth=5, url_path='/home/about-us/meet-the-team/staff-member-one/'
        )

    def test_returns_same_page_if_provided_page_is_section_root(self):
        # Using the default section root depth of 3
        with self.assertNumQueries(1):
            # One query should be used to get the specific page
            result = derive_section_root(self.page_with_depth_of_3)
            # The function should return the specific version of the same page
            self.assertEqual(result, self.page_with_depth_of_3.specific)

        # Using a custom section root depth of 4
        with self.settings(WAGTAILMENUS_SECTION_ROOT_DEPTH=4):
            with self.assertNumQueries(1):
                # One query should be used to get the specific page
                result = derive_section_root(self.page_with_depth_of_4)
                # The function should return the specific version of the same page
                self.assertEqual(result, self.page_with_depth_of_4.specific)

    def test_returns_section_root_if_provided_page_is_a_descendant_of_one(self):
        # Using the default section root depth of 3
        with self.assertNumQueries(2):
            # Two queries should be used to identify the page
            # and to get the specific version
            result = derive_section_root(self.page_with_depth_of_5)
            self.assertEqual(result.depth, defaults.SECTION_ROOT_DEPTH)
            self.assertIsInstance(result, TopLevelPage)

        # Using a custom section root depth of 4
        with self.settings(WAGTAILMENUS_SECTION_ROOT_DEPTH=4):
            with self.assertNumQueries(2):
                result = derive_section_root(self.page_with_depth_of_5)
                self.assertEqual(result.depth, 4)
                self.assertIsInstance(result, LowLevelPage)

    def test_returns_none_if_provided_page_is_not_a_descendant_of_a_section_root(self):
        # Using the default section root depth of 3
        with self.assertNumQueries(0):
            result = derive_section_root(self.page_with_depth_of_2)
            self.assertIs(result, None)

        # Using a custom section root depth of 4
        with self.settings(WAGTAILMENUS_SECTION_ROOT_DEPTH=4):
            with self.assertNumQueries(0):
                result = derive_section_root(self.page_with_depth_of_3)
                self.assertIs(result, None)


class TestGetSiteFromRequest(TestCase):
    """Tests for wagtailmenus.utils.misc.get_site_from_request()"""
    fixtures = ['test.json']

    def setUp(self):
        # URL to request during test
        self.url = '/superheroes/marvel-comics/'

    def _run_test(self):
        """
        Confirm that the Site returned by get_site_from_request() is a Wagtail Site
        instance.
        """
        request = self.client.get(self.url).wsgi_request
        site = get_site_from_request(request)
        self.assertIsInstance(site, Site)

    def test_with_wagtail_site_in_request(self):
        """
        Test when Wagtail Site exists at request.site.
        """
        self._run_test()

    @modify_settings(MIDDLEWARE={
        'append': 'django.contrib.sites.middleware.CurrentSiteMiddleware',
        'remove': 'wagtail.core.middleware.SiteMiddleware',
    })
    def test_with_django_site_in_request(self):
        """
        Test when only a Django Site exists at request.site for Wagtail 2.9 and above.
        """
        self._run_test()

    @modify_settings(MIDDLEWARE={'remove': 'wagtail.core.middleware.SiteMiddleware'})
    def test_with_no_site_in_request(self):
        """
        Test when no Site object exists at request.site for Wagtail 2.9 and above.
        """
        self._run_test()
