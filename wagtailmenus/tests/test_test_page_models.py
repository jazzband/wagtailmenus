from unittest.mock import ANY, patch

from django.test import TestCase

from wagtailmenus.tests.models import ArticleListPage, ArticlePage


class TestArticleListPage(TestCase):
    fixtures = ['test.json']
    base_url = '/news-and-events/latest-news/'

    @patch.object(ArticleListPage, 'get_context', return_value={})
    def test_custom_routes(self, mocked_method):
        request = ANY

        # default view
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)

        # year view
        response = self.client.get(self.base_url + '2019/')
        self.assertEqual(response.status_code, 200)
        mocked_method.assert_called_with(request, year='2019')

        # month view
        response = self.client.get(self.base_url + '2019/01/')
        self.assertEqual(response.status_code, 200)
        mocked_method.assert_called_with(request, year='2019', month='01')

        # day view
        response = self.client.get(self.base_url + '2019/01/01/')
        self.assertEqual(response.status_code, 200)
        mocked_method.assert_called_with(request, year='2019', month='01', day='01')

    def test_article_routing_with_invalid_date_url_raises_404(self):
        # 99 isn't a valid day
        response = self.client.get(self.base_url + '2019/01/99/slug/')
        self.assertEqual(response.status_code, 404)


class TestArticlePage(TestCase):
    fixtures = ['test.json']

    def test_url_includes_publish_date(self):
        self.assertEqual(
            ArticlePage.objects.get(slug='article-one').url,
            'http://www.wagtailmenus.co.uk:8000/news-and-events/latest-news/2016/04/18/article-one/'
        )
