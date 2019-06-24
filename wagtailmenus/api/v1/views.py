from collections import OrderedDict

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.views import APIView
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.reverse import reverse
from rest_framework.response import Response

from wagtailmenus.conf import settings as wagtailmenus_settings
from wagtailmenus.api.v1.conf import settings as api_settings
from wagtailmenus.api.v1.renderers import BrowsableAPIWithArgumentFormRenderer
from . import forms
from . import serializers


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
    use_specific_default = None
    apply_active_classes_default = True
    allow_repeating_parents_default = True
    use_absolute_page_urls_default = False

    # serialization
    serializer_class = None

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
        if cls.serializer_class is None:
            raise NotImplementedError(
                "You must either set the 'serializer_class' attribute or "
                "override the get_serializer_class() method for '%s'"
                % cls.__name__
            )
        return cls.serializer_class

    def get_form_init_kwargs(self):
        return {
            'request': self.request,
            'view': self,
            'data': self.request.POST or self.request.GET,
            'initial': self.get_form_initial(),
        }

    def get_form_initial(self):
        return {
            'max_levels': self.max_levels_default,
            'use_specific': self.use_specific_default,
            'apply_active_classes': self.apply_active_classes_default,
            'allow_repeating_parents': self.allow_repeating_parents_default,
            'use_absolute_page_urls': self.use_absolute_page_urls_default,
        }

    def get_form(self, request):
        form_class = self.get_form_class()
        init_kwargs = self.get_form_init_kwargs()
        return form_class(**init_kwargs)

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

        # Ensure all necessary argument values are present and valid
        form = self.get_form(request)
        self.form = form

        if not form.is_valid():
            raise ValidationError(form.errors)

        # Activate selected language
        with translation.override(form.cleaned_data['language']):

            # Get a menu instance using the valid data
            menu_instance = self.get_menu_instance(request, form)

            # Create a serializer for this menu instance
            menu_serializer = self.get_serializer(menu_instance)
            response_data = menu_serializer.data

        return Response(response_data)

    def get_menu_instance(self, request, form):
        """
        The Menu classes themselves are responsible for getting/creating menu
        instances and preparing them for rendering. So, the role of this
        method is to bundle up all available data into a format that
        ``Menu._get_render_prepared_object()`` will understand, and call that.
        """
        data = dict(form.cleaned_data)

        # `Menu._get_render_prepared_object()`` normally recieves a
        # ``RequestContext`` object, but will accept a dictionary with a
        # similar data structure.
        dummy_context = {
            'request': request,
            'current_site': data.pop('site'),
            'wagtailmenus_vals': {
                'current_page': data.pop('current_page', None),
                'section_root': data.pop('section_root_page', None),
                'current_page_ancestor_ids': data.pop('ancestor_page_ids', ()),
            }
        }
        cls = self.get_menu_class()
        data['add_sub_menus_inline'] = True  # This should always be True

        # Generate the menu and return
        menu_instance = cls._get_render_prepared_object(dummy_context, **data)
        if menu_instance is None:
            raise NotFound(_(
                "No {class_name} object could be found matching the supplied "
                "values.").format(class_name=cls.__name__)
            )

        return menu_instance


class MainMenuGeneratorView(BaseMenuGeneratorView):
    """
    Returns a JSON representation of a 'main menu' (including menu items)
    matching the supplied arguments.
    """
    name = _('Generate Main Menu')
    menu_class = wagtailmenus_settings.models.MAIN_MENU_MODEL
    form_class = forms.MainMenuGeneratorArgumentForm
    serializer_class = api_settings.objects.MAIN_MENU_SERIALIZER


class FlatMenuGeneratorView(BaseMenuGeneratorView):
    """
    Returns a JSON representation of a 'flat menu' (including menu items)
    matching the supplied arguments.
    """
    name = _('Generate Flat Menu')
    menu_class = wagtailmenus_settings.models.FLAT_MENU_MODEL
    form_class = forms.FlatMenuGeneratorArgumentForm
    serializer_class = api_settings.objects.FLAT_MENU_SERIALIZER

    # argument defaults
    fall_back_to_default_site_menus_default = True

    def get_form_initial(self):
        initial = super().get_form_initial()
        initial['fall_back_to_default_site_menus'] = self.fall_back_to_default_site_menus_default
        return initial


class ChildrenMenuGeneratorView(BaseMenuGeneratorView):
    """
    Returns a JSON representation of a 'children menu' (including menu items)
    matching the supplied arguments.
    """
    name = _('Generate Children Menu')
    menu_class = wagtailmenus_settings.objects.CHILDREN_MENU_CLASS
    form_class = forms.ChildrenMenuGeneratorArgumentForm
    serializer_class = api_settings.objects.CHILDREN_MENU_SERIALIZER

    # argument defaults
    max_levels_default = wagtailmenus_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS
    use_specific_default = wagtailmenus_settings.DEFAULT_CHILDREN_MENU_USE_SPECIFIC
    apply_active_classes_default = False


class SectionMenuGeneratorView(BaseMenuGeneratorView):
    """
    Returns a JSON representation of a 'section menu' (including menu items)
    matching the supplied arguments.
    """
    name = _('Generate Section Menu')
    menu_class = wagtailmenus_settings.objects.SECTION_MENU_CLASS
    form_class = forms.SectionMenuGeneratorArgumentForm
    serializer_class = api_settings.objects.SECTION_MENU_SERIALIZER

    # argument defaults
    max_levels_default = wagtailmenus_settings.DEFAULT_SECTION_MENU_MAX_LEVELS
    use_specific_default = wagtailmenus_settings.DEFAULT_SECTION_MENU_USE_SPECIFIC
