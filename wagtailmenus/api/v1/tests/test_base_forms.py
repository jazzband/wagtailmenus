from unittest import mock

from django import forms
from django.http import Http404
from django.test import modify_settings, TestCase

from wagtail.core.models import Page, Site

from wagtailmenus.api.v1 import forms as app_forms

from .mixins import ArgumentFormTestMixin


class TestBaseAPIViewArgumentForm(ArgumentFormTestMixin, TestCase):

    class TestForm(app_forms.BaseAPIViewArgumentForm):
        slug_required = forms.SlugField()
        slug_optional = forms.SlugField(required=False)
        slug_with_initial = forms.SlugField(required=False, initial='initial_for_field')

    form_class = TestForm

    def test_view_and_request_values_are_set_at_initialisation(self):
        view_value = ''
        request_value = self.make_request()
        form = self.get_form(view=view_value, request=request_value)
        self.assertIs(form._view, view_value)
        self.assertIs(form._request, request_value)

    def test_data_supplementation_works_for_non_required_field(self):
        field_name = 'slug_optional'
        initial_value = 'provided'

        form = self.get_form(data={}, initial={field_name: initial_value})
        form.supplement_missing_data_with_initial_values()
        self.assertIs(form.data.get(field_name), initial_value)

    def test_data_supplementation_works_with_initial_value_on_field(self):
        field_name = 'slug_with_initial'

        form = self.get_form(data={}, initial={})
        form.supplement_missing_data_with_initial_values()
        self.assertEqual(form.data.get(field_name), 'initial_for_field')

    def test_data_supplementation_works_even_if_the_initial_value_is_falsey(self):
        field_name = 'slug_optional'
        test_values = (False, 0)

        for value in test_values:
            form = self.get_form(data={}, initial={field_name: value})
            form.supplement_missing_data_with_initial_values()
            self.assertIs(form.data.get(field_name), value)

    def test_data_supplementation_does_not_work_if_the_initial_value_is_none(self):
        field_name = 'slug_optional'
        initial_value = None

        form = self.get_form(data={}, initial={field_name: initial_value})
        form.supplement_missing_data_with_initial_values()
        self.assertNotIn(field_name, form.data)

    def test_data_supplementation_does_not_works_for_required_field(self):
        test_data = {}
        field_name = 'slug_required'
        initial_value = 'provided'

        form = self.get_form(data=test_data, initial={field_name: initial_value})
        form.supplement_missing_data_with_initial_values()
        self.assertNotIn(field_name, form.data)

    def test_helper_method_returns_none_if_crispy_forms_not_installed(self):
        form = self.get_form()
        result = form.helper
        self.assertIs(result, None)

    def test_template_name_returns_standard_form_template_if_crispy_forms_not_installed(self):
        form = self.get_form()
        result = form.template_name
        self.assertTrue(result.endswith('/form.html'))

    @modify_settings(INSTALLED_APPS={'append': 'crispy_forms'})
    def test_helper_method_returns_formhelper_instance_if_crispy_forms_is_installed(self):
        from crispy_forms.helper import FormHelper
        form = self.get_form()
        result = form.helper
        self.assertIsInstance(result, FormHelper)

    @modify_settings(INSTALLED_APPS={'append': 'crispy_forms'})
    def test_template_name_returns_crispy_form_template_if_crispy_forms_is_installed(self):
        form = self.get_form()
        result = form.template_name
        self.assertTrue(result.endswith('/crispy_form.html'))


class TestDeriveSite(ArgumentFormTestMixin, TestCase):

    form_class = app_forms.BaseMenuGeneratorArgumentForm

    @mock.patch.object(form_class, 'get_site_for_request')
    def test_does_not_attempt_to_derive_if_site_is_already_present(self, mocked_method):
        form = self.get_form()
        data = {'site': Site.objects.first()}
        form.derive_site(cleaned_data=data)
        self.assertFalse(mocked_method.called)

    @mock.patch.object(form_class, 'get_site_for_request', return_value='ABC')
    def test_sets_site_if_get_site_site_can_be_derived(self, mocked_method):
        form = self.get_form()
        data = {}
        form.derive_site(cleaned_data=data)
        self.assertTrue(mocked_method.called)
        self.assertEqual(data['site'], 'ABC')

    @mock.patch.object(form_class, 'get_site_for_request', return_value=None)
    def test_adds_field_error_if_site_cannot_be_derived(self, mocked_method):
        form = self.get_form(set_errors=True)
        data = {}
        form.cleaned_data = {}
        form.derive_site(cleaned_data=data)
        self.assertTrue(mocked_method.called)
        self.assertNotIn('site', data)
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.has_error('site'))


class TestGetSiteForRequest(ArgumentFormTestMixin, TestCase):

    form_class = app_forms.BaseMenuGeneratorArgumentForm

    def test_returns_site_attribute_from_request_if_a_site_object(self):
        form = self.get_form(set_errors=True)
        request = self.make_request()
        dummy_site = Site(hostname='beepboop')
        request.site = dummy_site

        result = form.get_site_for_request(request)
        self.assertIs(result, dummy_site)

    @mock.patch.object(Site, 'find_for_request')
    def test_find_for_request_called_if_site_attribute_is_not_a_site_object(self, mocked_method):
        form = self.get_form(set_errors=True)
        request = self.make_request()
        request.site = 'just a string'

        form.get_site_for_request(request)
        self.assertTrue(mocked_method.called)


class TestDeriveCurrentPage(ArgumentFormTestMixin, TestCase):

    form_class = app_forms.BaseMenuGeneratorArgumentForm

    def make_data_dict(self, **kwargs):
        """
        Returns a dictionary that can be passed as ``cleaned_data`' to
        derive_current_page() in tests.
        """
        defaults = {
            'current_page': None,
            'current_url': '/',
            'site': Site.objects.all().first(),
            'apply_active_classes': True,
        }
        result = defaults.copy()
        result.update(kwargs)
        return result

    @mock.patch.object(form_class, 'get_page_for_url')
    def test_does_not_attempt_to_derive_if_current_page_is_already_present(self, mocked_method):
        form = self.get_form()
        data = self.make_data_dict(current_page=Page.objects.first())
        form.derive_current_page(cleaned_data=data)
        self.assertFalse(mocked_method.called)

    @mock.patch.object(form_class, 'get_page_for_url')
    def test_does_not_attempt_to_derive_if_current_url_is_blank_or_none(self, mocked_method):
        form = self.get_form()
        test_values = ('', None)
        for val in test_values:
            data = self.make_data_dict(current_url=val)
            form.derive_current_page(cleaned_data=data)
            self.assertFalse(mocked_method.called)

    @mock.patch.object(form_class, 'get_page_for_url')
    def test_does_not_attempt_to_derive_if_site_is_none(self, mocked_method):
        form = self.get_form()
        data = self.make_data_dict(site=None)
        form.derive_current_page(cleaned_data=data)
        self.assertFalse(mocked_method.called)

    @mock.patch.object(form_class, 'get_page_for_url')
    def test_does_not_attempt_to_derive_if_apply_active_classes_if_false(
        self, mocked_method
    ):
        form = self.get_form()
        data = self.make_data_dict(apply_active_classes=False)
        form.derive_current_page(cleaned_data=data)
        self.assertFalse(mocked_method.called)

    @mock.patch.object(form_class, 'get_page_for_url', return_value=(None, False))
    def test_attempts_if_apply_active_classes_if_false_but_force_derivation_is_true(
        self, mocked_method
    ):
        form = self.get_form()
        data = self.make_data_dict(apply_active_classes=False)
        form.derive_current_page(cleaned_data=data, force_derivation=True)
        self.assertTrue(mocked_method.called)

    @mock.patch.object(form_class, 'get_page_for_url', return_value=('XYZ', True))
    def test_sets_current_page_if_full_url_match_found(
        self, mocked_method
    ):
        form = self.get_form()
        data = self.make_data_dict()
        form.derive_current_page(cleaned_data=data)
        self.assertTrue(mocked_method.called)
        self.assertEqual(data['current_page'], 'XYZ')
        self.assertIs(data.get('best_match_page'), None)

    @mock.patch.object(form_class, 'get_page_for_url', return_value=('XYZ', False))
    def test_sets_best_match_page_if_partial_url_match_found(
        self, mocked_method
    ):
        form = self.get_form()
        data = self.make_data_dict()
        form.derive_current_page(cleaned_data=data)
        self.assertTrue(mocked_method.called)
        self.assertEqual(data['best_match_page'], 'XYZ')
        self.assertIs(data.get('current_page'), None)


class TestGetPageForURL(ArgumentFormTestMixin, TestCase):

    form_class = app_forms.BaseMenuGeneratorArgumentForm

    @mock.patch.object(Page, 'route')
    def test_no_match_attempts_made_if_url_is_blank_or_none(self, mocked_method):
        form = self.get_form()
        site = Site.objects.first()

        for url in ('', None):
            form.get_page_for_url(url, site)

        self.assertFalse(mocked_method.called)

    @mock.patch.object(Page, 'route', side_effect=Http404('Not found'))
    def test_attempts_match_until_path_components_are_exhausted(self, mocked_method):
        form = self.get_form()
        url = '/news-and-events/latest-news/blah/'
        path_components = [pc for pc in url.split('/') if pc]
        site = Site.objects.first()

        form.get_page_for_url(url, site)
        self.assertEqual(mocked_method.call_count, len(path_components))

    @mock.patch.object(Page, 'route', side_effect=Http404('Not found'))
    def test_attempts_only_once_if_accept_best_match_is_false(self, mocked_method):
        form = self.get_form()
        url = '/news-and-events/latest-news/blah/'
        site = Site.objects.first()

        form.get_page_for_url(url, site, accept_best_match=False)
        self.assertEqual(mocked_method.call_count, 1)

    @mock.patch.object(Page, 'route', return_value=(1, 2, 3))
    def test_exact_match_is_true_if_result_found_on_first_attempt(self, mocked_method):
        form = self.get_form()
        url = '/news-and-events/latest-news/blah/'
        site = Site.objects.first()

        page, exact_match = form.get_page_for_url(url, site)
        self.assertIs(exact_match, True)

    @mock.patch.object(Page, 'route', side_effect=[Http404('Not found'), (1, 2, 3)])
    def test_exact_match_is_false_if_result_found_on_consecutive_attempt(self, mocked_method):
        form = self.get_form()
        url = '/news-and-events/latest-news/blah/'
        site = Site.objects.first()

        page, exact_match = form.get_page_for_url(url, site)
        self.assertIs(exact_match, False)


class TestDeriveAncestorPageIDs(ArgumentFormTestMixin, TestCase):

    form_class = app_forms.BaseMenuGeneratorArgumentForm

    def make_data_dict(self, **kwargs):
        """
        Returns a dictionary that can be passed as ``cleaned_data`' to
        derive_current_page() in tests.
        """
        defaults = {
            'apply_active_classes': True,
        }
        result = defaults.copy()
        result.update(kwargs)
        return result

    def test_does_not_attempt_to_derive_if_no_page_is_set(self):
        form = self.get_form()
        data = self.make_data_dict(current_page=None, best_match_page=None)
        with self.assertNumQueries(0):
            form.derive_ancestor_page_ids(cleaned_data=data)

    def test_attempts_to_derive_if_current_page_is_set(self):
        form = self.get_form()
        data = self.make_data_dict(current_page=Page.objects.first())
        with self.assertNumQueries(1):
            form.derive_ancestor_page_ids(cleaned_data=data)

    def test_attempts_to_derive_if_best_match_page_is_set(self):
        form = self.get_form()
        data = self.make_data_dict(best_match_page=Page.objects.first())
        with self.assertNumQueries(1):
            form.derive_ancestor_page_ids(cleaned_data=data)

    def test_does_not_attempt_to_derive_if_apply_active_classes_is_false(self):
        form = self.get_form()
        data = self.make_data_dict(current_page=Page.objects.first(), apply_active_classes=False)
        with self.assertNumQueries(0):
            form.derive_ancestor_page_ids(cleaned_data=data)
