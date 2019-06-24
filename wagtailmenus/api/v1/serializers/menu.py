from rest_framework.serializers import (
    ModelSerializer, Serializer, SerializerMethodField
)

from wagtail.core.models import Page
from wagtailmenus.conf import settings as wagtailmenus_settings

from .menuitem import BaseMenuItemModelSerializer, MenuItemSerializer
from .page import PageSerializer


main_menu_model = wagtailmenus_settings.models.MAIN_MENU_MODEL
flat_menu_model = wagtailmenus_settings.models.FLAT_MENU_MODEL


class MenuSerializerMixin:
    """
    A mixin to faciliate rendering of a number of different types of menu,
    including subclasses of ``AbastractMainMenu`` or ``AbstractFlatMenu``, or
    instances of non-model-based menu classes like ``ChildrenMenu`` or
    ``SectionMenu``.
    """
    item_serializer_base_class = MenuItemSerializer
    item_fields = None
    item_page_fields = None

    def get_items(self, menu_instance):
        serializer_class = self.get_item_serializer_class(menu_instance)
        return serializer_class(
            menu_instance.items, many=True, context=self.context
        ).data

    def get_item_fields(self, menu_instance):
        if self.item_fields is None:
            raise NotImplementedError
        return self.item_fields

    def get_item_page_fields(self, menu_instance):
        if self.item_page_fields is None:
            raise NotImplementedError
        return self.item_page_fields

    def get_item_serializer_class(self, menu_instance):

        base_class = self.item_serializer_base_class

        class PageDrivenMenuItemSerializer(base_class):
            class Meta:
                fields = self.get_item_fields(menu_instance)
                page_serializer_class = self.get_item_page_serializer_class(menu_instance)

        return PageDrivenMenuItemSerializer

    def get_item_page_serializer_class(self, menu_instance):

        class MenuItemPageSerializer(PageSerializer):
            class Meta:
                model = Page
                fields = self.get_item_page_fields(menu_instance)

        return MenuItemPageSerializer


class ModelBasedMenuSerializer(MenuSerializerMixin, ModelSerializer):

    item_serializer_base_class = BaseMenuItemModelSerializer
    items = SerializerMethodField()
    sub_item_fields = None
    sub_item_page_fields = None

    @staticmethod
    def get_item_model_from_menu_instance(menu_instance):
        return menu_instance.get_menu_items_manager().model

    def get_item_serializer_class(self, menu_instance):

        base_class = self.item_serializer_base_class
        item_model = self.get_item_model_from_menu_instance(menu_instance)

        class MenuModelItemSerializer(base_class):
            class Meta:
                model = item_model
                fields = self.get_item_fields(menu_instance, item_model)
                sub_item_fields = self.get_sub_item_fields(menu_instance, item_model)
                page_serializer_class = self.get_item_page_serializer_class(menu_instance, item_model)
                sub_item_page_serializer_class = self.get_sub_item_page_serializer_class(menu_instance, item_model)

        return MenuItemSerializer

    def get_item_fields(self, menu_instance, item_model):
        if self.item_fields is not None:
            return self.item_fields
        return item_model.api_fields

    def get_item_page_fields(self, menu_instance, item_model):
        if self.item_page_fields is not None:
            return self.item_page_fields
        return item_model.page_api_fields

    def get_sub_item_fields(self, menu_instance, item_model):
        if self.sub_item_fields is None:
            return item_model.sub_item_api_fields
        return item_model.sub_item_api_fields

    def get_sub_item_page_fields(self, menu_instance, item_model):
        if self.sub_item_page_fields is None:
            return item_model.sub_item_page_api_fields
        return item_model.sub_item_page_api_fields

    def get_item_page_serializer_class(self, menu_instance, item_model):

        class MenuItemPageSerializer(PageSerializer):
            class Meta:
                model = Page
                fields = self.get_item_page_fields(menu_instance, item_model)

        return MenuItemPageSerializer

    def get_sub_item_page_serializer_class(self, menu_instance, item_model):

        class SubItemPageSerializer(PageSerializer):
            class Meta:
                model = Page
                fields = self.get_sub_item_page_fields(menu_instance, item_model)

        return SubItemPageSerializer


class MainMenuSerializer(ModelBasedMenuSerializer):

    class Meta:
        model = main_menu_model
        fields = main_menu_model.api_fields


class FlatMenuSerializer(ModelBasedMenuSerializer):

    class Meta:
        model = flat_menu_model
        fields = flat_menu_model.api_fields


class ChildrenMenuSerializer(MenuSerializerMixin, Serializer):
    items = SerializerMethodField()
    item_fields = ('text', 'href', 'active_class', 'page', 'children')
    item_page_fields = ('id', 'title', 'slug', 'type')

    parent_page = SerializerMethodField()
    parent_page_fields = ('id', 'title', 'slug', 'type')

    def get_parent_page(self, menu_instance):
        parent_page = menu_instance.parent_page
        serializer_class = self.get_parent_page_serializer_class(parent_page)
        return serializer_class(parent_page, context=self.context).data

    def get_parent_page_serializer_class(self, parent_page):

        class ParentPageSerializer(PageSerializer):
            class Meta:
                model = type(parent_page)
                fields = self.parent_page_fields

        return ParentPageSerializer


class SectionMenuSerializer(MenuSerializerMixin, Serializer):

    items = SerializerMethodField()
    item_fields = ('text', 'href', 'active_class', 'page', 'children')
    item_page_fields = ('id', 'title', 'slug', 'type')

    section_root = SerializerMethodField()
    section_root_serializer_fields = ('id', 'title', 'slug', 'type', 'href', 'active_class')

    def get_section_root(self, instance):
        section_root = instance.root_page
        serializer_class = self.get_section_root_serializer_class(section_root)
        return serializer_class(section_root, context=self.context).data

    def get_section_root_serializer_class(self, section_root):

        class SectionRootSerializer(BaseMenuItemModelSerializer, PageSerializer):
            class Meta:
                model = type(section_root)
                fields = self.section_root_serializer_fields

        return SectionRootSerializer
