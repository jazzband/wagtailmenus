from unittest import mock

from django import forms
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
