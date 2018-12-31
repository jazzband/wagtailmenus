from rest_framework import fields
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework_recursive.fields import RecursiveField

from wagtail.core.models import Page
from wagtail.api.v2.serializers import PageTypeField
from wagtailmenus.conf import settings as wagtailmenus_settings
from wagtailmenus.api.v1.conf import settings as api_settings
from wagtailmenus.models.menuitems import AbstractMenuItem

CHILDREN_ATTR = '__children'
PAGE_ATTR = '__page'

main_menu_model = wagtailmenus_settings.models.MAIN_MENU_MODEL
flat_menu_model = wagtailmenus_settings.models.FLAT_MENU_MODEL


class ContextSpecificFieldsMixin:
    """
    A mixin to facilitate the addition/replacement of fields based on the
    specific ``instance`` being serialized, and any other context available.
    """
    def to_representation(self, instance):
        fields = self.fields
        self.update_fields(
            fields, instance, getattr(self, '_context', {})
        )
        return super().to_representation(instance)

    def update_fields(self, fields, instance, context):
        pass


class BasePageSerializer(ModelSerializer):
    """
    Used to render 'page' info for menu items. This could be a ``link_page``
    value for a model-based menu item (e.g. a ``MainMenuItem`` or
    ``FlatMenuItem`` object), or a representation of the menu item itself (if
    the menu item is in fact a ``Page`` object).
    """
    type = PageTypeField(read_only=True)


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

        class DefaultMenuItemPageSerializer(BasePageSerializer):
            class Meta:
                model = type(page)
                fields = api_settings.MENU_ITEM_PAGE_SERIALIZER_FIELDS

        return DefaultMenuItemPageSerializer

    def get_page_serializer_init_kwargs(self, instance, page):
        return self.page_field_init_kwargs


class MenuItemSerializer(MenuItemSerializerMixin, Serializer):
    href = fields.CharField(read_only=True)
    text = fields.CharField(read_only=True)
    page = fields.DictField(read_only=True)
    active_class = fields.CharField(read_only=True)
    children = RecursiveField(many=True, read_only=True, source=CHILDREN_ATTR)


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
    children = MenuItemSerializer(many=True, read_only=True, source=CHILDREN_ATTR)


class MenuSerializerMixin(ContextSpecificFieldsMixin):
    """
    A mixin to faciliate rendering of a number of different types of menu,
    including subclasses of ``AbastractMainMenu`` or ``AbstractFlatMenu``, or
    instances of non-model-based menu classes like ``ChildrenMenu`` or
    ``SectionMenu``.
    """

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

    def get_items_serializer_init_kwargs(self, instance):
        return self.items_field_init_kwargs


class MainMenuSerializer(MenuSerializerMixin, ModelSerializer):

    # Placeholder fields
    items = fields.ListField()

    class Meta:
        model = main_menu_model
        fields = ('site', 'items')

    def get_items_serializer_class(self, instance):
        if api_settings.MAIN_MENU_ITEM_SERIALIZER:
            return api_settings.objects.MAIN_MENU_ITEM_SERIALIZER

        class DefaultMainMenuItemSerializer(BaseMenuItemModelSerializer):
            class Meta:
                model = instance.get_menu_items_manager().model
                fields = api_settings.MAIN_MENU_ITEM_SERIALIZER_FIELDS

        return DefaultMainMenuItemSerializer


class FlatMenuSerializer(MenuSerializerMixin, ModelSerializer):

    # Placeholder fields
    items = fields.ListField()

    class Meta:
        model = flat_menu_model
        fields = ('site', 'handle', 'title', 'heading', 'items')

    def get_items_serializer_class(self, instance):
        if api_settings.FLAT_MENU_ITEM_SERIALIZER:
            return api_settings.objects.FLAT_MENU_ITEM_SERIALIZER

        class DefaultFlatMenuItemSerializer(BaseMenuItemModelSerializer):
            class Meta:
                model = instance.get_menu_items_manager().model
                fields = api_settings.FLAT_MENU_ITEM_SERIALIZER_FIELDS

        return DefaultFlatMenuItemSerializer


class ChildrenMenuSerializer(MenuSerializerMixin, Serializer):

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
        return MenuItemSerializer

    def get_parent_page_serializer_class(self, instance):
        if api_settings.PARENT_PAGE_SERIALIZER:
            return api_settings.objects.PARENT_PAGE_SERIALIZER

        class DefaultParentPageSerializer(BasePageSerializer):
            class Meta:
                model = type(instance.parent_page)
                fields = api_settings.PARENT_PAGE_SERIALIZER_FIELDS
        return DefaultParentPageSerializer

    def get_parent_page_serializer_init_kwargs(self, instance):
        return self.parent_page_field_init_kwargs


class SectionMenuSerializer(MenuSerializerMixin, Serializer):

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
        init_kwargs = self.get_section_root_field_init_kwargs(instance)
        self.fields['section_root'] = field_class(**init_kwargs)

    def get_items_serializer_class(self, instance):
        if api_settings.SECTION_MENU_ITEM_SERIALIZER:
            return api_settings.objects.SECTION_MENU_ITEM_SERIALIZER
        return MenuItemSerializer

    def get_section_root_serializer_class(self, instance):
        if api_settings.SECTION_ROOT_SERIALIZER:
            return api_settings.objects.SECTION_ROOT_SERIALIZER

        # BaseMenuItemModelSerializer is being used below because SectionMenu
        # adds 'text', 'href' and 'active_class' attrs to 'root_page', which
        # this base class handles nicely.
        class DefaultSectionRootSerializer(BaseMenuItemModelSerializer):
            class Meta:
                model = type(instance.root_page)
                fields = api_settings.SECTION_ROOT_SERIALIZER_FIELDS
        return DefaultSectionRootSerializer

    def get_section_root_serializer_init_kwargs(self, instance):
        return self.section_root_field_init_kwargs
