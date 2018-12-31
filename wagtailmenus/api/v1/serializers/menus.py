from rest_framework import fields
from rest_framework.serializers import ModelSerializer, Serializer

from wagtailmenus.conf import settings as wagtailmenus_settings
from wagtailmenus.api.v1.conf import settings as api_settings

from .menuitems import BaseMenuItemModelSerializer, RecursiveMenuItemSerializer
from .pages import BasePageSerializer
from .utils import ContextSpecificFieldsMixin


main_menu_model = wagtailmenus_settings.models.MAIN_MENU_MODEL
flat_menu_model = wagtailmenus_settings.models.FLAT_MENU_MODEL


class MenuSerializerMixin(ContextSpecificFieldsMixin):
    """
    A mixin to faciliate rendering of a number of different types of menu,
    including subclasses of ``AbastractMainMenu`` or ``AbstractFlatMenu``, or
    instances of non-model-based menu classes like ``ChildrenMenu`` or
    ``SectionMenu``.
    """

    item_fields_setting_name = None
    item_page_fields_setting_name = None

    items_field_init_kwargs = {
        'many': True,
        'read_only': True,
    }

    def update_fields(self, fields, instance, context):
        super().update_fields(fields, instance, context)
        if 'items' in fields:
            self.replace_items_field(instance)

    def replace_items_field(self, instance):
        field_class = self.get_items_serializer_class(instance)
        init_kwargs = self.get_items_serializer_init_kwargs(instance)
        self.fields['items'] = field_class(**init_kwargs)

    def get_items_serializer_class(self, instance):
        raise NotImplementedError

    def get_items_serializer_fields(self, instance):
        if self.item_fields_setting_name is None:
            raise NotImplementedError
        field_list = api_settings.get(self.item_fields_setting_name)
        if field_list is not None:
            return field_list
        if hasattr(instance, 'get_menu_items_manager'):
            model = instance.get_menu_items_manager().model
            return model.api_fields
        return instance.item_api_fields

    def get_item_page_serializer_fields(self, instance):
        if self.item_page_fields_setting_name is None:
            raise NotImplementedError
        field_list = api_settings.get(self.item_page_fields_setting_name)
        if field_list is not None:
            return field_list
        if hasattr(instance, 'get_menu_items_manager'):
            model = instance.get_menu_items_manager().model
            return model.page_api_fields
        return instance.item_page_api_fields

    def get_items_serializer_init_kwargs(self, instance):
        return self.items_field_init_kwargs


class MainMenuSerializer(MenuSerializerMixin, ModelSerializer):

    item_fields_setting_name = 'MAIN_MENU_ITEM_SERIALIZER_FIELDS'
    item_page_fields_setting_name = 'MAIN_MENU_ITEM_PAGE_SERIALIZER_FIELDS'

    # Placeholder fields
    items = fields.ListField()

    class Meta:
        model = main_menu_model
        fields = main_menu_model.api_fields

    def get_items_serializer_class(self, instance):
        if api_settings.MAIN_MENU_ITEM_SERIALIZER:
            return api_settings.objects.MAIN_MENU_ITEM_SERIALIZER

        class DefaultMainMenuItemSerializer(BaseMenuItemModelSerializer):
            class Meta:
                model = instance.get_menu_items_manager().model
                fields = self.get_items_serializer_fields(instance)
                page_fields = self.get_item_page_serializer_fields(instance)

        return DefaultMainMenuItemSerializer


class FlatMenuSerializer(MenuSerializerMixin, ModelSerializer):

    item_fields_setting_name = 'FLAT_MENU_ITEM_SERIALIZER_FIELDS'
    item_page_fields_setting_name = 'FLAT_MENU_ITEM_PAGE_SERIALIZER_FIELDS'

    # Placeholder fields
    items = fields.ListField()

    class Meta:
        model = flat_menu_model
        fields = flat_menu_model.api_fields

    def get_items_serializer_class(self, instance):
        if api_settings.FLAT_MENU_ITEM_SERIALIZER:
            return api_settings.objects.FLAT_MENU_ITEM_SERIALIZER

        class DefaultFlatMenuItemSerializer(BaseMenuItemModelSerializer):
            class Meta:
                model = instance.get_menu_items_manager().model
                fields = self.get_items_serializer_fields(instance)
                page_fields = self.get_item_page_serializer_fields(instance)

        return DefaultFlatMenuItemSerializer


class ChildrenMenuSerializer(MenuSerializerMixin, Serializer):

    item_fields_setting_name = 'CHILDREN_MENU_ITEM_SERIALIZER_FIELDS'
    item_page_fields_setting_name = 'CHILDREN_MENU_ITEM_PAGE_SERIALIZER_FIELDS'

    # Placeholder fields
    parent_page = fields.DictField()
    items = fields.ListField()

    parent_page_field_init_kwargs = {
        'read_only': True,
    }

    def update_fields(self, fields, instance, context):
        super().update_fields(fields, instance, context)
        if 'parent_page' in fields:
            self.replace_parent_page_field(instance)

    def replace_parent_page_field(self, instance):
        field_class = self.get_parent_page_serializer_class(instance)
        init_kwargs = self.get_parent_page_serializer_init_kwargs(instance)
        self.fields['parent_page'] = field_class(**init_kwargs)

    def get_items_serializer_class(self, instance):
        if api_settings.CHILDREN_MENU_ITEM_SERIALIZER:
            return api_settings.objects.CHILDREN_MENU_ITEM_SERIALIZER

        class ChildrenMenuItemSerializer(RecursiveMenuItemSerializer):
            class Meta:
                fields = self.get_items_serializer_fields(instance)
                page_fields = self.get_item_page_serializer_fields(instance)

        return ChildrenMenuItemSerializer

    def get_parent_page_serializer_class(self, instance):
        if api_settings.PARENT_PAGE_SERIALIZER:
            return api_settings.objects.PARENT_PAGE_SERIALIZER

        class DefaultParentPageSerializer(BasePageSerializer):
            class Meta:
                model = type(instance.parent_page)
                fields = self.get_parent_page_serializer_fields(instance)

        return DefaultParentPageSerializer

    def get_parent_page_serializer_fields(self, instance):
        field_list = api_settings.PARENT_PAGE_SERIALIZER_FIELDS
        if field_list is not None:
            return field_list
        return instance.parent_page_api_fields

    def get_parent_page_serializer_init_kwargs(self, instance):
        return self.parent_page_field_init_kwargs


class SectionMenuSerializer(MenuSerializerMixin, Serializer):

    item_fields_setting_name = 'SECTION_MENU_ITEM_SERIALIZER_FIELDS'
    item_page_fields_setting_name = 'SECTION_MENU_ITEM_PAGE_SERIALIZER_FIELDS'

    # Placeholder fields
    section_root = fields.DictField()
    items = fields.ListField()

    section_root_field_init_kwargs = {
        'read_only': True,
        'source': 'root_page',
    }

    def update_fields(self, fields, instance, context):
        super().update_fields(fields, instance, context)
        if 'section_root' in fields:
            self.replace_section_root_field(instance)

    def replace_section_root_field(self, instance):
        field_class = self.get_section_root_serializer_class(instance)
        init_kwargs = self.get_section_root_serializer_init_kwargs(instance)
        self.fields['section_root'] = field_class(**init_kwargs)

    def get_items_serializer_class(self, instance):
        if api_settings.SECTION_MENU_ITEM_SERIALIZER:
            return api_settings.objects.SECTION_MENU_ITEM_SERIALIZER

        class SectionMenuItemSerializer(RecursiveMenuItemSerializer):
            class Meta:
                fields = self.get_items_serializer_fields(instance)
                page_fields = self.get_item_page_serializer_fields(instance)

        return SectionMenuItemSerializer

    def get_section_root_serializer_class(self, instance):
        if api_settings.SECTION_ROOT_SERIALIZER:
            return api_settings.objects.SECTION_ROOT_SERIALIZER

        class DefaultSectionRootSerializer(BaseMenuItemModelSerializer, BasePageSerializer):

            class Meta:
                model = type(instance.root_page)
                fields = self.get_section_root_serializer_fields(instance)

        return DefaultSectionRootSerializer

    def get_section_root_serializer_fields(self, instance):
        field_list = api_settings.SECTION_ROOT_SERIALIZER_FIELDS
        if field_list is not None:
            return field_list
        return instance.section_root_api_fields

    def get_section_root_serializer_init_kwargs(self, instance):
        return self.section_root_field_init_kwargs
