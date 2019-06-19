from rest_framework import fields
from rest_framework.serializers import ModelSerializer, Serializer

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
    items_serializer_init_kwargs = {
        'many': True,
        'read_only': True,
    }
    items_serializer_fields = None
    items_serializer_page_fields = None

    def update_fields(self, fields, instance, context):
        super().update_fields(fields, instance, context)
        if 'items' in fields:
            self.replace_items_field(instance)

    def replace_items_field(self, instance):
        field_class = self.get_items_serializer_class(instance)
        init_kwargs = self.get_items_serializer_init_kwargs(instance)
        self.fields['items'] = field_class(**init_kwargs)

    def get_items_serializer_class(self, instance):
        if self.items_serializer_class is None:
            raise NotImplementedError
        return self.items_serializer_class

    def get_items_serializer_fields(self, instance):
        if self.items_serializer_fields is not None:
            return self.items_serializer_fields
        if hasattr(instance, 'get_menu_items_manager'):
            model = instance.get_menu_items_manager().model
            return model.api_fields
        return instance.item_api_fields

    def get_items_serializer_page_fields(self, instance):
        if self.items_serializer_page_fields is not None:
            return self.items_serializer_page_fields
        if hasattr(instance, 'get_menu_items_manager'):
            model = instance.get_menu_items_manager().model
            return model.page_api_fields
        return instance.item_page_api_fields

    def get_items_serializer_init_kwargs(self, instance):
        return self.items_serializer_init_kwargs


class MainMenuSerializer(MenuSerializerMixin, ModelSerializer):

    items = fields.ListField()  # placeholder

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

    items = fields.ListField() # placeholder

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

    # Placeholder fields
    parent_page = fields.DictField()
    items = fields.ListField()

    parent_page_serializer_init_kwargs = {'read_only': True}
    parent_page_serializer_fields = ('id', 'title', 'slug', 'type')

    items_serializer_fields = ('text', 'href', 'active_class', 'page', 'children')
    items_serializer_page_fields = ('id', 'title', 'slug', 'type')

    def update_fields(self, fields, instance, context):
        super().update_fields(fields, instance, context)
        if 'parent_page' in fields:
            self.replace_parent_page_field(instance)

    def replace_parent_page_field(self, instance):
        field_class = self.get_parent_page_serializer_class(instance)
        init_kwargs = self.get_parent_page_serializer_init_kwargs(instance)
        self.fields['parent_page'] = field_class(**init_kwargs)

    def get_parent_page_serializer_class(self, instance):

        class ParentPageSerializer(BasePageSerializer):
            class Meta:
                model = type(instance.parent_page)
                fields = self.get_parent_page_serializer_fields(instance)

        return ParentPageSerializer

    def get_parent_page_serializer_fields(self, instance):
        return self.parent_page_serializer_fields

    def get_parent_page_serializer_init_kwargs(self, instance):
        return self.parent_page_serializer_init_kwargs

    def get_items_serializer_class(self, instance):

        class ChildrenMenuItemSerializer(RecursiveMenuItemSerializer):
            class Meta:
                fields = self.get_items_serializer_fields(instance)
                page_fields = self.get_items_serializer_page_fields(instance)

        return ChildrenMenuItemSerializer


class SectionMenuSerializer(MenuSerializerMixin, Serializer):

    # Placeholder fields
    section_root = fields.DictField()
    items = fields.ListField()

    section_root_serializer_init_kwargs = {
        'read_only': True,
        'source': 'root_page',
    }
    section_root_serializer_fields = ('id', 'title', 'slug', 'type', 'href', 'active_class')

    items_serializer_fields = ('text', 'href', 'active_class', 'page', 'children')
    items_serializer_page_fields = ('id', 'title', 'slug', 'type')

    def update_fields(self, fields, instance, context):
        super().update_fields(fields, instance, context)
        if 'section_root' in fields:
            self.replace_section_root_field(instance)

    def replace_section_root_field(self, instance):
        field_class = self.get_section_root_serializer_class(instance)
        init_kwargs = self.get_section_root_serializer_init_kwargs(instance)
        self.fields['section_root'] = field_class(**init_kwargs)

    def get_section_root_serializer_class(self, instance):

        class SectionRootSerializer(BaseMenuItemModelSerializer, BasePageSerializer):
            class Meta:
                model = type(instance.root_page)
                fields = self.get_section_root_serializer_fields(instance)

        return SectionRootSerializer

    def get_section_root_serializer_fields(self, instance):
        return self.section_root_serializer_fields

    def get_section_root_serializer_init_kwargs(self, instance):
        return self.section_root_field_init_kwargs

    def get_items_serializer_class(self, instance):
        class SectionMenuItemSerializer(RecursiveMenuItemSerializer):
            class Meta:
                fields = self.get_items_serializer_fields(instance)
                page_fields = self.get_items_serializer_page_fields(instance)

        return SectionMenuItemSerializer
