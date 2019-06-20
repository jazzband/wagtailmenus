from rest_framework import fields
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework_recursive.fields import RecursiveField

from wagtail.core.models import Page
from wagtailmenus.models.menuitems import AbstractMenuItem

from .page import BasePageSerializer
from .util import ContextSpecificFieldsMixin


class MenuItemSerializerMixin(ContextSpecificFieldsMixin):
    """
    A mixin to faciliate rendering of a number of different types of menu
    items, including ``MainMenuItem`` or ``FlatMenuItem`` objects (or custom
    variations of those), ``Page`` objects, or even dictionary-like structures
    added by custom hooks or ``MenuPageMixin.modify_submenu_items()`` methods.
    """
    children_serializer_class = RecursiveField

    def get_children(self, instance):
        value = self.get_children_value(instance)
        serializer_class = self.children_serializer_class
        return serializer_class(value, many=True, context=self.context)

    def get_children_value(self, instance):
        if getattr(instance, 'sub_menu', None):
            return instance.sub_menu.items
        return ()

    def get_page(self, instance):
        value = self.get_page_value(instance)
        serializer_class = BasePageSerializer
        return serializer_class(value, context=self.context)

    def get_page_value(self, instance):
        if isinstance(instance, Page):
            return instance
        if isinstance(instance, AbstractMenuItem):
            return instance.link_page


class RecursiveMenuItemSerializer(MenuItemSerializerMixin, Serializer):
    href = fields.CharField(read_only=True)
    text = fields.CharField(read_only=True)
    active_class = fields.CharField(read_only=True)
    page = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()


class BaseMenuItemModelSerializer(MenuItemSerializerMixin, ModelSerializer):
    """
    Used as a base class when dynamically creating serializers for model
    objects with menu-like attributes, including subclasses of
    ``AbstractMainMenuItem`` and ``AbstractFlatMenuItem``, and also for
    ``section_root`` in ``SectionMenuSerializer`` - which is a page object with
    menu-like attributes added.
    """
    href = fields.CharField(read_only=True)
    text = fields.CharField(read_only=True)
    active_class = fields.CharField(read_only=True)
    page = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    children_serializer_class = RecursiveMenuItemSerializer
