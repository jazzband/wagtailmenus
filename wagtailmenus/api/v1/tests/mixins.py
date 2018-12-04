from unittest import mock

from django import forms
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.test import override_settings, RequestFactory
from django.urls import reverse


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


class CommonArgumentFormTestsMixin:
    """
    We want to run these tests for all argument forms to ensure the behaviour
    remains consistent, so a Mixin seems like the best approach.
    """

    def test_current_page_field_queryset_gets_set_on_init(self):
        form = self.get_form()
        self.assertTrue(form.fields['current_page'].queryset.exists())

    def test_site_field_queryset_gets_set_on_init(self):
        form = self.get_form()
        self.assertTrue(form.fields['site'].queryset.exists())

    def test_language_field_has_select_widget_when_use_i18n_is_true(self):
        form = self.get_form()
        self.assertIsInstance(form.fields['language'].widget, forms.Select)

    @override_settings(USE_I18N=False)
    def test_language_field_has_hiddeninput_widget_when_use_i18n_is_false(self):
        form = self.get_form()
        self.assertIsInstance(form.fields['language'].widget, forms.HiddenInput)

    def _clean_triggers_call_to_method(self, form, method_name):
        # Setting this to an empty dict to avoid having to run full_clean()
        form.cleaned_data = {}
        # Mocking the method here to keep things quick
        with mock.patch.object(form, method_name, return_value=None) as mocked_method:
            try:
                form.clean()
            except ValidationError:
                pass
            return mocked_method.called

    def test_clean_triggers_derive_current_page(self):
        form = self.get_form()
        self.assertTrue(self._clean_triggers_call_to_method(form, method_name='derive_current_page'))

    def test_clean_triggers_derive_ancestor_page_ids(self):
        form = self.get_form()
        self.assertTrue(self._clean_triggers_call_to_method(form, method_name='derive_ancestor_page_ids'))
