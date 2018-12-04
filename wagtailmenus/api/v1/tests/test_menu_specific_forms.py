from unittest import mock

from django.test import TestCase

from wagtail.core.models import Page, Site

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
        pass

    def test_derive_parent_page_uses_the_current_page_value_if_present(self):
        pass

    def test_derive_parent_page_does_not_use_the_best_match_page_if_present(self):
        pass

    def test_derive_parent_page_adds_a_field_error_when_current_page_is_none(self):
        pass

    def test_derive_parent_page_adds_a_field_error_when_current_page_is_not_present(self):
        pass


class TestSectionMenuGeneratorArgumentForm(CommonArgumentFormTestsMixin, ArgumentFormTestMixin, TestCase):
    """
    Runs tests from ``CommonArgumentFormTestsMixin`` for the ``SectionMenuGeneratorArgumentForm``,
    as well as testing any form-specific behaviour.
    """
    form_class = forms.SectionMenuGeneratorArgumentForm

    def test_clean_triggers_derive_section_root_page(self):
        form = self.get_form()
        self.assertTrue(self._clean_triggers_call_to_method(form, method_name='derive_section_root_page'))

    def test_derive_section_root_page_changes_nothing_if_value_is_already_present(self):
        pass

    def test_derive_section_root_page_uses_the_current_page_value_if_present(self):
        pass

    def test_derive_section_root_page_adds_a_field_error_when_both_page_values_are_none(self):
        pass

    def test_derive_section_root_page_adds_a_field_error_when_neither_page_value_is_present(self):
        pass
