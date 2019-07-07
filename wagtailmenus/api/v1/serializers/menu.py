from rest_framework.serializers import (
    ModelSerializer, Serializer, SerializerMethodField
)

from wagtail.core.models import Page
from wagtailmenus.conf import settings as wagtailmenus_settings

from .menuitem import BaseMenuItemSerializer, BaseModelMenuItemSerializer
from .page import PageSerializer


main_menu_model = wagtailmenus_settings.models.MAIN_MENU_MODEL
flat_menu_model = wagtailmenus_settings.models.FLAT_MENU_MODEL


class MenuSerializerMixin:
    """
    A mixin to faciliate rendering of a number of different types of menu,
    including subclasses of ``AbstractMainMenu`` or ``AbstractFlatMenu``, or
    instances of non-model-based menu classes like ``ChildrenMenu`` or
    ``SectionMenu``.
    """
    item_fields = None
    item_serializer_base_class = BaseMenuItemSerializer

    item_page_fields = None
    item_page_serializer_base_class = PageSerializer

    @staticmethod
    def get_item_model(menu_instance):
        """
        If the menu items for ``menu_instance`` are defined using
        an inline model, return that model. Otherwise return ``None``
        """
        try:
            return menu_instance.get_menu_items_manager().model
        except AttributeError:
            return

    def get_items(self, menu_instance):
        serializer_class = self.get_item_serializer_class(
            menu_instance=menu_instance,
            item_model=self.get_item_model(menu_instance)
        )
        return serializer_class(
            menu_instance.items, many=True, context=self.context
        ).data

    def get_item_fields(self, menu_instance, item_model=None):
        if self.item_fields is not None:
            return self.item_fields

        if hasattr(item_model, 'api_fields'):
            return item_model.api_fields

        raise NotImplementedError(
            "Please set the 'item_fields' atrribute on your %s class, "
            "or consider overriding the get_item_fields() method"
            % self.__class__.__name__
        )

    def get_item_page_fields(self, menu_instance, item_model=None):
        if self.item_page_fields is not None:
            return self.item_page_fields

        if hasattr(item_model, 'page_api_fields'):
            return item_model.page_api_fields

        raise NotImplementedError(
            "Please set 'item_page_fields' atrribute on your %s class, "
            "or consider overriding the get_item_page_fields() method"
            % self.__class__.__name__
        )

    def get_item_serializer_class(self, menu_instance, item_model=None):

        class ItemSerializer(self.item_serializer_base_class):

            page_serializer_class = self.get_item_page_serializer_class(
                menu_instance, item_model
            )

            class Meta:
                fields = self.get_item_fields(menu_instance, item_model)

        return ItemSerializer

    def get_item_page_serializer_class(self, menu_instance, item_model=None):

        class ItemPageSerializer(self.item_page_serializer_base_class):

            class Meta:
                model = Page
                fields = self.get_item_page_fields(menu_instance, item_model)

        return ItemPageSerializer


class ModelBasedMenuSerializer(MenuSerializerMixin, ModelSerializer):
    """
    Used to serialize menus that are defined using a model, with an
    inline model to define menu items (for example ``MainMenu`` or
    ``FlatMenu``.
    """

    items = SerializerMethodField()

    item_serializer_base_class = BaseModelMenuItemSerializer

    sub_item_fields = None
    sub_item_serializer_base_class = BaseMenuItemSerializer

    sub_item_page_fields = None
    sub_item_page_serializer_base_class = PageSerializer

    def get_item_serializer_class(self, menu_instance, item_model):
        """
        Menu items are recursively serialized (using the same class for all
        levels) by default, but this won't work for model-based menu
        items, because the sub items are not instances of the same model.

        This class generates a separate serializer class for sub menu items,
        and sets it on the item serializer.
        """
        class ItemSerializer(self.item_serializer_base_class):

            page_serializer_class = self.get_item_page_serializer_class(
                menu_instance, item_model)

            children_serializer_class = self.get_sub_item_serializer_class(
                menu_instance, item_model)

            class Meta:
                model = item_model
                fields = self.get_item_fields(menu_instance, item_model)

        return ItemSerializer

    def get_sub_item_fields(self, menu_instance, item_model):
        if self.sub_item_fields is not None:
            return self.sub_item_fields
        return item_model.sub_item_api_fields

    def get_sub_item_page_fields(self, menu_instance, item_model):
        if self.sub_item_page_fields is not None:
            return self.sub_item_page_fields
        return item_model.sub_item_page_api_fields

    def get_sub_item_serializer_class(self, menu_instance, item_model):

        class SubItemSerializer(self.sub_item_serializer_base_class):

            page_serializer_class = self.get_sub_item_page_serializer_class(
                menu_instance, item_model
            )

            class Meta:
                fields = self.get_sub_item_fields(menu_instance, item_model)

        return SubItemSerializer

    def get_sub_item_page_serializer_class(self, menu_instance, item_model):

        class SubItemPageSerializer(self.sub_item_page_serializer_base_class):

            class Meta:
                model = Page
                fields = self.get_sub_item_page_fields(menu_instance, item_model)

        return SubItemPageSerializer


class MainMenuSerializer(ModelBasedMenuSerializer):
    """
    Used to serialize instances of ``MainMenu``, or some other subclass of
    ``AbastractMenuItem`` if a custom main menu model is being used.
    Menu item data will automatically be drawn from custom menu item
    models if one is being used.
    """

    class Meta:
        model = main_menu_model
        fields = main_menu_model.api_fields


class FlatMenuSerializer(ModelBasedMenuSerializer):
    """
    Used to serialize instances of ``FlatMenu``, or some other subclass of
    ``AbastractMenuItem`` if a custom main menu model is being used.
    Menu item data will automatically be drawn from custom menu item
    models if one is being used.
    """

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

        class SectionRootSerializer(BaseModelMenuItemSerializer, PageSerializer):

            class Meta:
                model = type(section_root)
                fields = self.section_root_serializer_fields

        return SectionRootSerializer
