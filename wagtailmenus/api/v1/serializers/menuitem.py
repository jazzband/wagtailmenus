from rest_framework import fields
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework_recursive.fields import RecursiveField

from wagtail.core.models import Page
from wagtailmenus.models.menuitems import AbstractMenuItem

from .page import PageSerializer


class MenuItemSerializer(serializers.Serializer):
    """
    A mixin to faciliate rendering of a number of different types of menu
    items, including ``MainMenuItem`` or ``FlatMenuItem`` objects (or custom
    variations of those), ``Page`` objects, or even dictionary-like structures
    added by custom hooks or ``MenuPageMixin.modify_submenu_items()`` methods.
    """
    href = fields.CharField(read_only=True)
    text = fields.CharField(read_only=True)
    active_class = fields.CharField(read_only=True)
    page = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    @classmethod
    def get_children_serializer_class(cls):
        return cls

    @classmethod
    def get_page_serializer_class(cls):
        return cls.Meta.page_serializer_class

    def get_children_value(self, instance):
        if getattr(instance, 'sub_menu', None):
            return instance.sub_menu.items
        return ()

    def get_children(self, instance):
        value = self.get_children_value(instance)
        if not value:
            return value
        serializer_class = self.get_children_serializer_class()
        return serializer_class(value, many=True, context=self.context).data

    def get_page_value(self, instance):
        if isinstance(instance, Page):
            return instance
        if isinstance(instance, AbstractMenuItem):
            return instance.link_page

    def get_page(self, instance):
        page = self.get_page_value(instance)
        serializer_class = self.get_page_serializer_class()
        return serializer_class(page, context=self.context).data


class BaseMenuItemModelSerializer(MenuItemSerializer, ModelSerializer):
    """
    Used as a base class when dynamically creating serializers for model
    objects with menu-like attributes, including subclasses of
    ``AbstractMainMenuItem`` and ``AbstractFlatMenuItem``, and also for
    ``section_root`` in ``SectionMenuSerializer`` - which is a page object with
    menu-like attributes added.
    """

    @classmethod
    def get_children_serializer_class(cls):

        class SubMenuItemSerializer(MenuItemSerializer):
            class Meta:
                fields = cls.Meta.sub_item_fields
                page_serializer_class = cls.Meta.sub_item_page_serializer_class

        return SubMenuItemSerializer
