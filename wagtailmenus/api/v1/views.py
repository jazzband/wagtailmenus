from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.settings import perform_import

from wagtailmenus.conf import settings as wagtailmenus_settings
from wagtailmenus.utils.misc import derive_ancestor_ids
from wagtailmenus.api.utils import make_result_serializer_class
from wagtailmenus.api.v1.conf import settings as api_settings
from wagtailmenus.api.v1.serializers import BaseModelMenuSerializer, options as option_serializers


class MenuAPIView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if api_settings.AUTHENTICATION_CLASSES is not None:
            self.authentication_classes = perform_import(
                api_settings.AUTHENTICATION_CLASSES,
                'WAGTAILMENUS_API_V1_AUTHENTICATION_CLASSES'
            )
        if api_settings.PERMISSION_CLASSES is not None:
            self.permission_classes = perform_import(
                api_settings.PERMISSION_CLASSES,
                'WAGTAILMENUS_API_V1_PERMISSION_CLASSES'
            )
        if api_settings.RENDERER_CLASSES is not None:
            self.renderer_classes = perform_import(
                api_settings.RENDERER_CLASSES,
                'WAGTAILMENUS_API_V1_RENDERER_CLASSES'
            )


class MenuGeneratorIndexView(MenuAPIView):
    name = "Menu Generation"

    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get(self, request, *args, **kwargs):
        # Return a plain {"name": "hyperlink"} response.
        data = OrderedDict()
        namespace = request.resolver_match.namespace
        url_names = ('main_menu', 'flat_menu', 'section_menu', 'children_menu')
        for name in url_names:
            if namespace:
                name = namespace + ':' + name
            data[name] = reverse(
                name,
                args=args,
                kwargs=kwargs,
                request=request,
                format=kwargs.get('format', None)
            )
        return Response(data)


class BaseMenuGeneratorView(MenuAPIView):
    menu_class = None

    # argument validation and defaults
    serializer_class = None
    max_levels_default = None
    allow_repeating_parents_default = True

    # result serialization
    result_serializer_class = None
    result_serializer_class_setting_name = None

    # ---------------------------------------------------------------
    # Querystring option serialization
    # ---------------------------------------------------------------

    def get_option_data(self):
        original = self.request.POST or self.request.GET
        data = original.copy()
        for key, value in self.self.get_default_option_values():
            if key not in data:
                data[key] = value
        return data

    @classmethod
    def get_serializer_class(cls):
        if cls.serializer_class:
            return cls.serializer_class
        raise ImproperlyConfigured(
            "You must either set the 'serializer_class' attribute or "
            "override the get_serializer_class() method for '%s'"
            % cls.__name__
        )

    def get_serializer(self):
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        return serializer_class(
            data=self.get_option_data(),
            context=context
        )

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
        }

    def get_default_option_values(self):
        return {
            'max_levels': self.max_levels_default,
            'allow_repeating_parents': self.allow_repeating_parents_default,
        }

    # ---------------------------------------------------------------
    # Getting a menu instance from serialized options
    # ---------------------------------------------------------------

    @classmethod
    def get_menu_class(cls):
        if cls.menu_class:
            return cls.menu_class
        raise ImproperlyConfigured(
            "You must either set the 'menu_class' attribute or override "
            "the get_menu_class() method for '%s'"
            % cls.__name__
        )

    def get_menu_instance(self, **kwargs):
        """
        The Menu classes themselves are responsible for getting/creating menu
        instances and preparing them for rendering. So, the role of this
        method is to bundle up all available data into a format that
        ``Menu._get_render_prepared_object()`` will understand, and call that.
        """

        # Set request attributes with 'current_site'
        current_site = kwargs.pop('current_site', None)
        if current_site is not None:
            self.request.site = current_site  # Wagtail < 2.9
            self.request._wagtatil_site = current_site  # Wagtail >= 2.9

        # Generate ancestor_page_ids
        if kwargs['apply_active_classes']:
            ancestor_page_ids = derive_ancestor_ids(
                kwargs.get('current_page') or kwargs.get('best_match_page')
            )
        else:
            ancestor_page_ids = ()

        # `Menu._get_render_prepared_object()`` normally recieves a
        # ``RequestContext`` object, but will accept a dictionary with a
        # similar data structure.
        dummy_context = {
            'request': self.request,
            'current_site': current_site,
            'wagtailmenus_vals': {
                'current_page': kwargs.pop('current_page', None),
                'section_root': kwargs.pop('section_root_page', None),
                'current_page_ancestor_ids': ancestor_page_ids,
            }
        }

        # Generate the menu and return
        menu_class = self.get_menu_class()
        menu_instance = menu_class._get_render_prepared_object(
            dummy_context,
            add_sub_menus_inline=True,
            use_absolute_page_urls=not kwargs.pop('relative_page_urls'),
            ancestor_page_ids=ancestor_page_ids,
            **kwargs
        )
        if menu_instance is None:
            raise NotFound(_(
                "No {class_name} object could be found matching the supplied "
                "values.").format(class_name=menu_class.__name__)
            )

        return menu_instance

    # ---------------------------------------------------------------
    # Serializating the result
    # ---------------------------------------------------------------

    @classmethod
    def get_result_serializer_class(cls):
        if cls.result_serializer_class:
            return cls.result_serializer_class
        if cls.result_serializer_class_setting_name:
            return api_settings.get_object(cls.result_serializer_class_setting_name)
        raise ImproperlyConfigured(
            "You must either set the 'result_serializer_class' attribute, "
            "or override the get_result_serializer_class() method for '%s'"
            % cls.__name__
        )

    def get_result_serializer(self, menu_instance):
        result_serializer_class = self.get_result_serializer_class()
        context = self.get_result_serializer_context()
        return result_serializer_class(menu_instance, context=context)

    def get_result_serializer_context(self):
        return self.get_serializer_context()

    # ---------------------------------------------------------------
    # View logic
    # ---------------------------------------------------------------

    def get(self, request, *args, **kwargs):
        # seen_types is a mapping of type name strings
        # (format: "app_label.ModelName") to model classes.
        # When an page object is serialised in the API, its
        # model is added to this mapping
        self.seen_types = OrderedDict()

        # Ensure supplied option arguments are valid for this view
        option_serializer = self.get_serializer()
        option_serializer.is_valid(raise_exception=True)

        # Activate selected language during serialization
        with translation.override(
            option_serializer.validated_data.get('language', translation.get_language())
        ):
            # Get a menu instance using the valid data
            menu_instance = self.get_menu_instance(**option_serializer.validated_data)

            # Create a serializer for this menu instance
            menu_serializer = self.get_result_serializer(menu_instance)
            response_data = menu_serializer.data

        return Response(response_data)


class ChildrenMenuGeneratorView(BaseMenuGeneratorView):
    """
    Returns a JSON representation of a 'children menu' (including menu items)
    matching the supplied arguments.
    """
    name = _('Generate Children Menu')
    menu_class = wagtailmenus_settings.objects.CHILDREN_MENU_CLASS
    serializer_class = option_serializers.ChildrenMenuOptionSerializer
    result_serializer_class_setting_name = 'CHILDREN_MENU_SERIALIZER'

    # argument defaults
    max_levels_default = wagtailmenus_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS


class SectionMenuGeneratorView(BaseMenuGeneratorView):
    """
    Returns a JSON representation of a 'section menu' (including menu items)
    matching the supplied arguments.
    """
    name = _('Generate Section Menu')
    menu_class = wagtailmenus_settings.objects.SECTION_MENU_CLASS
    serializer_class = option_serializers.SectionMenuOptionSerializer
    result_serializer_class_setting_name = 'SECTION_MENU_SERIALIZER'

    # argument defaults
    max_levels_default = wagtailmenus_settings.DEFAULT_SECTION_MENU_MAX_LEVELS


class BaseModelMenuGeneratorView(BaseMenuGeneratorView):
    base_result_serializer_class = BaseModelMenuSerializer

    @classmethod
    def get_result_serializer_fields(cls):
        return cls.menu_class.api_fields

    @classmethod
    def get_result_serializer_field_names(cls):
        return [field.name for field in cls.get_result_serializer_fields()]

    @classmethod
    def get_result_serializer_field_overrides(cls):
        return {
            field.name: field.serializer
            for field in cls.get_result_serializer_fields()
            if field.serializer is not None
        }

    @classmethod
    def get_result_serializer_class_create_kwargs(cls, **kwargs):
        values = {
            'model': cls.menu_class,
            'field_names': cls.get_result_serializer_field_names(),
            'field_serializer_overrides': cls.get_result_serializer_field_overrides(),
        }
        values.update(kwargs)
        return values

    @classmethod
    def get_result_serializer_class(cls):
        if cls.result_serializer_class:
            return cls.result_serializer_class
        name = cls.menu_class.__name__ + 'Serializer'
        base_class = cls.base_result_serializer_class
        create_kwargs = cls.get_result_serializer_class_create_kwargs()
        return make_result_serializer_class(name, base_class, **create_kwargs)


class MainMenuGeneratorView(BaseModelMenuGeneratorView):
    """
    Returns a JSON representation of a 'main menu' (including menu items)
    matching the supplied arguments.
    """
    name = _('Generate Main Menu')
    menu_class = wagtailmenus_settings.models.MAIN_MENU_MODEL
    serializer_class = option_serializers.MainMenuOptionSerializer
    base_result_serializer_class_setting_name = 'BASE_MAIN_MENU_SERIALIZER'


class FlatMenuGeneratorView(BaseModelMenuGeneratorView):
    """
    Returns a JSON representation of a 'flat menu' (including menu items)
    matching the supplied arguments.
    """
    name = _('Generate Flat Menu')
    menu_class = wagtailmenus_settings.models.FLAT_MENU_MODEL
    serializer_class = option_serializers.FlatMenuOptionSerializer
    base_result_serializer_class_setting_name = 'BASE_FLAT_MENU_SERIALIZER'

    # argument defaults
    fall_back_to_default_site_menus_default = True

    def get_default_option_values(self):
        initial = super().get_default_option_values()
        initial['fall_back_to_default_site_menus'] = self.fall_back_to_default_site_menus_default
        return initial
