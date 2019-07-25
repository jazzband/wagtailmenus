from collections import OrderedDict

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.views import APIView
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.reverse import reverse
from rest_framework.response import Response

from wagtailmenus.conf import settings as wagtailmenus_settings
from wagtailmenus.utils.misc import derive_section_root, derive_ancestor_ids
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

    def process_form_data(self, data):
        if not data['current_page'] and not data.get('best_match_page') and (
            data['apply_active_classes'] or data['use_relative_urls']
        ):
            self.set_current_or_best_match_page(data)

        if data['apply_active_classes']:
            self.set_ancestor_page_ids(data)

        # Replace 'use_relative_page_urls' with 'use_absolute_page_urls'
        data['use_absolute_page_urls'] = not data.pop('use_relative_page_urls')

        return data

    def set_current_site(self, data):
        """
        Attempts to derive a 'current_site' value from other
        values in ``data`` and update ``data`` with the value.
        """
        derivation_function = api_settings.objects.CURRENT_SITE_DERIVATION_FUNCTION

        site_page = data.get('current_page') or \
            data.get('parent_page') or \
            data.get('section_root_page')

        data['current_site'] = derivation_function(
            self.request, site_page, data['current_url']
        )

    def set_current_or_best_match_page(self, data):
        """
        Attempts to derive a ``Page`` value from 'current_url` in
        ``data``. If a page is found matching the complete URL, it will
        be added to data as 'current_page'. Otherwise, it will be added
        as 'best_match_page'.
        """
        derivation_function = api_settings.objects.CURRENT_PAGE_DERIVATION_FUNCTION

        if not data.get('current_site'):
            self.derive_current_site(data)

        page, full_url_match = derivation_function(
            self.request,
            data['current_site'],
            data.get('current_url'),
        )

        if full_url_match:
            data['current_page'] = page
        else:
            data['best_match_page'] = page

    def set_ancestor_page_ids(self, data):
        """
        Attempts to derive and list of 'ancestor_page_ids' from
        'current_page' or 'best_match_page' values in ``data`` and
        update ``data`` with that value.
        """
        data['ancestor_page_ids'] = derive_ancestor_ids(
            data['current_page'] or data.get('best_match_page')
        )

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

        # Apply any additional processing to form data
        processed_data = self.process_form_data(
            form.cleaned_data.copy()
        )

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

        # Set request.site attribute from 'current_site'
        if 'current_site' in data:
            self.request.site = data.pop('current_site')

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

    def process_form_data(self, data):
        data['current_site'] = self.derive_current_site(data)
        return super().process_form_data(data)


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

    def process_form_data(self, data):
        data['current_site'] = self.derive_current_site(data)
        return super().process_form_data(data)


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

    def process_form_data(self, data):
        if not data['parent_page']:
            self.set_parent_page(data)
        return super().process_form_data(data)

    def set_parent_page(self, data):
        """
        Attempts to derive a 'parent_page' value from 'current_page'
        or 'current_url' values in ``data``, and update ``data`` with
        the value. Raises a ``ValidationError`` if the value cannot be
        derived.
        """
        if not data['current_page']:
            self.set_current_or_best_match_page(data)

        # NOTE: 'best_match_page' is not a good enough substitute here
        if data['current_page']:
            data['parent_page'] = data['current_page']
        else:
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

    def process_form_data(self, data):
        if not data['section_root_page']:
            self.set_section_root_page(data)
        return super().process_form_data(data)

    def set_section_root_page(self, data):
        """
        Attempts to derive a 'parent_page' value from 'current_page'
        or 'current_url' values in ``data``, and update ``data`` with
        the value. Raises a ``ValidationError`` if the value cannot be
        derived.
        """
        if not data['current_page']:
            self.set_current_or_best_match_page(data)

        # NOTE: 'current_page' or 'best_match_page' will do here, so
        # long as they are deep enough
        section_root = derive_section_root(data['current_page'] or data.get('best_match_page'))

        if section_root:
            data['section_root_page'] = section_root
        else:
            raise ValidationError({'section_root_page': UNDERIVABLE_MSG})
