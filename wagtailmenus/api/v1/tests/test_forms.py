from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.test import modify_settings, RequestFactory, TestCase
from django.urls import reverse

from wagtailmenus.api.v1 import forms as app_forms


class ArgumentFormTestMixin:
    url_namespace = 'wagtailmenus_api:v1'
    default_request_url_name = 'main_menu'
    form_class = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.request_factory = RequestFactory()

    def get_form_class(self):
        if self.form_class is None:
            raise ImproperlyConfigured(
                "The 'form_class' attribute on '%s' must be set to something "
                "other than None" % self.__class__
            )
        return self.form_class

    def get_form(self, view=None, request=None, data=None, initial={}):
        # 'view' isn't really used anywhere, so it's safe to leave as None
        # However, we can easily create a stand-in value for 'request'
        if request is None:
            request = self.make_request()
        form_cls = self.get_form_class()
        return form_cls(view, request, data=data, initial=initial)

    def make_request(self, url=None, url_name=None):
        if url is None:
            url_name = url_name or self.default_request_url_name
            if not url_name.startswith(self.url_namespace):
                url_name = self.url_namespace + ':' + url_name
            url = reverse(url_name)
        return self.request_factory.get(url)


class TestBaseAPIViewArgumentForm(ArgumentFormTestMixin, TestCase):

    class TestForm(app_forms.BaseAPIViewArgumentForm):
        slug_required = forms.SlugField()
        slug_optional = forms.SlugField(required=False)
        slug_with_initial = forms.SlugField(required=False, initial='initial_for_field')
        field_order = ('slug_optional', 'slug_with_initial', 'slug')

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
