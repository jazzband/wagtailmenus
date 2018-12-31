from django.test import override_settings, TestCase

from wagtailmenus.api.v1.views import MenuGeneratorView
from wagtailmenus.api.v1.serializers import FlatMenuSerializer, MainMenuSerializer


class TestGetSerializerClass(TestCase):

    class CustomView(MenuGeneratorView):
        default_serializer_class = MainMenuSerializer
        serializer_class_setting_name = 'MAIN_MENU_SERIALIZER'

    view_class = CustomView

    def test_returns_default_serializer_by_default(self):
        view = self.view_class()
        result = view.get_serializer_class()
        self.assertEqual(result, view.default_serializer_class)

    def test_returns_serializer_class_attribute_value_is_set(self):
        view = self.view_class()
        view.serializer_class = FlatMenuSerializer
        result = view.get_serializer_class()
        self.assertEqual(result, FlatMenuSerializer)
        view.serializer_class = None

    @override_settings(WAGTAILMENUS_API_V1_MAIN_MENU_SERIALIZER='wagtailmenus.api.v1.serializers.FlatMenuSerializer')
    def test_returns_default_setting_override_serializer_if_specified(self):
        view = self.view_class()
        result = view.get_serializer_class()
        self.assertEqual(result, FlatMenuSerializer)
