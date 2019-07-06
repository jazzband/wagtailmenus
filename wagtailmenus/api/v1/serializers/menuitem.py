from rest_framework import fields
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework_recursive.fields import RecursiveField

from wagtail.core.models import Page
from wagtailmenus.models.menuitems import AbstractMenuItem

from .page import PageSerializer


class BaseMenuItemSerializer(serializers.Serializer):
    """
    A mixin to faciliate rendering of a number of different types of menu
    items, including ``MainMenuItem`` or ``FlatMenuItem`` objects (or custom
    variations of those), ``Page`` objects, or even dictionary-like structures
    added by custom hooks or ``MenuPageMixin.modify_submenu_items()`` methods.
    """
    children_serializer_class = None
    page_serializer_class = PageSerializer

    href = fields.CharField(read_only=True)
    text = fields.CharField(read_only=True)
    active_class = fields.CharField(read_only=True)
    page = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    @classmethod
    def get_children_serializer_class(cls):
        if cls.children_serializer_class:
            return cls.children_serializer_class
        return cls

    @classmethod
    def get_page_serializer_class(cls):
        return cls.page_serializer_class

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
        value = self.get_page_value(instance)
        serializer_class = self.get_page_serializer_class()
        return serializer_class(value, context=self.context).data


class BaseModelMenuItemSerializer(BaseMenuItemSerializer, ModelSerializer):
    """
    Used as a base class when dynamically creating serializers for model
    objects with menu-like attributes, including subclasses of
    ``AbstractMainMenuItem`` and ``AbstractFlatMenuItem``, and also for
    ``section_root`` in ``SectionMenuSerializer`` - which is a page object with
    menu-like attributes added.
    """
    pass
