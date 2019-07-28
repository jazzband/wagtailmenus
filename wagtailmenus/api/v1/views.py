from collections import OrderedDict

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.views import APIView
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.reverse import reverse
from rest_framework.response import Response

from wagtailmenus.conf import settings as wagtailmenus_settings
from wagtailmenus.utils.misc import derive_ancestor_ids
from wagtailmenus.api.utils import make_serializer_class
from wagtailmenus.api.v1.conf import settings as api_settings
from wagtailmenus.api.v1.renderers import BrowsableAPIWithArgumentFormRenderer

from . import forms


UNDERIVABLE_MSG = _(
    "This value was not provided and could not be derived from other values."
)


class MenuGeneratorIndexView(APIView):
    name = "Menu Generation"

    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get(self, request, *args, **kwargs):
        # Return a plain {"name": "hyperlink"} response.
        data = OrderedDict()
        namespace = request.resolver_match.namespace
        names = ('main_menu', 'flat_menu', 'section_menu', 'children_menu')
        for url_name in names:
            if namespace:
                url_name = namespace + ':' + url_name
            data[url_name] = reverse(
                url_name,
                args=args,
                kwargs=kwargs,
                request=request,
                format=kwargs.get('format', None)
            )
        return Response(data)


class BaseMenuGeneratorView(APIView):
    menu_class = None

    # argument validation and defaults
    form_class = None
    max_levels_default = None
    allow_repeating_parents_default = True

    # serialization
    serializer_class = None
    serializer_class_setting_name = None

    renderer_classes = (JSONRenderer, BrowsableAPIWithArgumentFormRenderer)

    @classmethod
    def get_menu_class(cls):
        if cls.menu_class is None:
            raise NotImplementedError(
                "You must either set the 'menu_class' attribute or override "
                "the get_menu_class() method for '%s'"
                % cls.__name__
            )
        return cls.menu_class

    @classmethod
    def get_form_class(cls):
        if cls.form_class is None:
            raise NotImplementedError(
                "You must either set the 'form_class' attribute or "
                "override the get_form_class() method for '%s'"
                % cls.__name__
            )
        return cls.form_class

    @classmethod
    def get_serializer_class(cls):
        if cls.serializer_class:
            return cls.serializer_class
        if cls.serializer_class_setting_name:
            return api_settings.get_object(cls.serializer_class_setting_name)
        raise NotImplementedError(
            "You must either set the 'serializer_class' attribute, "
            "or override the get_serializer_class() method for '%s'"
            % cls.__name__
        )

    def get_form_init_kwargs(self):
        return {
            'request': self.request,
            'data': self.request.POST or self.request.GET,
            'initial': self.get_form_initial(),
        }

    def get_form_initial(self):
        return {
            'max_levels': self.max_levels_default,
            'allow_repeating_parents': self.allow_repeating_parents_default,
        }

    def get_form(self):
        if hasattr(self, '_form'):
            return self._form
        form_class = self.get_form_class()
        init_kwargs = self.get_form_init_kwargs()
        form = form_class(**init_kwargs)
        self._form = form
        return form

    def get_serializer(self, menu_instance):
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        return serializer_class(menu_instance, context=context)

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
        }

    def get(self, request, *args, **kwargs):
        # seen_types is a mapping of type name strings
        # (format: "app_label.ModelName") to model classes.
        # When an page object is serialised in the API, its
        # model is added to this mapping
        self.seen_types = OrderedDict()

        # Ensure all argument values are valid
        form = self.get_form()
        if not form.is_valid():
            raise ValidationError(form.errors)

        # Activate selected language during serialization
        with translation.override(
            form.cleaned_data.get('language', translation.get_language())
        ):
            # Get a menu instance using the valid data
            menu_instance = self.get_menu_instance(form.cleaned_data)

            # Create a serializer for this menu instance
            menu_serializer = self.get_serializer(menu_instance)
            response_data = menu_serializer.data

        return Response(response_data)

    def get_menu_instance(self, form_data):
        """
        The Menu classes themselves are responsible for getting/creating menu
        instances and preparing them for rendering. So, the role of this
        method is to bundle up all available data into a format that
        ``Menu._get_render_prepared_object()`` will understand, and call that.
        """

        # Set request.site attribute from 'current_site'
        if 'current_site' in form_data:
            self.request.site = form_data.pop('current_site')

        # Generate ancestor_page_ids
        if form_data['apply_active_classes']:
            ancestor_page_ids = derive_ancestor_ids(
                form_data['current_page'] or form_data.get('best_match_page')
            )
        else:
            ancestor_page_ids = ()

        # `Menu._get_render_prepared_object()`` normally recieves a
        # ``RequestContext`` object, but will accept a dictionary with a
        # similar data structure.
        dummy_context = {
            'request': self.request,
            'wagtailmenus_vals': {
                'current_page': form_data.pop('current_page', None),
                'section_root': form_data.pop('section_root_page', None),
                'current_page_ancestor_ids': form_data.pop('ancestor_page_ids', ()),
            }
        }

        # Generate the menu and return
        menu_class = self.get_menu_class()
        menu_instance = menu_class._get_render_prepared_object(
            dummy_context,
            add_sub_menus_inline=True,
            use_absolute_page_urls=not form_data.pop('use_relative_page_urls'),
            ancestor_page_ids=ancestor_page_ids,
            **form_data
        )
        if menu_instance is None:
            raise NotFound(_(
                "No {class_name} object could be found matching the supplied "
                "values.").format(class_name=menu_class.__name__)
            )

        return menu_instance


class ChildrenMenuGeneratorView(BaseMenuGeneratorView):
    """
    Returns a JSON representation of a 'children menu' (including menu items)
    matching the supplied arguments.
    """
    name = _('Generate Children Menu')
    menu_class = wagtailmenus_settings.objects.CHILDREN_MENU_CLASS
    form_class = forms.ChildrenMenuGeneratorArgumentForm
    serializer_class_setting_name = 'CHILDREN_MENU_SERIALIZER'

    # argument defaults
    max_levels_default = wagtailmenus_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS


class SectionMenuGeneratorView(BaseMenuGeneratorView):
    """
    Returns a JSON representation of a 'section menu' (including menu items)
    matching the supplied arguments.
    """
    name = _('Generate Section Menu')
    menu_class = wagtailmenus_settings.objects.SECTION_MENU_CLASS
    form_class = forms.SectionMenuGeneratorArgumentForm
    serializer_class_setting_name = 'SECTION_MENU_SERIALIZER'

    # argument defaults
    max_levels_default = wagtailmenus_settings.DEFAULT_SECTION_MENU_MAX_LEVELS


class MenuBasedMenuGeneratorView(BaseMenuGeneratorView):
    base_serializer_class = None
    base_serializer_class_setting_name = None

    @classmethod
    def get_serializer_fields(cls):
        return cls.menu_class.api_fields

    @classmethod
    def get_serializer_field_names(cls):
        return [field.name for field in cls.get_serializer_fields()]

    @classmethod
    def get_serializer_field_overrides(cls):
        return {
            field.name: field.serializer
            for field in cls.get_serializer_fields()
            if field.serializer is not None
        }

    @classmethod
    def get_base_serializer_class(cls):
        if cls.base_serializer_class:
            return cls.base_serializer_class
        return api_settings.get_object(cls.base_serializer_class_setting_name)

    @classmethod
    def get_serializer_class_create_kwargs(cls, base_class, **kwargs):
        values = {
            'model': cls.menu_class,
            'field_names': cls.get_serializer_field_names(),
            'field_serializer_overrides': cls.get_serializer_field_overrides(),
        }
        values.update(kwargs)
        return values

    @classmethod
    def get_serializer_class(cls):
        if cls.serializer_class:
            return cls.serializer_class
        name = cls.menu_class.__name__ + 'Serializer'
        base_class = cls.get_base_serializer_class()
        create_kwargs = cls.get_serializer_class_create_kwargs(base_class)
        return make_serializer_class(name, base_class, **create_kwargs)


class MainMenuGeneratorView(MenuBasedMenuGeneratorView):
    """
    Returns a JSON representation of a 'main menu' (including menu items)
    matching the supplied arguments.
    """
    name = _('Generate Main Menu')
    menu_class = wagtailmenus_settings.models.MAIN_MENU_MODEL
    form_class = forms.MainMenuGeneratorArgumentForm
    base_serializer_class_setting_name = 'BASE_MAIN_MENU_SERIALIZER'


class FlatMenuGeneratorView(MenuBasedMenuGeneratorView):
    """
    Returns a JSON representation of a 'flat menu' (including menu items)
    matching the supplied arguments.
    """
    name = _('Generate Flat Menu')
    menu_class = wagtailmenus_settings.models.FLAT_MENU_MODEL
    form_class = forms.FlatMenuGeneratorArgumentForm
    base_serializer_class_setting_name = 'BASE_FLAT_MENU_SERIALIZER'

    # argument defaults
    fall_back_to_default_site_menus_default = True

    def get_form_initial(self):
        initial = super().get_form_initial()
        initial['fall_back_to_default_site_menus'] = self.fall_back_to_default_site_menus_default
        return initial
