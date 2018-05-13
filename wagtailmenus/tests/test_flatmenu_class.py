from django.test import TestCase

from wagtailmenus.models import FlatMenu
from wagtailmenus.tests import base, utils

Page = utils.get_page_model()
Site = utils.get_site_model()


class FlatMenuTestCase(TestCase):
    """A base TestCase class for testing FlatMenu model class methods"""

    @staticmethod
    def create_test_menus_for_site(site, count=3, set_option_vals=False):
        for i in range(1, count + 1):
            obj = FlatMenu.objects.create(
                site=site, handle='test-%s' % i, title='Test Menu %s' % i
            )
            if set_option_vals:
                obj._option_vals = utils.make_optionvals_instance()
            yield obj

    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.menus = tuple(
            self.create_test_menus_for_site(self.site, set_option_vals=True)
        )

    def get_test_menu_instance(self):
        return self.menus[0]


class TestGetForSite(FlatMenuTestCase):
    """Unit tests for AbstractFlatMenu.get_for_site()"""
    def setUp(self):
        super().setUp()
        self.default_site = self.site
        self.not_default_site = Site.objects.create(
            hostname='test2.com',
            root_page=Page.objects.all().first(),
            is_default_site=False,
        )
        self.not_default_site_menus = tuple(
            self.create_test_menus_for_site(self.not_default_site)
        )

    def test_returns_none_if_no_match_for_supplied_site_and_fall_back_to_default_site_menus_is_false(self):
        test_handle = 'test-1'

        FlatMenu.objects.filter(site=self.not_default_site, handle=test_handle).delete()

        with self.assertNumQueries(1):
            result = FlatMenu.get_for_site(
                handle=test_handle,
                site=self.not_default_site,
                fall_back_to_default_site_menus=False
            )
        self.assertIs(result, None)

    def test_returns_menu_for_default_site_if_no_match_for_supplied_site_and_fall_back_to_default_site_menus_is_true(self):
        test_handle = 'test-1'

        FlatMenu.objects.filter(site=self.not_default_site, handle=test_handle).delete()

        expected_result = FlatMenu.objects.get(
            site=self.default_site, handle=test_handle)

        with self.assertNumQueries(1):
            result = FlatMenu.get_for_site(
                handle=test_handle,
                site=self.not_default_site,
                fall_back_to_default_site_menus=True
            )
        self.assertEqual(result, expected_result)

    def test_returns_provided_site_matches_over_default_site_matches(self):
        for handle in ('test-1', 'test-2', 'test-3'):
            with self.assertNumQueries(1):
                result = FlatMenu.get_for_site(
                    handle=handle,
                    site=self.not_default_site,
                    fall_back_to_default_site_menus=True
                )
            self.assertEqual(result.site_id, self.not_default_site.id)


class TestGetSubMenuTemplateNames(
    FlatMenuTestCase, base.GetSubMenuTemplateNamesMethodTestCase
):
    """
    Tests FlatMenu.get_sub_menu_template_names() using common test cases
    from base.GetTemplateNamesMethodTestCase
    """
    expected_default_result_length = 9


class TestGetTemplateNames(
    FlatMenuTestCase, base.GetTemplateNamesMethodTestCase
):
    """
    Tests FlatMenu.get_template_names() using common test cases from
    base.GetTemplateNamesMethodTestCase
    """
    expected_default_result_length = 10
