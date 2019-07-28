from rest_framework import serializers

from wagtail.core.models import Page
from wagtailmenus.conf import settings as wagtailmenus_settings
from wagtailmenus.api.utils import make_serializer_class

from .menuitem import BaseMenuItemSerializer, BaseModelMenuItemSerializer
from .page import PageSerializer


main_menu_model = wagtailmenus_settings.models.MAIN_MENU_MODEL
flat_menu_model = wagtailmenus_settings.models.FLAT_MENU_MODEL


class MenuSerializerMixin:
    """
    A mixin to faciliate serialization of all types of menu.
    """

    # Subclasses can use the following attributes to customise
    # serialization of menu items, instead of updating the relevant
    # attributes on the MenuItem model or Menu class.
    item_fields = None
    base_item_page_serializer_class = PageSerializer

    item_page_fields = None
    base_item_serializer_class = BaseMenuItemSerializer

    # -----------------------------------------------------------------------------
    # item serializer
    # -----------------------------------------------------------------------------

    @classmethod
    def get_item_fields(cls, item_model, menu_instance):
        if cls.item_fields is not None:
            return cls.item_fields

        if hasattr(item_model, 'api_fields'):
            return item_model.api_fields

        if hasattr(menu_instance, 'item_api_fields'):
            return menu_instance.item_api_fields

    @classmethod
    def get_item_field_names(cls, item_model, menu_instance):
        return [
            field.name for field in
            cls.get_item_fields(item_model, menu_instance)
        ]

    @classmethod
    def get_item_field_serializer_overrides(cls, item_model, menu_instance):
        return {
            field.name: field.serializer for field in
            cls.get_item_fields(item_model, menu_instance)
            if field.serializer is not None
        }

    @classmethod
    def get_item_serializer_init_kwargs(cls, base_class, item_model, menu_instance, **kwargs):
        """
        Subclasses can add new or update values by providing them as 'kwargs'
        when calling super().get_item_serializer_init_kwargs().
        """
        values = {
            'model': item_model,
            'field_names': cls.get_item_field_names(item_model, menu_instance),
            'field_serializer_overrides': cls.get_item_field_serializer_overrides(item_model, menu_instance),
            'page_serializer_class': cls.get_item_page_serializer_class(item_model, menu_instance)
        }
        values.update(kwargs)
        return values

    @classmethod
    def get_item_serializer_class(cls, item_model, menu_instance):
        base_class = cls.base_item_serializer_class
        init_kwargs = cls.get_item_serializer_init_kwargs(base_class, item_model, menu_instance)
        return make_serializer_class('SubItemSerializer', base_class, **init_kwargs)

    # -----------------------------------------------------------------------------
    # item page serializer
    # -----------------------------------------------------------------------------

    @classmethod
    def get_item_page_fields(cls, item_model, menu_instance):
        if cls.item_page_fields is not None:
            return cls.item_page_fields

        if hasattr(item_model, 'page_api_fields'):
            return item_model.page_api_fields

        if hasattr(menu_instance, 'item_page_api_fields'):
            return menu_instance.item_page_api_fields

    @classmethod
    def get_item_page_field_names(cls, item_model, menu_instance):
        return [
            field.name for field in
            cls.get_item_page_fields(item_model, menu_instance)
        ]

    @classmethod
    def get_item_page_field_serializer_overrides(cls, item_model, menu_instance):
        return {
            field.name: field.serializer
            for field in cls.get_item_page_fields(item_model, menu_instance)
            if field.serializer is not None
        }

    @classmethod
    def get_item_page_serializer_init_kwargs(cls, base_class, item_model, menu_instance, **kwargs):
        """
        Subclasses can add new or update values by providing them as 'kwargs'
        when calling super().get_item_page_serializer_init_kwargs().
        """
        values = {
            'model': Page,
            'field_names': cls.get_item_page_field_names(item_model, menu_instance),
            'field_serializer_overrides': cls.get_item_page_field_serializer_overrides(item_model, menu_instance),
        }
        values.update(kwargs)
        return values

    @classmethod
    def get_item_page_serializer_class(cls, item_model, menu_instance):
        base_class = cls.base_item_page_serializer_class
        init_kwargs = cls.get_item_page_serializer_init_kwargs(base_class, item_model, menu_instance)
        return make_serializer_class('SubItemPageSerializer', base_class, **init_kwargs)

    def get_items(self, menu_instance):

        item_model = None
        if hasattr(menu_instance, 'get_menu_items_manager'):
            # this is a model-based menu with inline/child menu items
            item_model = menu_instance.get_menu_items_manager().model

        cls = self.get_item_serializer_class(item_model, menu_instance)
        return cls(menu_instance.items, many=True, context=self.context).data


class BaseModelMenuSerializer(MenuSerializerMixin, serializers.ModelSerializer):
    """
    Used to serialize menus that are defined using a model, with an
    inline (or child) model to define menu items (for example ``MainMenu``
    or ``FlatMenu``.

    Because menu item model have unique fields that need serializing, and
    can be swapped out for a custom models with even more unique fields,
    this class defines a separate pair of serializers are to handle
    serialization for sub-level items and their 'page' fields.
    """
    items = serializers.SerializerMethodField()

    # base serializer classes overrides
    base_item_serializer_class = BaseModelMenuItemSerializer
    base_sub_item_serializer = BaseMenuItemSerializer

    # Subclasses can use the following attributes to customise
    # serialization of sub-level items instead of updating
    # 'sub_item_api_fields'  and 'sub_item_page_api_fields'
    # attributes on the menu item model
    sub_item_fields = None
    sub_item_page_fields = None

    # Leave as `None` to reuse `base_item_page_serializer` for all levels
    base_sub_item_page_serializer = None

    # -----------------------------------------------------------------------------
    # item serializer
    # -----------------------------------------------------------------------------

    @classmethod
    def get_item_serializer_init_kwargs(cls, base_class, item_model, menu_instance, **kwargs):
        """
        Overrides MenuSerializerMixin.get_item_serializer_init_kwargs() to set
        the 'children_serializer_class' attribute on the serializer used for
        top-level items.

        Subclasses can add new or update values by providing them as 'kwargs'
        when calling super().get_item_serializer_init_kwargs().
        """
        values = {
            'children_serializer_class': cls.get_sub_item_serializer_class(item_model, menu_instance)
        }
        values.update(kwargs)
        return super().get_item_serializer_init_kwargs(base_class, item_model, menu_instance, **values)

    # -----------------------------------------------------------------------------
    # sub_item
    # -----------------------------------------------------------------------------

    @classmethod
    def get_sub_item_fields(cls, item_model, menu_instance):
        if cls.sub_item_fields is not None:
            return cls.sub_item_fields

        # Default values are defined on `AbstractMenuItem`, so should
        # be present on default or custom menu item classes
        return item_model.sub_item_api_fields

    @classmethod
    def get_sub_item_field_names(cls, item_model, menu_instance):
        return [
            field.name for field in cls.get_sub_item_fields(item_model, menu_instance)
        ]

    @classmethod
    def get_sub_item_field_serializer_overrides(cls, item_model, menu_instance):
        return {
            field.name: field.serializer for field in
            cls.get_sub_item_fields(item_model, menu_instance)
            if field.serializer is not None
        }

    @classmethod
    def get_sub_item_serializer_init_kwargs(cls, base_class, item_model, menu_instance, **kwargs):
        """
        Subclasses can add new or update values by providing them as 'kwargs'
        when calling super().get_item_serializer_init_kwargs().

        NOTE: A 'sub item' is almost always a ``Page`` object, but wagtailmenus
        allows custom menu items to be added via hooks or custom ``MenuPage``
        methods, which might be defined as dicts or other custom types. Because
        of this, this serializer will be a basic ``Serializer`` (instead of
        a ``ModelSerializer``). If the menu item IS a ``Page`` object,
        additional data for that page will be surfaced in a separate 'page'
        field, which DOES use a ``ModelSerializer``, and can be made to
        output custom page fields if neccessary.
        """
        values = {
            'field_names': cls.get_sub_item_field_names(item_model, menu_instance),
            'field_serializer_overrides': cls.get_sub_item_field_serializer_overrides(item_model, menu_instance),
            'page_serializer_class': cls.get_sub_item_page_serializer_class(item_model, menu_instance)
        }
        values.update(kwargs)
        return values

    @classmethod
    def get_sub_item_serializer_class(cls, item_model, menu_instance):
        base_class = cls.base_sub_item_serializer
        init_kwargs = cls.get_sub_item_serializer_init_kwargs(base_class, item_model, menu_instance)
        return make_serializer_class('SubItemSerializer', base_class, **init_kwargs)

    # -----------------------------------------------------------------------------
    # sub_item_page
    # -----------------------------------------------------------------------------

    @classmethod
    def get_sub_item_page_fields(cls, item_model, menu_instance):
        if cls.sub_item_page_fields is not None:
            return cls.sub_item_page_fields

        # Default values are defined on `AbstractMenuItem`, so should
        # be present on default or custom menu item classes
        return item_model.sub_item_page_api_fields

    @classmethod
    def get_sub_item_page_field_names(cls, item_model, menu_instance):
        return [
            field.name for field in cls.get_sub_item_page_fields(item_model, menu_instance)
        ]

    @classmethod
    def get_sub_item_page_field_serializer_overrides(cls, item_model, menu_instance):
        return {
            field.name: field.serializer for field in
            cls.get_sub_item_page_fields(item_model, menu_instance)
            if field.serializer is not None
        }

    @classmethod
    def get_sub_item_page_serializer_init_kwargs(cls, base_class, item_model, menu_instance, **kwargs):
        """
        Subclasses can add new or update values by providing them as 'kwargs'
        when calling super().get_item_serializer_init_kwargs().
        """
        values = {
            'model': Page,
            'field_names': cls.get_sub_item_page_field_names(item_model, menu_instance),
            'field_serializer_overrides': cls.get_sub_item_page_field_serializer_overrides(item_model, menu_instance),
        }
        values.update(kwargs)
        return values

    @classmethod
    def get_sub_item_page_serializer_class(cls, item_model, menu_instance):
        base_class = cls.base_sub_item_page_serializer or cls.base_item_page_serializer_class
        init_kwargs = cls.get_sub_item_page_serializer_init_kwargs(base_class, item_model, menu_instance)
        return make_serializer_class('SubItemPageSerializer', base_class, **init_kwargs)


class ChildrenMenuSerializer(MenuSerializerMixin, serializers.Serializer):

    items = serializers.SerializerMethodField()
    parent_page = serializers.SerializerMethodField()

    # Subclasses can use the following attributes to customise
    # serialization of 'parent_page' instead of updating the
    # `parent_page_api_fields` attribute on the menu class
    base_parent_page_serializer = PageSerializer
    parent_page_fields = None

    @classmethod
    def get_parent_page_fields(cls, parent_page, menu_instance):
        if cls.parent_page_fields:
            return cls.parent_page_field

        # Default values are defined on `ChildrenMenu`, so should
        # be present on default or custom menu classes
        return menu_instance.parent_page_api_fields

    @classmethod
    def get_parent_page_field_names(cls, parent_page, menu_instance):
        return [
            field.name for field in cls.get_parent_page_fields(parent_page, menu_instance)
        ]

    @classmethod
    def get_parent_page_serializer_overrides(cls, parent_page, menu_instance):
        return {
            field.name: field.serializer for field in
            cls.get_parent_page_fields(parent_page, menu_instance)
            if field.serializer is not None
        }

    @classmethod
    def get_parent_page_serializer_init_kwargs(cls, base_class, parent_page, menu_instance, **kwargs):
        """
        Subclasses can add new or update values by providing them as 'kwargs'
        when calling super().get_parent_page_serializer_init_kwargs().
        """
        values = {
            'model': type(parent_page),
            'field_names': cls.get_parent_page_field_names(parent_page, menu_instance),
            'field_serializer_overrides': cls.get_parent_page_serializer_overrides(parent_page, menu_instance),
        }
        values.update(kwargs)
        return values

    @classmethod
    def get_parent_page_serializer_class(cls, parent_page, menu_instance):
        base_class = cls.base_parent_page_serializer
        init_kwargs = cls.get_parent_page_serializer_init_kwargs(base_class, parent_page, menu_instance)
        return make_serializer_class('ParentPageSerializer', base_class, **init_kwargs)

    def get_parent_page(self, menu_instance):
        parent_page = menu_instance.parent_page
        serializer_class = self.get_parent_page_serializer_class(parent_page, menu_instance)
        return serializer_class(parent_page, context=self.context).data


class SectionMenuSerializer(MenuSerializerMixin, serializers.Serializer):

    items = serializers.SerializerMethodField()
    section_root = serializers.SerializerMethodField()

    # Subclasses can use the following attributes to customise
    # serialization of 'section_root' instead of updating the
    # `section_root_api_fields` attribute on the menu class
    base_section_root_serializer = PageSerializer
    section_root_fields = None

    @classmethod
    def get_section_root_fields(cls, section_root_page, menu_instance):
        if cls.section_root_fields:
            return cls.section_root_fields

        # Default values are defined on `SectionMenu`, so should
        # be present on default or custom menu classes
        return menu_instance.section_root_api_fields

    @classmethod
    def get_section_root_field_names(cls, section_root_page, menu_instance):
        return [
            field.name for field in cls.get_section_root_fields(section_root_page, menu_instance)
        ]

    @classmethod
    def get_section_root_serializer_overrides(cls, section_root_page, menu_instance):
        return {
            field.name: field.serializer for field in
            cls.get_section_root_fields(section_root_page, menu_instance)
            if field.serializer is not None
        }

    @classmethod
    def get_section_root_serializer_init_kwargs(cls, base_class, section_root_page, menu_instance, **kwargs):
        """
        Subclasses can add new or update values by providing them as 'kwargs'
        when calling super().get_section_root_serializer_init_kwargs().
        """
        values = {
            'model': type(section_root_page),
            'field_names': cls.get_section_root_field_names(section_root_page, menu_instance),
            'field_serializer_overrides': cls.get_section_root_serializer_overrides(section_root_page, menu_instance),
        }
        values.update(kwargs)
        return values

    @classmethod
    def get_section_root_serializer_class(cls, section_root_page, menu_instance):
        base_class = cls.base_section_root_serializer
        init_kwargs = cls.get_section_root_serializer_init_kwargs(base_class, section_root_page, menu_instance)
        return make_serializer_class('SectionRootSerializer', base_class, **init_kwargs)

    def get_section_root(self, menu_instance):
        section_root_page = menu_instance.root_page
        serializer_class = self.get_section_root_serializer_class(section_root_page, menu_instance)
        return serializer_class(section_root_page, context=self.context).data
