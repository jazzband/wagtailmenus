from django.test import TestCase

from wagtail.core.models import Page

from wagtailmenus.conf import settings
from wagtailmenus.api.v1 import forms

from .mixins import ArgumentFormTestMixin, CommonArgumentFormTestsMixin


class TestMainMenuGeneratorArgumentForm(CommonArgumentFormTestsMixin, ArgumentFormTestMixin, TestCase):
    """
    Runs tests from ``CommonArgumentFormTestsMixin`` for the ``MainMenuGeneratorArgumentForm``
    """
    form_class = forms.MainMenuGeneratorArgumentForm


class TestFlatMenuGeneratorArgumentForm(CommonArgumentFormTestsMixin, ArgumentFormTestMixin, TestCase):
    """
    Runs tests from ``CommonArgumentFormTestsMixin`` for the ``FlatMenuGeneratorArgumentForm``
    """
    form_class = forms.FlatMenuGeneratorArgumentForm


class TestChildrenMenuGeneratorArgumentForm(CommonArgumentFormTestsMixin, ArgumentFormTestMixin, TestCase):
    """
    Runs tests from ``CommonArgumentFormTestsMixin`` for the ``ChildrenMenuGeneratorArgumentForm``,
    as well as testing any form-specific behaviour.
    """
    form_class = forms.ChildrenMenuGeneratorArgumentForm

    def test_clean_triggers_derive_parent_page(self):
        form = self.get_form()
        self.assertTrue(self._clean_triggers_call_to_method(form, method_name='derive_parent_page'))

    def test_derive_parent_page_changes_nothing_if_value_is_already_present(self):
        # Prepare form and values for test
        form = self.get_form(set_errors=True)
        parent_page_value = 'ABC'
        data = {'parent_page': parent_page_value}
        form.cleaned_data = data

        # Call the method
        form.derive_parent_page(data)

        # Check outcome
        self.assertIs(data['parent_page'], parent_page_value)
        self.assertFalse(form.errors)

    def test_derive_parent_page_uses_the_current_page_value_if_present(self):
        # Prepare form and values for test
        form = self.get_form(set_errors=True)
        current_page_value = 'ABC'
        data = {'current_page': current_page_value}
        form.cleaned_data = data

        # Call the method
        form.derive_parent_page(data)

        # Check outcome
        self.assertIs(data['parent_page'], current_page_value)
        self.assertFalse(form.errors)

    def test_derive_parent_page_does_not_use_the_best_match_page_if_present(self):
        # Prepare form and values for test
        form = self.get_form(set_errors=True)
        data = {'best_match_page': 'ABC'}
        form.cleaned_data = data

        # Call the method
        form.derive_parent_page(data)

        # Check outcome
        self.assertNotIn('parent_page', data)
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.has_error('parent_page'))

    def test_derive_parent_page_adds_a_field_error_when_current_page_is_none(self):
        # Prepare form and values for test
        form = self.get_form(set_errors=True)
        data = {'current_page': None}
        form.cleaned_data = data

        # Call the method
        form.derive_parent_page(data)

        # Check outcome
        self.assertNotIn('parent_page', data)
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.has_error('parent_page'))

    def test_derive_parent_page_adds_a_field_error_when_current_page_is_not_present(self):
        # Prepare form and values for test
        form = self.get_form(set_errors=True)
        data = {}
        form.cleaned_data = data

        # Call the method
        form.derive_parent_page(data)

        # Check outcome
        self.assertNotIn('parent_page', data)
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.has_error('parent_page'))


class TestSectionMenuGeneratorArgumentForm(CommonArgumentFormTestsMixin, ArgumentFormTestMixin, TestCase):
    """
    Runs tests from ``CommonArgumentFormTestsMixin`` for the ``SectionMenuGeneratorArgumentForm``,
    as well as testing any form-specific behaviour.
    """
    form_class = forms.SectionMenuGeneratorArgumentForm
    fixtures = ['test.json']

    def test_clean_triggers_derive_section_root_page(self):
        form = self.get_form()
        self.assertTrue(self._clean_triggers_call_to_method(form, method_name='derive_section_root_page'))

    def test_derive_section_root_page_changes_nothing_if_value_is_already_present(self):
        # Prepare form and values for test
        form = self.get_form(set_errors=True)
        section_root_page_value = 'ABC'
        data = {'section_root_page': section_root_page_value}
        form.cleaned_data = data

        # Call the method
        with self.assertNumQueries(0):
            form.derive_section_root_page(data)

        # Check outcome
        self.assertIs(data['section_root_page'], section_root_page_value)
        self.assertFalse(form.errors)

    def test_derive_section_root_page_adds_a_field_error_when_neither_page_value_is_present(self):
        # Prepare form and values for test
        form = self.get_form(set_errors=True)
        data = {}
        form.cleaned_data = data

        # Call the method
        with self.assertNumQueries(0):
            form.derive_section_root_page(data)

        # Check outcome
        self.assertNotIn('section_root_page', data)
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.has_error('section_root_page'))

    def test_derive_section_root_page_adds_a_field_error_when_both_page_values_are_none(self):
        # Prepare form and values for test
        form = self.get_form(set_errors=True)
        data = {'current_page': None, 'best_match_page': None}
        form.cleaned_data = data

        # Call the method
        with self.assertNumQueries(0):
            form.derive_section_root_page(data)

        # Check outcome
        self.assertNotIn('section_root_page', data)
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.has_error('section_root_page'))

    def test_derive_section_root_page_uses_the_current_page_over_best_match_page_if_present(self):
        # Prepare form and values for test
        form = self.get_form(set_errors=True)
        current_page = Page.objects.get(url_path='/home/about-us/meet-the-team/staff-member-one/')
        best_match_page = Page.objects.get(url_path='/home/news-and-events/latest-news/')
        data = {
            'current_page': current_page,
            'best_match_page': best_match_page,
        }
        form.cleaned_data = data

        # Call the method
        with self.assertNumQueries(1):
            form.derive_section_root_page(data)

        # Check outcome
        self.assertEqual(
            data['section_root_page'],
            current_page.get_ancestors().get(depth__exact=settings.SECTION_ROOT_DEPTH)
        )
        self.assertFalse(form.errors)

    def test_derive_section_root_page_uses_the_best_match_page_if_current_page_not_present(self):
        # Prepare form and values for test
        form = self.get_form(set_errors=True)
        page = Page.objects.get(url_path='/home/news-and-events/latest-news/')
        data = {'best_match_page': page}
        form.cleaned_data = data

        # Call the method
        with self.assertNumQueries(1):
            form.derive_section_root_page(data)

        # Check outcome
        self.assertEqual(
            data['section_root_page'],
            page.get_ancestors().get(depth__exact=settings.SECTION_ROOT_DEPTH)
        )
        self.assertFalse(form.errors)

    def test_derive_section_root_page_uses_the_page_itself_if_a_section_root(self):
        # Prepare form and values for test
        form = self.get_form(set_errors=True)
        page = Page.objects.filter(depth__exact=settings.SECTION_ROOT_DEPTH).first()
        data = {'current_page': page}
        form.cleaned_data = data

        # Call the method
        with self.assertNumQueries(0):
            form.derive_section_root_page(data)

        # Check outcome
        self.assertIs(data['section_root_page'], page)
        self.assertFalse(form.errors)

    def test_derive_section_root_page_adds_field_error_if_page_is_below_section_root_depth(self):
        # Prepare form and values for test
        form = self.get_form(set_errors=True)
        page = Page.objects.get(url_path='/home/')
        data = {'current_page': page}
        form.cleaned_data = data

        # Call the method
        form.derive_section_root_page(data)

        # Check outcome
        self.assertNotIn('section_root_page', data)
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.has_error('section_root_page'))
