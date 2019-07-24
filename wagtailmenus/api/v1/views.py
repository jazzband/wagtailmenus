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
    apply_active_classes_default = False
    allow_repeating_parents_default = True
    use_absolute_page_urls_default = False

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
            'data': self.request.POST or self.request.GET,
            'initial': self.get_form_initial(),
        }

    def get_form_initial(self):
        return {
            'max_levels': self.max_levels_default,
            'apply_active_classes': self.apply_active_classes_default,
            'allow_repeating_parents': self.allow_repeating_parents_default,
            'use_absolute_page_urls': self.use_absolute_page_urls_default,
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

    def is_current_page_derivation_required(self, data):
        """
        Returns a boolean indicating whether the form should
        attempt to derive a 'current_page' value from other
        values in ``data``.
        """
        return (
            data.get('current_page') is None and
            data.get('apply_active_classes')
        )

    def accept_best_match_for_current_page(self, data):
        return True

    def derive_current_page(self, data):
        """
        Attempts to derive a 'current_page' value from other values
        in ``data`` and update``data`` with that value.
        """
        func = api_settings.objects.CURRENT_PAGE_DERIVATION_FUNCTION

        match, is_exact_match = func(
            data.get('current_url'),
            current_site=self.request.site,
            api_request=self.request,
            accept_best_match=self.accept_best_match_for_current_page(data),
        )

        if match:
            if is_exact_match:
                data['current_page'] = match
            else:
                data['best_match_page'] = match

    def derive_ancestor_page_ids(self, data):
        """
        Attempts to derive a tuple of 'ancestor_page_ids' from
        page values in ``data`` and update ``data`` with the value.
        """
        source_page = data.get('current_page') or \
            data.get('best_match_page')
        if source_page:
            ancestor_ids = tuple(
                source_page.get_ancestors(inclusive=data['current_page'] is None)
                .filter(depth__gte=wagtailmenus_settings.SECTION_ROOT_DEPTH)
                .values_list('id', flat=True)
            )
        else:
            ancestor_ids = ()
        data['ancestor_page_ids'] = ancestor_ids

    def process_form_data(self, data):
        if self.is_current_page_derivation_required(data):
            self.derive_current_page(data)
        if data['apply_active_classes']:
            self.derive_ancestor_page_ids(data)
        return data

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

        # Derive current site and add to the current request
        site_derivation_function = api_settings.objects.CURRENT_SITE_DERIVATION_FUNCTION
        self.request.site = site_derivation_function(
            form.cleaned_data['current_url'],
            api_request=self.request,
        )

        # Run post-processing on form data
        processed_data = self.process_form_data(form.cleaned_data)

        # Activate selected language during serialization
        with translation.override(
            processed_data.get('language', translation.get_language())
        ):

            # Get a menu instance using the valid data
            menu_instance = self.get_menu_instance(processed_data)

            # Create a serializer for this menu instance
            menu_serializer = self.get_serializer(menu_instance)
            response_data = menu_serializer.data

        return Response(response_data)

    def get_menu_instance(self, data):
        """
        The Menu classes themselves are responsible for getting/creating menu
        instances and preparing them for rendering. So, the role of this
        method is to bundle up all available data into a format that
        ``Menu._get_render_prepared_object()`` will understand, and call that.
        """

        # `Menu._get_render_prepared_object()`` normally recieves a
        # ``RequestContext`` object, but will accept a dictionary with a
        # similar data structure.
        dummy_context = {
            'request': self.request,
            'wagtailmenus_vals': {
                'current_page': data.pop('current_page', None),
                'section_root': data.pop('section_root_page', None),
                'current_page_ancestor_ids': data.pop('ancestor_page_ids', ()),
            }
        }
        data['add_sub_menus_inline'] = True  # This should always be True

        # Generate the menu and return
        menu_class = self.get_menu_class()
        menu_instance = menu_class._get_render_prepared_object(dummy_context, **data)
        if menu_instance is None:
            raise NotFound(_(
                "No {class_name} object could be found matching the supplied "
                "values.").format(class_name=menu_class.__name__)
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
    serializer_class_setting_name = 'MAIN_MENU_SERIALIZER'


class FlatMenuGeneratorView(BaseMenuGeneratorView):
    """
    Returns a JSON representation of a 'flat menu' (including menu items)
    matching the supplied arguments.
    """
    name = _('Generate Flat Menu')
    menu_class = wagtailmenus_settings.models.FLAT_MENU_MODEL
    form_class = forms.FlatMenuGeneratorArgumentForm
    serializer_class_setting_name = 'FLAT_MENU_SERIALIZER'

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
    serializer_class_setting_name = 'CHILDREN_MENU_SERIALIZER'

    # argument defaults
    max_levels_default = wagtailmenus_settings.DEFAULT_CHILDREN_MENU_MAX_LEVELS

    def is_current_page_derivation_required(self, data):
        return (
            super().is_current_page_derivation_required(data) or
            not data.get('parent_page')
        )

    def accept_best_match_for_current_page(self, data):
        # If 'current_page' will be used to supplement 'parent_page',
        # only an exact match for 'current_url' will do
        return bool(data['parent_page'])

    def process_form_data(self, data):
        data = super().process_form_data(data)
        if not data['parent_page']:
            self.derive_parent_page(data)
        return data

    def derive_parent_page(self, data):
        """
        Attempts to derive 'parent_page' value from other values in
        ``data`` and update ``data`` with the value.
        """
        if data['current_page']:
            data['parent_page'] = data['current_page']
            return

        raise ValidationError({'parent_page': UNDERIVABLE_MSG})


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

    def is_current_page_derivation_required(self, data):
        return (
            super().is_current_page_derivation_required(data) or
            not data.get('section_root_page')
        )

    def process_form_data(self, data):
        data = super().process_form_data(data)
        if not data['section_root_page']:
            self.derive_section_root_page(data)
        return data

    def derive_section_root_page(self, data):
        """
        Attempts to derive a 'section_root_page' value from other values in
        ``data`` and update ``data`` with the value.
        """
        source_page = data.get('current_page') or data.get('best_match_page')
        section_root_depth = wagtailmenus_settings.SECTION_ROOT_DEPTH

        if source_page:
            if source_page.dept == section_root_depth:
                data['section_root_page'] = source_page
            elif source_page.depth > section_root_depth:
                data['section_root_page'] = source_page.get_ancestors().get(
                    depth__exact=section_root_depth)

        if not data['section_root_page']:
            raise ValidationError({'section_root_page': UNDERIVABLE_MSG})
