from unittest.mock import ANY, Mock, patch

from django.test import TestCase
from rest_framework.fields import CharField
from rest_framework.serializers import Serializer

from wagtailmenus.api.v1 import serializers
from wagtailmenus.api.v1.views import BaseModelMenuGeneratorView
from wagtailmenus.tests.models import CustomFlatMenu


class TestView(BaseModelMenuGeneratorView):
    menu_class = CustomFlatMenu


class TestBaseModelMenuGeneratorView(TestCase):

    def test_field_methods(self):

        self.assertIs(
            TestView.get_serializer_fields(),
            CustomFlatMenu.api_fields
        )

        self.assertEqual(
            TestView.get_serializer_field_names(),
            ['handle', 'translated_heading']
        )

        overrides = TestView.get_serializer_field_overrides()
        self.assertIsInstance(overrides, dict)
        self.assertIn('translated_heading', overrides)
        self.assertIsInstance(overrides['translated_heading'], CharField)

    def test_get_serializer_class_create_kwargs(self):
        """
        Typically, no arguements are passed to this method
        """
        result = TestView.get_serializer_class_create_kwargs()
        self.assertEqual(result, {
            'model': CustomFlatMenu,
            'field_names': ['handle', 'translated_heading'],
            'field_serializer_overrides': {'translated_heading': ANY},
        })

    def test_get_serializer_class_create_kwargs_adds_extra_kwargs_to_result(self):
        """
        Subclasses can provide additional kwargs to update the result
        (a bit like View.get_context_data() in Django)
        """
        result = TestView.get_serializer_class_create_kwargs(foo='bar', bar='baz')
        self.assertIn('foo', result)
        self.assertEqual(result['foo'], 'bar')
        self.assertIn('foo', result)
        self.assertEqual(result['bar'], 'baz')

    @patch('wagtailmenus.api.v1.views.make_serializer_class', autospec=True)
    def test_get_serializer_class_use_of_make_serializer_class(self, mocked_method=True):
        """
        This test mocks out make_serializer_class() because we only want to
        check that the view 'calls' it correctly. The workings of
        make_serializer_class() are tested separately elsewhere.
        """

        result = TestView.get_serializer_class()

        # The result of make_serializer_class() should be returned
        self.assertIsInstance(result, Mock)

        # make_serializer_class() should have been called with:
        mocked_method.assert_called_once_with(
            'CustomFlatMenuSerializer',
            serializers.BaseModelMenuSerializer,
            model=CustomFlatMenu,
            field_names=['handle', 'translated_heading'],
            field_serializer_overrides={'translated_heading': ANY},
        )

    @patch('wagtailmenus.api.v1.views.make_serializer_class')
    def test_get_serializer_class_prefers_serializer_class_attribute_if_set(self, mocked_function):
        class TestViewWithSerializerClass(TestView):
            serializer_class = Serializer

        self.assertIs(
            TestViewWithSerializerClass.get_serializer_class(),
            TestViewWithSerializerClass.serializer_class
        )

        # There should be no need to call make_serializer_class()
        # when 'serializer_class' is available
        self.assertFalse(mocked_function.called)
