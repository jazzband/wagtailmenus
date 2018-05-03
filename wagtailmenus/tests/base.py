from django.test import TestCase, override_settings

from wagtailmenus.tests import utils


class GetSubMenuTemplateNamesMethodTestCase(TestCase):
    """
    A 'base' test case for a testing a menu class's
    get_sub_menu_template_names() method.
    """

    expected_default_result_length = None

    def get_test_menu_instance(self):
        # Must be overridden to supply a menu instance of the right type
        raise NotImplementedError()

    def get_test_site_instance(self):
        Site = utils.get_site_model()
        Page = utils.get_page_model()
        return Site.objects.all().first() or Site.objects.create(
            id=1,
            hostname='wagtailmenus.co.uk',
            root_page=Page.objects.first(),
        )

    def test_site_specific_templates_not_returned_by_default(self):
        menu = self.get_test_menu_instance()
        site = self.get_test_site_instance()

        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=site
        )
        result = menu.get_sub_menu_template_names()
        self.assertEqual(len(result), self.expected_default_result_length)
        for val in result:
            self.assertFalse(site.hostname in val)

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True)
    def test_specific_templates_returned_if_setting_is_true_and_current_site_is_in_contextual_vals(self):
        menu = self.get_test_menu_instance()
        site = self.get_test_site_instance()

        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=site
        )
        result = menu.get_sub_menu_template_names()
        self.assertGreater(len(result), self.expected_default_result_length)
        for val in result[:2]:
            self.assertTrue(site.hostname in val)

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True)
    def test_specific_templates_not_returned_if_current_site_not_in_contextual_vals(self):
        menu = self.get_test_menu_instance()
        site = self.get_test_site_instance()

        menu._contextual_vals = utils.make_contextualvals_instance(
            current_site=None
        )
        result = menu.get_sub_menu_template_names()
        self.assertEqual(len(result), self.expected_default_result_length)
        for val in result:
            self.assertTrue(site.hostname not in val)


class GetTemplateNamesMethodTestCase(TestCase):

    expected_default_result_length = 3

    def get_test_menu_instance(self):
        # Must be overridden to supply a menu instance of the right type
        raise NotImplementedError()

    def get_test_site_instance(self):
        Site = utils.get_site_model()
        Page = utils.get_page_model()
        return Site.objects.all().first() or Site.objects.create(
            id=1,
            hostname='wagtailmenus.co.uk',
            root_page=Page.objects.first(),
        )

    def test_site_specific_templates_not_returned_by_default(self):
        menu = self.get_test_menu_instance()
        site = self.get_test_site_instance()

        menu._contextual_vals = utils.make_contextualvals_instance(
            url='/', current_site=site
        )
        result = menu.get_template_names()
        self.assertEqual(len(result), self.expected_default_result_length)
        for val in result:
            self.assertFalse(site.hostname in val)

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True)
    def test_site_specific_templates_returned_if_setting_is_true_and_current_site_is_in_contextual_vals(self):
        menu = self.get_test_menu_instance()
        site = self.get_test_site_instance()

        menu._contextual_vals = utils.make_contextualvals_instance(
            url='/', current_site=site
        )
        result = menu.get_template_names()
        self.assertGreater(len(result), self.expected_default_result_length)
        for val in result[:2]:
            self.assertTrue(site.hostname in val)

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True)
    def test_specific_templates_not_returned_if_current_site_not_in_contextual_vals(self):
        menu = self.get_test_menu_instance()
        site = self.get_test_site_instance()

        menu._contextual_vals = utils.make_contextualvals_instance(
            url='/', current_site=None
        )
        result = menu.get_template_names()
        self.assertEqual(len(result), self.expected_default_result_length)
        for val in result:
            self.assertTrue(site.hostname not in val)
