from rest_framework.serializers import (
    ModelSerializer, Serializer, SerializerMethodField
)

from wagtailmenus.conf import settings as wagtailmenus_settings

from .menuitem import BaseMenuItemModelSerializer, RecursiveMenuItemSerializer
from .page import BasePageSerializer
from .util import ContextSpecificFieldsMixin


main_menu_model = wagtailmenus_settings.models.MAIN_MENU_MODEL
flat_menu_model = wagtailmenus_settings.models.FLAT_MENU_MODEL


class MenuSerializerMixin(ContextSpecificFieldsMixin):
    """
    A mixin to faciliate rendering of a number of different types of menu,
    including subclasses of ``AbastractMainMenu`` or ``AbstractFlatMenu``, or
    instances of non-model-based menu classes like ``ChildrenMenu`` or
    ``SectionMenu``.
    """
    items_serializer_class = None
    items_serializer_fields = None
    items_serializer_page_fields = None

    def get_items(self, menu_instance):
        serializer_class = self.get_items_serializer_class(menu_instance)
        return serializer_class(
            menu_instance.items, many=True, read_only=True, context=self.context
        )

    def get_items_serializer_class(self, menu_instance):
        if self.items_serializer_class is None:
            raise NotImplementedError
        return self.items_serializer_class

    def get_items_serializer_fields(self, menu_instance):
        if self.items_serializer_fields is not None:
            return self.items_serializer_fields
        if hasattr(menu_instance, 'get_menu_items_manager'):
            model = menu_instance.get_menu_items_manager().model
            return model.api_fields
        return menu_instance.item_api_fields

    def get_items_serializer_page_fields(self, menu_instance):
        if self.items_serializer_page_fields is not None:
            return self.items_serializer_page_fields
        if hasattr(menu_instance, 'get_menu_items_manager'):
            model = menu_instance.get_menu_items_manager().model
            return model.page_api_fields
        return menu_instance.item_page_api_fields

    def get_items_serializer_init_kwargs(self, instance):
        return self.items_serializer_init_kwargs


class MainMenuSerializer(MenuSerializerMixin, ModelSerializer):

    items = SerializerMethodField()

    class Meta:
        model = main_menu_model
        fields = main_menu_model.api_fields

    def get_items_serializer_class(self, instance):

        class MainMenuItemSerializer(BaseMenuItemModelSerializer):
            class Meta:
                model = instance.get_menu_items_manager().model
                fields = self.get_items_serializer_fields(instance)
                page_fields = self.get_items_serializer_page_fields(instance)

        return MainMenuItemSerializer


class FlatMenuSerializer(MenuSerializerMixin, ModelSerializer):

    items = SerializerMethodField()

    class Meta:
        model = flat_menu_model
        fields = flat_menu_model.api_fields

    def get_items_serializer_class(self, instance):

        class FlatMenuItemSerializer(BaseMenuItemModelSerializer):
            class Meta:
                model = instance.get_menu_items_manager().model
                fields = self.get_items_serializer_fields(instance)
                page_fields = self.get_items_serializer_page_fields(instance)

        return FlatMenuItemSerializer


class ChildrenMenuSerializer(MenuSerializerMixin, Serializer):

    parent_page = SerializerMethodField()
    items = SerializerMethodField()

    items_serializer_fields = ('text', 'href', 'active_class', 'page', 'children')
    items_serializer_page_fields = ('id', 'title', 'slug', 'type')
    parent_page_serializer_fields = ('id', 'title', 'slug', 'type')

    def get_parent_page(self, menu_instance):
        parent_page = menu_instance.parent_page
        serializer_class = self.get_parent_page_serializer_class(parent_page)
        return serializer_class(parent_page, read_only=True)

    def get_parent_page_serializer_class(self, parent_page):

        class ParentPageSerializer(BasePageSerializer):
            class Meta:
                model = type(parent_page)
                fields = self.parent_page_serializer_fields

        return ParentPageSerializer

    def get_items_serializer_class(self, instance):

        class ChildrenMenuItemSerializer(RecursiveMenuItemSerializer):
            class Meta:
                fields = self.get_items_serializer_fields(instance)
                page_fields = self.get_items_serializer_page_fields(instance)

        return ChildrenMenuItemSerializer


class SectionMenuSerializer(MenuSerializerMixin, Serializer):

    section_root = SerializerMethodField()
    items = SerializerMethodField()

    items_serializer_fields = ('text', 'href', 'active_class', 'page', 'children')
    items_serializer_page_fields = ('id', 'title', 'slug', 'type')
    section_root_serializer_fields = ('id', 'title', 'slug', 'type', 'href', 'active_class')

    def get_section_root(self, instance):
        section_root = instance.root_page
        serializer_class = self.get_section_root_serializer_class(section_root)
        return serializer_class(section_root, read_only=True)

    def get_section_root_serializer_class(self, section_root):

        class SectionRootSerializer(BaseMenuItemModelSerializer, BasePageSerializer):
            class Meta:
                model = type(section_root)
                fields = self.section_root_serializer_fields

        return SectionRootSerializer

    def get_items_serializer_class(self, instance):

        class SectionMenuItemSerializer(RecursiveMenuItemSerializer):
            class Meta:
                fields = self.get_items_serializer_fields(instance)
                page_fields = self.get_items_serializer_page_fields(instance)

        return SectionMenuItemSerializer
