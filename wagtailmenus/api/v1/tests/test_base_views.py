from django.test import override_settings, TestCase

from wagtailmenus.api.v1.views import BaseMenuGeneratorView
from wagtailmenus.api.v1 import serializers


class TestGetSerializerClass(TestCase):

    def test_prefers_serializer_class_attribute(self):

        class TestView(BaseMenuGeneratorView):
            serializer_class = serializers.MainMenuSerializer
            serializer_class_setting_name = 'CHILDREN_MENU_SERIALIZER'

        self.assertIs(
            TestView.get_serializer_class(),
            TestView.serializer_class
        )

    def test_returns_default_setting_value_if_not_overriden(self):

        class TestView(BaseMenuGeneratorView):
            serializer_class_setting_name = 'CHILDREN_MENU_SERIALIZER'

        self.assertIs(
            TestView.get_serializer_class(),
            serializers.ChildrenMenuSerializer
        )

    @override_settings(WAGTAILMENUS_API_V1_MAIN_MENU_SERIALIZER='wagtailmenus.api.v1.serializers.FlatMenuSerializer')
    def test_returns_custom_serializer_if_setting_is_overridden(self):

        class TestView(BaseMenuGeneratorView):
            serializer_class_setting_name = 'MAIN_MENU_SERIALIZER'

        self.assertIs(
            TestView.get_serializer_class(),
            serializers.FlatMenuSerializer
        )
