from collections import OrderedDict

from django.conf import settings as django_settings
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.reverse import reverse
from rest_framework.response import Response

from wagtailmenus.conf import settings as wagtailmenus_settings
from wagtailmenus.api.v1.conf import settings as api_settings
from . import forms
from . import renderers
from . import serializers


class MenuGeneratorIndexView(APIView):
    name = "Menu Generation"

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


class MenuGeneratorView(APIView):
    menu_class = None

    # serialization
    serializer_class = None  # override this for custom view classes
    default_serializer_class = None
    serializer_class_setting_name = None

    # argument validation and defaults
    argument_form_class = None
    max_levels_default = None
    use_specific_default = None
    apply_active_classes_default = True
    allow_repeating_parents_default = True
    use_absolute_page_urls_default = False

    renderer_classes = (
        JSONRenderer,
        renderers.BrowsableAPIWithArgumentFormRenderer,
    )

    def get_menu_class(self):
        if self.menu_class is None:
            raise NotImplementedError(
                "You must either set the 'menu_class' attribute or override "
                "the get_menu_class() method for '%s'" % self.__class__.__name__
            )
        return self.menu_class

    def get_argument_form_class(self):
        if self.argument_form_class is None:
            raise NotImplementedError(
                "You must either set the 'argument_form_class' attribute or "
                "override the get_argument_form_class() method for '%s'" % self.__class__.__name__
            )
        return self.argument_form_class

    def get_argument_form(self, request, *args, **kwargs):
        init_kwargs = self.get_argument_form_kwargs(request)
        return self.get_argument_form_class()(**init_kwargs)

    def get_argument_form_kwargs(self, request):
        return {
            'request': request,
            'view': self,
            'data': request.POST or request.GET,
            'initial': self.get_argument_form_initial(request),
        }

    def get_argument_form_initial(self, request):
        return {
            'max_levels': self.max_levels_default,
            'use_specific': self.use_specific_default,
            'apply_active_classes': self.apply_active_classes_default,
            'allow_repeating_parents': self.allow_repeating_parents_default,
            'use_absolute_page_urls': self.use_absolute_page_urls_default,
        }

    def get_serializer(self, instance, *args, **kwargs):
        cls = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return cls(instance=instance, *args, **kwargs)

    def get_serializer_class(self):
        if self.serializer_class is not None:
            return self.serializer_class

        if self.default_serializer_class is None:
            raise NotImplementedError(
                "You must either set the 'default_serializer_class' attribute "
                "or override the get_serializer_class() method for '%s'" % self.__class__.__name__
            )

        setting_name = self.serializer_class_setting_name
        if setting_name:
            override_value = api_settings.get(setting_name)
            if override_value:
                # Use the 'objects' helper to retrieve the actual class
                return getattr(api_settings.objects, setting_name)
        return self.default_serializer_class

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
        }

    def get(self, request, *args, **kwargs):
        # seen_types is a mapping of type name strings (format: "app_label.ModelName")
        # to model classes. When an page object is serialised in the API, its model
        # is added to this mapping
        self.seen_types = OrderedDict()

        # Ensure all necessary argument values are present and valid
        form = self.get_argument_form(request, *args, **kwargs)
        self.argument_form = form

        if not form.is_valid():
            raise ValidationError(form.errors)

        # Activate selected language
        self.activate_selected_language(form.cleaned_data['language'])

        # Get a menu instance using the valid data
        menu_instance = self.get_menu_instance(request, form)

        # Create a serializer for this menu instance
        menu_serializer = self.get_serializer(menu_instance, *args, **kwargs)
        response_data = menu_serializer.data

        # Restore original language now that the menu has been serialized
        self.restore_original_language()

        return Response(response_data)

    def activate_selected_language(self, language):
        """
        Activates the provided language using translation.get_language(). Used
        before calling ``get_menu_instance()`` and ``get_serializer()``, to
        allow the menu to be rendered in the selected language.
        """
        if django_settings.USE_I18N:
            # store the the active language so that it can be restored
            self._original_language = translation.get_language()
            translation.activate(language)

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

    def restore_original_language(self):
        """
        Reactivates the language that was active before a 'selected language'
        was activated. This is called after menu representation has been
        extracted from the serializer, so that the response itself can be
        rendered in the original language.
        """
        if django_settings.USE_I18N and hasattr(self, '_original_language'):
            translation.activate(self._original_language)


class MainMenuGeneratorView(MenuGeneratorView):
    """
    Returns a JSON representation of a 'main menu' (including menu items) matching the supplied arguments.
    """
    name = _('Generate Main Menu')
    menu_class = wagtailmenus_settings.models.MAIN_MENU_MODEL
    argument_form_class = forms.MainMenuGeneratorArgumentForm

    # serialization
    default_serializer_class = serializers.MainMenuSerializer
    serializer_class_setting_name = 'MAIN_MENU_SERIALIZER'


class FlatMenuGeneratorView(MenuGeneratorView):
    """
    Returns a JSON representation of a 'flat menu' (including menu items) matching the supplied arguments.
    """
    name = _('Generate Flat Menu')
    menu_class = wagtailmenus_settings.models.FLAT_MENU_MODEL
    argument_form_class = forms.FlatMenuGeneratorArgumentForm

    # serialization
    default_serializer_class = serializers.FlatMenuSerializer
    serializer_class_setting_name = 'FLAT_MENU_SERIALIZER'

    # argument defaults
    fall_back_to_default_site_menus_default = True

    def get_argument_form_initial(self, request):
        initial = super().get_argument_form_initial(request)
        initial['fall_back_to_default_site_menus'] = self.fall_back_to_default_site_menus_default
        return initial


class ChildrenMenuGeneratorView(MenuGeneratorView):
    """
    Returns a JSON representation of a 'children menu' (including menu items) matching the supplied arguments.
    """
    name = _('Generate Children Menu')
    menu_class = wagtailmenus_settings.objects.CHILDREN_MENU_CLASS
    argument_form_class = forms.ChildrenMenuGeneratorArgumentForm

    # serialization
    default_serializer_class = serializers.ChildrenMenuSerializer
    serializer_class_setting_name = 'CHILDREN_MENU_SERIALIZER'

    # argument defaults
    max_levels_default = wagtailmenus_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS
    use_specific_default = wagtailmenus_settings.DEFAULT_CHILDREN_MENU_USE_SPECIFIC
    apply_active_classes_default = False


class SectionMenuGeneratorView(MenuGeneratorView):
    """
    Returns a JSON representation of a 'section menu' (including menu items) matching the supplied arguments.
    """
    name = _('Generate Section Menu')
    menu_class = wagtailmenus_settings.objects.SECTION_MENU_CLASS
    argument_form_class = forms.SectionMenuGeneratorArgumentForm

    # serialization
    default_serializer_class = serializers.SectionMenuSerializer
    serializer_class_setting_name = 'SECTION_MENU_SERIALIZER'

    # argument defaults
    max_levels_default = wagtailmenus_settings.DEFAULT_SECTION_MENU_MAX_LEVELS
    use_specific_default = wagtailmenus_settings.DEFAULT_SECTION_MENU_USE_SPECIFIC
