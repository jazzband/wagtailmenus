from rest_framework import fields
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework_recursive.fields import RecursiveField

from wagtail.core.models import Page
from wagtailmenus.api.v1.conf import settings as api_settings
from wagtailmenus.models.menuitems import AbstractMenuItem

from .page import BasePageSerializer
from .util import ContextSpecificFieldsMixin


CHILDREN_ATTR = '__children'
PAGE_ATTR = '__page'


class MenuItemSerializerMixin(ContextSpecificFieldsMixin):
    """
    A mixin to faciliate rendering of a number of different types of menu
    items, including ``MainMenuItem`` or ``FlatMenuItem`` objects (or custom
    variations of those), ``Page`` objects, or even dictionary-like structures
    added by custom hooks or ``MenuPageMixin.modify_submenu_items()`` methods.
    """

    page_field_init_kwargs = {
        'read_only': True,
        'source': PAGE_ATTR,
    }

    def to_representation(self, instance):
        """
        Due to the varied nature of menu item data, this override sets a couple
        of additional attributes (or adds extra items to a dictionary) that can
        be reliably used as a source for ``children`` and ``page`` fields.
        """
        children_val = ()
        if getattr(instance, 'sub_menu', None):
            children_val = instance.sub_menu.items

        page_val = None
        if isinstance(instance, Page):
            page_val = instance
        elif isinstance(instance, AbstractMenuItem):
            page_val = instance.link_page

        if isinstance(instance, dict):
            instance[CHILDREN_ATTR] = children_val
            instance[PAGE_ATTR] = page_val
        else:
            setattr(instance, CHILDREN_ATTR, children_val)
            setattr(instance, PAGE_ATTR, page_val)
        self.instance = instance
        return super().to_representation(instance)

    def update_fields(self, fields, instance, context):
        if 'page' in fields:
            if isinstance(instance, dict):
                page = instance.get(PAGE_ATTR)
            else:
                page = getattr(instance, PAGE_ATTR, None)
            self.replace_page_field(instance, page)

    def replace_page_field(self, instance, page):
        field_class = self.get_page_serializer_class(instance, page)
        init_kwargs = self.get_page_serializer_init_kwargs(instance, page)
        self.fields['page'] = field_class(**init_kwargs)

    def get_page_serializer_class(self, instance, page):
        if api_settings.MENU_ITEM_PAGE_SERIALIZER:
            return api_settings.objects.MENU_ITEM_PAGE_SERIALIZER

        class MenuItemPageSerializer(BasePageSerializer):
            class Meta:
                model = type(page)
                fields = self.Meta.page_fields

        return MenuItemPageSerializer

    def get_page_serializer_init_kwargs(self, instance, page):
        return self.page_field_init_kwargs


class RecursiveMenuItemSerializer(MenuItemSerializerMixin, Serializer):
    href = fields.CharField(read_only=True)
    text = fields.CharField(read_only=True)
    page = fields.DictField(read_only=True)
    active_class = fields.CharField(read_only=True)
    children = RecursiveField(many=True, read_only=True, source=CHILDREN_ATTR)

    class Meta:
        fields = api_settings.MENU_ITEM_SERIALIZER_FIELDS
        page_fields = api_settings.MENU_ITEM_PAGE_SERIALIZER_FIELDS


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
    page = fields.DictField(read_only=True)
    children = RecursiveMenuItemSerializer(many=True, read_only=True, source=CHILDREN_ATTR)
