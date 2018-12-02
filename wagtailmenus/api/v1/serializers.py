from rest_framework import fields
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework_recursive.fields import RecursiveField

from wagtail.core.models import Page
from wagtail.api.v2.serializers import PageTypeField
from wagtailmenus.conf import settings as wagtailmenus_settings
from wagtailmenus.api.conf import settings as api_settings
from wagtailmenus.models.menuitems import AbstractMenuItem

CHILDREN_ATTR = '__children'
PAGE_ATTR = '__page'

main_menu_model = wagtailmenus_settings.models.MAIN_MENU_MODEL
flat_menu_model = wagtailmenus_settings.models.FLAT_MENU_MODEL


class BasePageSerializer(ModelSerializer):
    type = PageTypeField(read_only=True)


class InstanceSpecificFieldsMixin:

    def to_representation(self, instance):
        self.add_instance_specific_fields(instance)
        return super().to_representation(instance)

    def add_instance_specific_fields(self):
        pass


class MenuItemSerializerMixin(InstanceSpecificFieldsMixin):

    def __init__(self, *args, **kwargs):
        self._page_fields = kwargs.pop('page_fields', api_settings.MENU_ITEM_PAGE_FIELDS)
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
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

    def add_instance_specific_fields(self, instance):
        try:
            page = getattr(instance, PAGE_ATTR)
        except AttributeError:
            page = instance.get(PAGE_ATTR)
        if page:
            cls = self.get_page_specific_serializer_class(page)
            self.fields['page'] = cls(source=PAGE_ATTR)

    def get_page_specific_serializer_class(self, page):

        class PageSerializer(BasePageSerializer):
            class Meta:
                model = type(page)
                fields = self._page_fields

        return PageSerializer


class MenuItemSerializer(MenuItemSerializerMixin, Serializer):
    href = fields.CharField(read_only=True)
    text = fields.CharField(read_only=True)
    page = fields.DictField(read_only=True)
    active_class = fields.CharField(read_only=True)


class RecursiveMenuItemSerializer(MenuItemSerializer):
    children = RecursiveField(many=True, read_only=True, source=CHILDREN_ATTR)

    class Meta:
        fields = api_settings.MENU_ITEM_FIELDS


class BaseModelMenuItemSerializer(MenuItemSerializerMixin, ModelSerializer):
    href = fields.CharField(read_only=True)
    text = fields.CharField(read_only=True)
    active_class = fields.CharField(read_only=True)
    page = fields.DictField(read_only=True)
    children = RecursiveMenuItemSerializer(many=True, read_only=True, source=CHILDREN_ATTR)


class MainMenuSerializer(InstanceSpecificFieldsMixin, ModelSerializer):
    items = fields.ListField()

    class Meta:
        model = main_menu_model
        fields = api_settings.MAIN_MENU_FIELDS

    def add_instance_specific_fields(self, instance):

        class MainMenuItemSerializer(BaseModelMenuItemSerializer):
            class Meta:
                model = instance.get_menu_items_manager().model
                fields = api_settings.MAIN_MENU_ITEM_FIELDS

        self.fields['items'] = MainMenuItemSerializer(many=True, read_only=True, page_fields=api_settings.MAIN_MENU_ITEM_PAGE_FIELDS)


class FlatMenuSerializer(InstanceSpecificFieldsMixin, ModelSerializer):
    items = fields.ListField()

    class Meta:
        model = flat_menu_model
        fields = api_settings.FLAT_MENU_FIELDS

    def add_instance_specific_fields(self, instance):

        class FlatMenuItemSerializer(BaseModelMenuItemSerializer):
            class Meta:
                model = instance.get_menu_items_manager().model
                fields = api_settings.FLAT_MENU_ITEM_FIELDS

        self.fields['items'] = FlatMenuItemSerializer(many=True, read_only=True, page_fields=api_settings.FLAT_MENU_ITEM_PAGE_FIELDS)


class ChildrenMenuSerializer(InstanceSpecificFieldsMixin, Serializer):
    parent_page = fields.DictField(read_only=True)
    items = RecursiveMenuItemSerializer(many=True, read_only=True)

    def add_instance_specific_fields(self, instance):

        class ParentPageSerializer(BasePageSerializer):
            class Meta:
                model = type(instance.parent_page)
                fields = api_settings.PARENT_PAGE_FIELDS

        self.fields['parent_page'] = ParentPageSerializer()


class SectionMenuSerializer(Serializer):
    section_root = MenuItemSerializer(source='root_page', read_only=True, page_fields=api_settings.SECTION_ROOT_PAGE_FIELDS)
    items = RecursiveMenuItemSerializer(many=True, read_only=True)
