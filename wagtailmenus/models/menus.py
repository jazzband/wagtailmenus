from collections import defaultdict, namedtuple, OrderedDict
from types import GeneratorType

from distutils.version import LooseVersion
from django import __version__ as django_version
from django.db import models
from django.db.models import BooleanField, Case, Q, When
from django.core.exceptions import ImproperlyConfigured, MultipleObjectsReturned
from django.http import HttpRequest
from django.template.loader import get_template, select_template
from django.utils.functional import cached_property, lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
try:
    from wagtail import hooks
    from wagtail.models import Page, Site
except ImportError:
    from wagtail.core import hooks
    from wagtail.core.models import Page, Site


from wagtailmenus import forms, panels
from wagtailmenus.conf import constants, settings
from wagtailmenus.errors import RequestUnavailableError
from wagtailmenus.utils.misc import get_fake_request, get_site_from_request
from .menuitems import MenuItem
from .mixins import DefinesSubMenuTemplatesMixin
from .pages import AbstractLinkPage

if LooseVersion(django_version) >= LooseVersion('4.1'):
    mark_safe_lazy = mark_safe
else:
    mark_safe_lazy = lazy(mark_safe, str)

ContextualVals = namedtuple('ContextualVals', (
    'parent_context',
    'request',
    'current_site',
    'current_level',
    'original_menu_tag',
    'original_menu_instance',
    'current_page',
    'current_section_root_page',
    'current_page_ancestor_ids',
))

OptionVals = namedtuple('OptionVals', (
    'max_levels',
    'apply_active_classes',
    'allow_repeating_parents',
    'use_absolute_page_urls',
    'add_sub_menus_inline',
    'parent_page',
    'handle',
    'template_name',
    'sub_menu_template_name',
    'sub_menu_template_names',
    'extra',
))


# ########################################################
# Base classes
# ########################################################

class Menu:
    """The base class that which all other menu classes should inherit from"""
    menu_short_name = ''  # used by 'get_template_names()'
    related_templatetag_name = ''
    template_name = None
    menu_instance_context_name = 'menu'
    sub_menu_class = None

    @classmethod
    def render_from_tag(
        cls, context, max_levels=None, apply_active_classes=True,
        allow_repeating_parents=True, use_absolute_page_urls=False,
        add_sub_menus_inline=None, template_name='', **kwargs
    ):
        """
        A template tag should call this method to render a menu.
        The ``Context`` instance and option values provided are used to get or
        create a relevant menu instance, prepare it, then render it and it's
        menu items to an appropriate template.

        It shouldn't be neccessary to override this method, as any new option
        values will be available as a dict in `opt_vals.extra`, and there are
        more specific methods for overriding certain behaviour at different
        stages of rendering, such as:

            * get_from_collected_values() (if the class is a Django model), OR
            * create_from_collected_values() (if it isn't)

            * prepare_to_render()
            * get_context_data()
            * render_to_template()
        """
        instance = cls._get_render_prepared_object(
            context,
            max_levels=max_levels,
            apply_active_classes=apply_active_classes,
            allow_repeating_parents=allow_repeating_parents,
            use_absolute_page_urls=use_absolute_page_urls,
            add_sub_menus_inline=add_sub_menus_inline,
            template_name=template_name,
            **kwargs
        )
        if not instance:
            return ''
        return instance.render_to_template()

    @classmethod
    def _get_render_prepared_object(cls, context, **option_values):
        """
        Returns a fully prepared, request-aware menu object that can be used
        for rendering. ``context`` could be a ``django.template.Context``
        object passed to ``render_from_tag()`` by a menu tag.
        """
        ctx_vals = cls._create_contextualvals_obj_from_context(context)
        opt_vals = cls._create_optionvals_obj_from_values(**option_values)

        if issubclass(cls, models.Model):
            instance = cls.get_from_collected_values(ctx_vals, opt_vals)
        else:
            instance = cls.create_from_collected_values(ctx_vals, opt_vals)
        if not instance:
            return None

        instance.prepare_to_render(context['request'], ctx_vals, opt_vals)
        return instance

    @classmethod
    def _create_contextualvals_obj_from_context(cls, context):
        """
        Gathers all of the 'contextual' data needed to render a menu instance
        and returns it in a structure that can be conveniently referenced
        throughout the process of preparing the menu and menu items and
        for rendering.
        """
        context_processor_vals = context.get('wagtailmenus_vals', {})
        return ContextualVals(
            context,
            context.get('request') or get_fake_request(),
            cls._get_site(context),
            context.get('current_level', 0) + 1,
            context.get('original_menu_tag', cls.related_templatetag_name),
            context.get('original_menu_instance'),
            context_processor_vals.get('current_page'),
            context_processor_vals.get('section_root'),
            context_processor_vals.get('current_page_ancestor_ids', ()),
        )

    @classmethod
    def _get_site(cls, context):
        site = context.get('site')
        if isinstance(site, Site):
            return site
        request = context.get('request')
        if request is not None:
            return get_site_from_request(request)

    @classmethod
    def _create_optionvals_obj_from_values(cls, **kwargs):
        """
        Takes all of the options passed to the class's ``render_from_tag()``
        method and returns them in a structure that can be conveniently
        referenced throughout the process of rendering.

        Any additional options supplied by custom menu tags will be available
        as a dictionary using the 'extra' key name. For example, when rendering
        a flat menu, the 'fall_back_to_default_site_menus' option passed to the
        tag is available as:

        .. code-block:: python

            option_vals.extra['fall_back_to_default_site_menus']
        """
        return OptionVals(
            kwargs.pop('max_levels'),
            kwargs.pop('apply_active_classes'),
            kwargs.pop('allow_repeating_parents'),
            kwargs.pop('use_absolute_page_urls'),
            kwargs.pop('add_sub_menus_inline', settings.DEFAULT_ADD_SUB_MENUS_INLINE),
            kwargs.pop('parent_page', None),
            kwargs.pop('handle', None),  # for AbstractFlatMenu
            kwargs.pop('template_name', ''),
            kwargs.pop('sub_menu_template_name', ''),
            kwargs.pop('sub_menu_template_names', None),
            kwargs  # anything left over will be stored as 'extra'
        )

    @classmethod
    def create_from_collected_values(cls, contextual_vals, option_vals):
        """
        When the menu class in not model-based, this method is called by
        ``render_from_tag()`` to 'create' a menu object appropriate
        for the provided contextual and option values.
        """
        raise NotImplementedError(
            "Subclasses of 'Menu' must define their own "
            "'create_from_collected_values' method."
        )

    @classmethod
    def get_from_collected_values(cls, contextual_vals, option_vals):
        """
        When the menu class also subclasses django.db.models.Model, this
        method is called by ``render_from_tag()`` to 'get' a menu object
        appropriate for the provided contextual and option values.
        """
        raise NotImplementedError(
            "Subclasses of 'Menu' and 'django.db.models.Model' must define "
            "their own 'get_from_collected_values' method."
        )

    def prepare_to_render(self, request, contextual_vals, option_vals):
        """
        Before calling ``render_to_template()``, this method is called to give
        the instance opportunity to prepare itself. For example,
        ``AbstractMainMenu`` and ``AbstractFlatMenu`` must to set the object's
        ``max_levels`` value to whatever was specified in ``option_vals``.

        By default, a reference to the 'contextual_vals' and 'option_vals'
        namedtumples prepared by the class in ``render_from_template()`` are
        set as private attributes on the instance, making those values
        available to other instance methods. ``set_request()`` is also called
        to make the current HttpRequest available as ``self.request``.
        """
        self._contextual_vals = contextual_vals
        self._option_vals = option_vals
        self.set_request(request)

    def render_to_template(self):
        """
        Render the current menu instance to a template and return a string
        """
        context_data = self.get_context_data()
        template = self.get_template()

        context_data['current_template'] = template.template.name
        return template.render(context_data)

    def get_common_hook_kwargs(self, **kwargs):
        """
        Returns a dictionary of common values to be passed as keyword
        arguments to methods registered as 'hooks'.
        """
        opt_vals = self._option_vals
        hook_kwargs = self._contextual_vals._asdict()
        hook_kwargs.update({
            'menu_instance': self,
            'menu_tag': self.related_templatetag_name,
            'parent_page': None,
            'max_levels': self.max_levels,
            'apply_active_classes': opt_vals.apply_active_classes,
            'allow_repeating_parents': opt_vals.allow_repeating_parents,
            'use_absolute_page_urls': opt_vals.use_absolute_page_urls,
        })
        if hook_kwargs['original_menu_instance'] is None:
            hook_kwargs['original_menu_instance'] = self
        hook_kwargs.update(kwargs)
        return hook_kwargs

    @cached_property
    def common_hook_kwargs(self):
        return self.get_common_hook_kwargs()

    def set_request(self, request):
        """
        Set `self.request` to the supplied HttpRequest, so that developers can
        make use of it
        """
        self.request = request

    def get_base_page_queryset(self):
        qs = Page.objects.filter(live=True, expired=False, show_in_menus=True)
        # allow hooks to modify the queryset
        for hook in hooks.get_hooks('menus_modify_base_page_queryset'):
            qs = hook(qs, **self.common_hook_kwargs)
        return qs

    def get_pages_for_display(self):
        raise NotImplementedError(
            "Subclasses of 'Menu' must define their own "
            "'get_pages_for_display' method")

    @cached_property
    def pages_for_display(self):
        """Returns a dictionary of all pages needed to render the
        menu, keyed by id."""
        # using OrderedDict to preserve ordering in Python < 3.6
        return OrderedDict((p.id, p) for p in self.get_pages_for_display())

    def get_page_children_dict(self, page_qs=None):
        """
        Returns a dictionary of lists, where the keys are 'path' values for
        pages, and the value is a list of children pages for that page.
        """
        children_dict = defaultdict(list)
        for page in page_qs or self.pages_for_display.values():
            children_dict[page.path[:-page.steplen]].append(page)
        return children_dict

    @cached_property
    def page_children_dict(self):
        return self.get_page_children_dict()

    def get_children_for_page(self, page):
        """Return a list of relevant child pages for a given page."""
        return self.page_children_dict.get(page.path, [])

    def page_has_children(self, page):
        """
        Return a boolean indicating whether a given page has any relevant
        child pages.
        """
        return page.path in self.page_children_dict

    def get_sub_menu_class(self):
        """
        Called by the 'sub_menu' tag to identify which menu class to use for
        rendering when 'self' is the original menu instance.
        """
        return self.sub_menu_class or SubMenu

    def create_sub_menu(self, parent_page):
        ctx_vals = self._contextual_vals
        menu_class = self.get_sub_menu_class()
        context = self.create_dict_from_parent_context()
        context.update(ctx_vals._asdict())
        if not ctx_vals.original_menu_instance and ctx_vals.current_level == 1:
            context['original_menu_instance'] = self
        option_vals = self._option_vals._asdict()
        option_vals.update({
            'parent_page': parent_page,
            'max_levels': self.max_levels,
        })
        return menu_class._get_render_prepared_object(context, **option_vals)

    def create_dict_from_parent_context(self):
        parent_context = self._contextual_vals.parent_context

        try:
            # Django template engine (or similar) Context
            return parent_context.flatten()
        except AttributeError:
            pass

        try:
            # Jinja2 Context
            return parent_context.get_all()
        except AttributeError:
            pass

        if isinstance(parent_context, dict):
            return parent_context.copy()

        return {}

    def get_context_data(self, **kwargs):
        """
        Return a dictionary containing all of the values needed to render the
        menu instance to a template, including values that might be used by
        the 'sub_menu' tag to render any additional levels.
        """
        ctx_vals = self._contextual_vals
        opt_vals = self._option_vals
        data = self.create_dict_from_parent_context()
        data.update(ctx_vals._asdict())
        data.update({
            'apply_active_classes': opt_vals.apply_active_classes,
            'allow_repeating_parents': opt_vals.allow_repeating_parents,
            'use_absolute_page_urls': opt_vals.use_absolute_page_urls,
            'max_levels': self.max_levels,
            'menu_instance': self,
            self.menu_instance_context_name: self,
            # Repeat some vals with backwards-compatible keys
            'section_root': data['current_section_root_page'],
            'current_ancestor_ids': data['current_page_ancestor_ids'],
        })
        if not ctx_vals.original_menu_instance and ctx_vals.current_level == 1:
            data['original_menu_instance'] = self
        if 'menu_items' not in kwargs:
            data['menu_items'] = self.get_menu_items_for_rendering()
        data.update(kwargs)
        return data

    def get_menu_items_for_rendering(self):
        """
        Return a list of 'menu items' to be included in the context for
        rendering the current level of the menu.

        The responsibility for sourcing, priming, and modifying menu items is
        split between three methods: ``get_raw_menu_items()``,
        ``prime_menu_items()`` and ``modify_menu_items()``, respectively.
        """
        items = self.get_raw_menu_items()

        # Allow hooks to modify the raw list
        for hook in hooks.get_hooks('menus_modify_raw_menu_items'):
            items = hook(items, **self.common_hook_kwargs)

        # Prime and modify the menu items accordingly
        items = self.modify_menu_items(self.prime_menu_items(items))
        if isinstance(items, GeneratorType):
            items = list(items)

        # Allow hooks to modify the primed/modified list
        hook_methods = hooks.get_hooks('menus_modify_primed_menu_items')
        for hook in hook_methods:
            items = hook(items, **self.common_hook_kwargs)
        return items

    items = property(get_menu_items_for_rendering)

    def get_raw_menu_items(self):
        """
        Returns a python list of ``Page`` on ``MenuItem`` objects that will
        serve as the basis of the menu items for current level.
        """
        raise NotImplementedError("Subclasses of 'Menu' must define their own "
                                  "'get_raw_menu_items' method")

    def _prime_menu_item(self, item):
        ctx_vals = self._contextual_vals
        option_vals = self._option_vals
        current_site = ctx_vals.current_site
        current_page = ctx_vals.current_page
        request = self.request
        stop_at_this_level = ctx_vals.current_level >= self.max_levels
        item_is_menu_item_object = isinstance(item, MenuItem)

        # ---------------------------------------------------------------------
        # Establish whether this item 'is' or 'links to' a page
        # ---------------------------------------------------------------------

        if item_is_menu_item_object:
            item_is_page_object = False
            page = item.link_page
        else:
            item_is_page_object = isinstance(item, Page)
            page = item if item_is_page_object else None

        # ---------------------------------------------------------------------
        # Special handling for 'LinkPage' objects
        # ---------------------------------------------------------------------

        if item_is_page_object and issubclass(item.specific_class, AbstractLinkPage):

            if not item.show_in_menus_custom(
                request=request,
                current_site=current_site,
                menu_instance=self,
                original_menu_tag=ctx_vals.original_menu_tag,
            ):
                # This item shouldn't be displayed
                return

            item.active_class = item.extra_classes
            item.text = item.menu_text(request)
            if option_vals.use_absolute_page_urls:
                item.href = item.get_full_url(request=request)
            else:
                item.href = item.relative_url(current_site, request)
            return item

        # ---------------------------------------------------------------------
        # Determine appropriate value for 'has_children_in_menu'
        # ---------------------------------------------------------------------

        # NOTE: Attributes aren't being set yet, as the item could potentially
        # be replaced

        has_children_in_menu = False

        if page:
            if (
                not stop_at_this_level and
                page.depth >= settings.SECTION_ROOT_DEPTH and
                (not item_is_menu_item_object or item.allow_subnav)
            ):
                if hasattr(page, 'has_submenu_items'):
                    has_children_in_menu = page.has_submenu_items(
                        menu_instance=self,
                        request=request,
                        allow_repeating_parents=option_vals.allow_repeating_parents,
                        current_page=current_page,
                        original_menu_tag=ctx_vals.original_menu_tag,
                    )
                else:
                    has_children_in_menu = self.page_has_children(page)

        # ---------------------------------------------------------------------
        # Determine appropriate value for 'active_class'
        # ---------------------------------------------------------------------

        # NOTE: Attributes aren't being set yet, as the item could potentially
        # be replaced

        active_class = ''

        if option_vals.apply_active_classes:
            if page:
                if(current_page and page.pk == current_page.pk):
                    # This is the current page, so the menu item should
                    # probably have the 'active' class
                    active_class = settings.ACTIVE_CLASS
                    if (
                        option_vals.allow_repeating_parents and
                        has_children_in_menu
                    ):
                        if getattr(page, 'repeat_in_subnav', False):
                            active_class = settings.ACTIVE_ANCESTOR_CLASS

                elif page.pk in ctx_vals.current_page_ancestor_ids:
                    active_class = settings.ACTIVE_ANCESTOR_CLASS
            else:
                # This is a `MenuItem` for a custom URL
                active_class = item.get_active_class_for_request(request)

        # ---------------------------------------------------------------------
        # Set 'text' attribute
        # ---------------------------------------------------------------------

        if item_is_menu_item_object:
            item.text = item.menu_text
        else:
            item.text = getattr(item, settings.PAGE_FIELD_FOR_MENU_ITEM_TEXT, item.title)

        # ---------------------------------------------------------------------
        # Set 'href' attribute
        # ---------------------------------------------------------------------

        if option_vals.use_absolute_page_urls:
            item.href = item.get_full_url(request=request)
        else:
            item.href = item.relative_url(current_site, request=request)

        # ---------------------------------------------------------------------
        # Set additional attributes
        # ---------------------------------------------------------------------

        item.has_children_in_menu = has_children_in_menu
        item.active_class = active_class

        if item.has_children_in_menu and option_vals.add_sub_menus_inline:
            item.sub_menu = self.create_sub_menu(page)
        else:
            item.sub_menu = None

        return item

    def prime_menu_items(self, menu_items):
        """
        A generator method that takes a list of ``MenuItem`` or ``Page``
        objects and sets a number of additional attributes on each item that
        are useful in menu templates.
        """
        for item in menu_items:
            item = self._prime_menu_item(item)
            if item is not None:
                yield item

    def modify_menu_items(self, menu_items):
        """
        Returns a python list of objects that will form the basis of the
        menu items for current level.
        """
        return menu_items

    def get_template(self):
        template_name = self._option_vals.template_name or self.template_name

        if template_name:
            return get_template(template_name)

        return select_template(self.get_template_names())

    def get_template_names(self):
        """Return a list (or tuple) of template names to search for when
        rendering an instance of this class. The list should be ordered
        with most specific names first, since the first template found to
        exist will be used for rendering."""
        site = self._contextual_vals.current_site
        template_names = []
        menu_str = self.menu_short_name
        if settings.SITE_SPECIFIC_TEMPLATE_DIRS and site:
            hostname = site.hostname
            template_names.extend([
                "menus/%s/%s/level_1.html" % (hostname, menu_str),
                "menus/%s/%s/menu.html" % (hostname, menu_str),
                "menus/%s/%s_menu.html" % (hostname, menu_str),
            ])
        template_names.extend([
            "menus/%s/level_1.html" % menu_str,
            "menus/%s/menu.html" % menu_str,
        ])
        lstn = self.get_least_specific_template_name()
        if lstn:
            template_names.append(lstn)
        return template_names

    @classmethod
    def get_least_specific_template_name(cls):
        """Return a template name to be added to the end of the list returned
        by 'get_template_names'. This is defined as a separate method because
        template lists tend to follow a similar pattern, except the last
        item, which typically comes from an overridable setting."""
        return


class MenuFromPage(Menu):
    """
    A menu class who's menu items are (by default) just descendant pages of a
    specific page. The 'parent page' from which the menu items descend might be
    supplied as an option value to the tag, or the menu class might identify it
    from values present in the parent context. However identified, the page
    will be used to figure out which pages to prefetch, and will also be given
    the opportunity to modify the first level of items before they are sent to
    a template for rendering (if it has a 'modify_submenu_items()' method).
    """

    def get_parent_page_for_menu_items(self):
        """
        Returns the 'parent page' from which all of menu items for this menu
        descend. Override this method to change which page is used.
        """
        raise NotImplementedError(
            "Subclasses of 'MenuFromPage' must define a "
            "'get_parent_page_for_menu_items()' method")

    @cached_property
    def parent_page_for_menu_items(self):
        """
        In case the 'get_parent_page_for_menu_items()' method is resource
        intensive, this decorated method is used so that the 'parent page' only
        needs to be fetched once
        """
        return self.get_parent_page_for_menu_items()

    def get_pages_for_display(self):
        """Returns a queryset of all pages needed to render the menu."""
        parent_page = self.parent_page_for_menu_items
        queryset = self.get_base_page_queryset().filter(
            path__startswith=parent_page.path,
            depth__lte=parent_page.depth + self.max_levels,
        )
        # Always return 'specific' page instances
        return queryset.specific()

    def get_children_for_page(self, page):
        """Returns a list of relevant child pages for a given page"""
        return super().get_children_for_page(page)

    def get_raw_menu_items(self):
        parent_page = self.parent_page_for_menu_items
        return list(self.get_children_for_page(parent_page))

    def modify_menu_items(self, menu_items):
        """
        If the 'parent page' has a 'modify_submenu_items()' method, send the
        menu items to that for further modification and return the modified
        result.

        The supplied ``menu_items`` might be a GeneratorType instance returned
        by 'prime_menu_items()' or a list.

        Subclasses of ``MenuFromPage`` are responsible for ensuring the page is
        'specific' by this point if it needs to be. (The 'modify_submenu_items'
        method will not be present on a vanilla ``Page`` instances).
        """
        parent_page = self.parent_page_for_menu_items
        modifier_method = getattr(parent_page, 'modify_submenu_items', None)
        if not modifier_method:
            return menu_items

        ctx_vals = self._contextual_vals
        opt_vals = self._option_vals
        kwargs = {
            'request': self.request,
            'menu_instance': self,
            'original_menu_tag': ctx_vals.original_menu_tag,
            'current_site': ctx_vals.current_site,
            'current_page': ctx_vals.current_page,
            'current_ancestor_ids': ctx_vals.current_page_ancestor_ids,
            'allow_repeating_parents': opt_vals.allow_repeating_parents,
            'apply_active_classes': opt_vals.apply_active_classes,
            'use_absolute_page_urls': opt_vals.use_absolute_page_urls,
        }
        if isinstance(menu_items, GeneratorType):
            # 'modify_submenu_items' methods expect 'menu_items' to be a list
            menu_items = list(menu_items)
        return modifier_method(menu_items, **kwargs)

    def get_common_hook_kwargs(self, **kwargs):
        hook_kwargs = {'parent_page': self.parent_page_for_menu_items}
        hook_kwargs.update(kwargs)
        return super().get_common_hook_kwargs(**hook_kwargs)


class SectionMenu(DefinesSubMenuTemplatesMixin, MenuFromPage):
    menu_short_name = 'section'  # used to find templates
    menu_instance_context_name = 'section_menu'
    related_templatetag_name = 'section_menu'

    @classmethod
    def render_from_tag(
        cls, context, show_section_root=True, max_levels=None,
        apply_active_classes=True, allow_repeating_parents=True,
        use_absolute_page_urls=False, add_sub_menus_inline=None,
        template_name='', sub_menu_template_name='',
        sub_menu_template_names=None, **kwargs
    ):
        return super().render_from_tag(
            context,
            show_section_root=show_section_root,
            max_levels=max_levels,
            apply_active_classes=apply_active_classes,
            allow_repeating_parents=allow_repeating_parents,
            use_absolute_page_urls=use_absolute_page_urls,
            add_sub_menus_inline=add_sub_menus_inline,
            template_name=template_name,
            sub_menu_template_name=sub_menu_template_name,
            sub_menu_template_names=sub_menu_template_names,
            **kwargs
        )

    @classmethod
    def create_from_collected_values(cls, contextual_vals, option_vals):
        if not contextual_vals.current_section_root_page:
            return
        return cls(
            root_page=contextual_vals.current_section_root_page,
            max_levels=option_vals.max_levels,
        )

    @classmethod
    def get_least_specific_template_name(cls):
        return settings.DEFAULT_SECTION_MENU_TEMPLATE

    def __init__(self, root_page, max_levels):
        self.root_page = root_page
        self.max_levels = max_levels
        super().__init__()

    def prepare_to_render(self, request, contextual_vals, option_vals):
        super().prepare_to_render(request, contextual_vals, option_vals)
        root_page = self.root_page.specific

        root_page.text = getattr(
            root_page, settings.PAGE_FIELD_FOR_MENU_ITEM_TEXT,
            root_page.title
        )
        if option_vals.use_absolute_page_urls:
            href = root_page.get_full_url(request=self.request)
        else:
            href = root_page.relative_url(contextual_vals.current_site)
        root_page.href = href

        active_class = ''
        if option_vals.apply_active_classes:
            current_page = contextual_vals.current_page
            if current_page and root_page.id == current_page.id:
                if getattr(root_page, 'repeat_in_subnav', False):
                    active_class = settings.ACTIVE_ANCESTOR_CLASS
                else:
                    active_class = settings.ACTIVE_CLASS
            elif root_page.id in contextual_vals.current_page_ancestor_ids:
                active_class = settings.ACTIVE_ANCESTOR_CLASS
        root_page.active_class = active_class
        self.root_page = root_page

    def get_parent_page_for_menu_items(self):
        return self.root_page

    def get_context_data(self, **kwargs):
        data = {
            'show_section_root': self._option_vals.extra['show_section_root'],
            'section_root': self.root_page,
        }
        data.update(kwargs)
        return super().get_context_data(**data)


class ChildrenMenu(DefinesSubMenuTemplatesMixin, MenuFromPage):
    menu_short_name = 'children'  # used to find templates
    menu_instance_context_name = 'children_menu'
    related_templatetag_name = 'children_menu'

    @classmethod
    def render_from_tag(
        cls, context, parent_page, max_levels=None,
        apply_active_classes=True, allow_repeating_parents=True,
        use_absolute_page_urls=False, add_sub_menus_inline=None,
        template_name='', sub_menu_template_name='',
        sub_menu_template_names=None, **kwargs
    ):
        return super().render_from_tag(
            context,
            parent_page=parent_page,
            max_levels=max_levels,
            apply_active_classes=apply_active_classes,
            allow_repeating_parents=allow_repeating_parents,
            use_absolute_page_urls=use_absolute_page_urls,
            add_sub_menus_inline=add_sub_menus_inline,
            template_name=template_name,
            sub_menu_template_name=sub_menu_template_name,
            sub_menu_template_names=sub_menu_template_names,
            **kwargs
        )

    @classmethod
    def create_from_collected_values(cls, contextual_vals, option_vals):
        parent_page = option_vals.parent_page or contextual_vals.current_page
        if not parent_page:
            return
        return cls(
            max_levels=option_vals.max_levels,
            parent_page=parent_page,
        )

    @classmethod
    def get_least_specific_template_name(cls):
        return settings.DEFAULT_CHILDREN_MENU_TEMPLATE

    def __init__(self, parent_page, max_levels):
        self.parent_page = parent_page
        self.max_levels = max_levels
        super().__init__()

    def get_parent_page_for_menu_items(self):
        return self.parent_page

    def get_context_data(self, **kwargs):
        data = {'parent_page': self.parent_page}
        data.update(kwargs)
        return super().get_context_data(**data)


class SubMenu(MenuFromPage):
    menu_short_name = 'sub'  # used to find templates
    menu_instance_context_name = 'sub_menu'
    related_templatetag_name = 'sub_menu'

    @classmethod
    def render_from_tag(
        cls, context, parent_page, max_levels=None,
        apply_active_classes=True, allow_repeating_parents=True,
        use_absolute_page_urls=False, add_sub_menus_inline=False,
        template_name='', **kwargs
    ):
        return super().render_from_tag(
            context,
            parent_page=parent_page,
            max_levels=max_levels,
            apply_active_classes=apply_active_classes,
            allow_repeating_parents=allow_repeating_parents,
            use_absolute_page_urls=use_absolute_page_urls,
            add_sub_menus_inline=add_sub_menus_inline,
            template_name=template_name,
            **kwargs
        )

    @classmethod
    def create_from_collected_values(cls, contextual_vals, option_vals):
        return cls(
            original_menu=contextual_vals.original_menu_instance,
            parent_page=option_vals.parent_page,
            max_levels=option_vals.max_levels,
        )

    def __init__(self, original_menu, parent_page, max_levels):
        self.original_menu = original_menu
        self.page_children_dict = original_menu.page_children_dict
        self.parent_page = parent_page
        self.max_levels = max_levels

    def get_parent_page_for_menu_items(self):
        return self.parent_page

    def get_raw_menu_items(self):
        """Overrides the 'MenuFromPage' version, because sub menus are powered
        by page data, which is prefetched by the the original menu instance.
        """
        return self.original_menu.get_children_for_page(self.parent_page)

    def get_template(self):
        if self._option_vals.template_name or self.template_name:
            return super().get_template()
        return self.original_menu.get_sub_menu_template(
            level=self._contextual_vals.current_level
        )

    def get_context_data(self, **kwargs):
        data = {'parent_page': self.parent_page}
        data.update(kwargs)
        return super().get_context_data(**data)


class MenuWithMenuItems(ClusterableModel, Menu):
    """A base model class for menus who's 'menu_items' are defined by
    a set of 'menu item' model instances."""
    menu_items_relation_setting_name = None

    class Meta:
        abstract = True

    @classmethod
    def _get_site(cls, context):
        site = super()._get_site(context)
        if site is not None:
            return site
        try:
            return Site.objects.get()
        except MultipleObjectsReturned:
            raise RequestUnavailableError(
                f"In multisite projects, menus of type '{cls.__name__}' can "
                "only be identified when the current HttpRequest is "
                "available to the menu tag. If you are rendering menus "
                "from within a streamfield block, try using Wagtail's "
                "{% include_block %} tag to render streamfield values, "
                "which passes ``request`` and other values through to the "
                "block template context."
            )

    @classmethod
    def _get_menu_items_related_name(cls):
        return getattr(settings, cls.menu_items_relation_setting_name)

    def get_base_menuitem_queryset(self):
        qs = self.get_menu_items_manager().for_display()

        # Prefetch minimal page values only. The rest will be
        # fetched by get_pages_for_display()
        qs = qs.select_related('link_page').defer(*[
            'link_page__{}'.format(f.name) for f in Page._meta.get_fields()
            if f.concrete and f.name not in ('id', 'path', 'depth')
        ])

        # allow hooks to modify the queryset
        for hook in hooks.get_hooks('menus_modify_base_menuitem_queryset'):
            qs = hook(qs, **self.common_hook_kwargs)
        return qs

    def get_menu_items_manager(self):
        relationship_name = self._get_menu_items_related_name()
        try:
            return getattr(self, relationship_name)
        except AttributeError:
            raise ImproperlyConfigured(
                "'%s' isn't a valid relationship name for accessing menu "
                "items from %s. Check that your `%s` setting matches the "
                "`related_name` used on your MenuItem model's `ParentalKey` "
                "field." % (
                    relationship_name,
                    self.__class__.__name__,
                    self.menu_items_relation_setting_name
                )
            )

    def get_top_level_items(self):
        """Return a list of menu items with prefetched `link_page` values"""

        menu_items = self.get_base_menuitem_queryset()
        # allow this query result to be reused by get_pages_for_display()
        self._raw_menu_items = menu_items

        top_level_items = []
        for item in menu_items:

            # Non-page links are always included
            if not item.link_page_id:
                top_level_items.append(item)
                continue

            # But, we only want to include links to pages if the page was
            # in the get_pages_for_display() result
            try:
                item.link_page = self.pages_for_display[item.link_page_id]
                top_level_items.append(item)
            except KeyError:
                continue
        return top_level_items

    @cached_property
    def top_level_items(self):
        return self.get_top_level_items()

    def get_pages_for_display(self):
        """Returns a queryset of all pages needed to render the menu."""

        if hasattr(self, '_raw_menu_items'):
            # get_top_level_items() may have set this
            menu_items = self._raw_menu_items
        else:
            menu_items = self.get_base_menuitem_queryset()

        # Start with an empty queryset, and expand as needed
        queryset = Page.objects.none()

        for item in (item for item in menu_items if item.link_page):
            if(
                item.allow_subnav and
                item.link_page.depth >= settings.SECTION_ROOT_DEPTH
            ):
                # Add this branch to the overall `queryset`
                queryset = queryset | Page.objects.filter(
                    path__startswith=item.link_page.path,
                    depth__lt=item.link_page.depth + self.max_levels,
                )
            else:
                # Add this page only to the overall `queryset`
                queryset = queryset | Page.objects.filter(id=item.link_page_id)

        # Filter out pages unsutable display
        queryset = self.get_base_page_queryset() & queryset

        # Always return 'specific' page instances
        return queryset.specific()

    def add_menu_items_for_pages(self, pagequeryset=None, allow_subnav=True):
        """Add menu items to this menu, linking to each page in `pagequeryset`
        (which should be a PageQuerySet instance)"""
        item_manager = self.get_menu_items_manager()
        item_class = item_manager.model
        item_list = []
        i = item_manager.count()
        for p in pagequeryset.all():
            item_list.append(item_class(
                menu=self, link_page=p, sort_order=i, allow_subnav=allow_subnav
            ))
            i += 1
        item_manager.bulk_create(item_list)

    def prepare_to_render(self, request, contextual_vals, option_vals):
        if option_vals.max_levels is not None:
            self.max_levels = option_vals.max_levels
        super().prepare_to_render(request, contextual_vals, option_vals)

    def get_raw_menu_items(self):
        return self.top_level_items

    def get_context_data(self, **kwargs):
        data = {
            'max_levels': self.max_levels,
        }
        data.update(kwargs)
        return super().get_context_data(**data)

    settings_panels = panels.menu_settings_panels


# ########################################################
# Abstract models
# ########################################################

class AbstractMainMenu(DefinesSubMenuTemplatesMixin, MenuWithMenuItems):
    menu_short_name = 'main'  # used to find templates
    menu_instance_context_name = 'main_menu'
    related_templatetag_name = 'main_menu'
    content_panels = panels.main_menu_content_panels
    menu_items_relation_setting_name = 'MAIN_MENU_ITEMS_RELATED_NAME'

    site = models.OneToOneField(
        'wagtailcore.Site',
        verbose_name=_('site'),
        db_index=True,
        editable=False,
        on_delete=models.CASCADE,
        related_name="+",
    )
    max_levels = models.PositiveSmallIntegerField(
        verbose_name=_('maximum levels'),
        choices=constants.MAX_LEVELS_CHOICES,
        default=2,
        help_text=mark_safe_lazy(_(
            "The maximum number of levels to display when rendering this "
            "menu. The value can be overidden by supplying a different "
            "<code>max_levels</code> value to the <code>{% main_menu %}"
            "</code> tag in your templates."
        ))
    )

    class Meta:
        abstract = True
        verbose_name = _("main menu")
        verbose_name_plural = _("main menu")

    @classmethod
    def render_from_tag(
        cls, context, max_levels=None, apply_active_classes=True,
        allow_repeating_parents=True, use_absolute_page_urls=False,
        add_sub_menus_inline=False, template_name='',
        sub_menu_template_name='', sub_menu_template_names=None, **kwargs
    ):
        return super().render_from_tag(
            context,
            max_levels=max_levels,
            apply_active_classes=apply_active_classes,
            allow_repeating_parents=allow_repeating_parents,
            use_absolute_page_urls=use_absolute_page_urls,
            add_sub_menus_inline=add_sub_menus_inline,
            template_name=template_name,
            sub_menu_template_name=sub_menu_template_name,
            sub_menu_template_names=sub_menu_template_names,
            **kwargs
        )

    @classmethod
    def get_from_collected_values(cls, contextual_vals, option_vals):
        try:
            return cls.get_for_site(contextual_vals.current_site)
        except cls.DoesNotExist:
            return

    @classmethod
    def get_for_site(cls, site):
        """Return the 'main menu' instance for the provided site"""
        instance, created = cls.objects.get_or_create(site=site)
        return instance

    @classmethod
    def get_least_specific_template_name(cls):
        return settings.DEFAULT_MAIN_MENU_TEMPLATE

    def __str__(self):
        return _('Main menu for %(site_name)s') % {
            'site_name': self.site.site_name or self.site
        }


class AbstractFlatMenu(DefinesSubMenuTemplatesMixin, MenuWithMenuItems):
    menu_short_name = 'flat'  # used to find templates
    menu_instance_context_name = 'flat_menu'
    related_templatetag_name = 'flat_menu'
    base_form_class = forms.FlatMenuAdminForm
    content_panels = panels.flat_menu_content_panels
    menu_items_relation_setting_name = 'FLAT_MENU_ITEMS_RELATED_NAME'

    site = models.ForeignKey(
        Site,
        verbose_name=_('site'),
        db_index=True,
        on_delete=models.CASCADE,
        related_name='+'
    )
    title = models.CharField(
        verbose_name=_('title'),
        max_length=255,
        help_text=_("For internal reference only.")
    )
    handle = models.SlugField(
        verbose_name=_('handle'),
        max_length=100,
        help_text=_(
            "Used to reference this menu in templates etc. Must be unique "
            "for the selected site."
        )
    )
    heading = models.CharField(
        verbose_name=_('heading'),
        max_length=255,
        blank=True,
        help_text=_("If supplied, appears above the menu when rendered.")
    )
    max_levels = models.PositiveSmallIntegerField(
        verbose_name=_('maximum levels'),
        choices=constants.MAX_LEVELS_CHOICES,
        default=1,
        help_text=mark_safe_lazy(_(
            "The maximum number of levels to display when rendering this "
            "menu. The value can be overidden by supplying a different "
            "<code>max_levels</code> value to the <code>{% flat_menu %}"
            "</code> tag in your templates."
        ))
    )

    class Meta:
        abstract = True
        unique_together = ("site", "handle")
        verbose_name = _("flat menu")
        verbose_name_plural = _("flat menus")

    @classmethod
    def render_from_tag(
        cls, context, handle, fall_back_to_default_site_menus=True,
        max_levels=None, apply_active_classes=True,
        allow_repeating_parents=True, use_absolute_page_urls=False,
        add_sub_menus_inline=False, template_name='',
        sub_menu_template_name='', sub_menu_template_names=None, **kwargs
    ):
        return super().render_from_tag(
            context,
            handle=handle,
            fall_back_to_default_site_menus=fall_back_to_default_site_menus,
            max_levels=max_levels,
            apply_active_classes=apply_active_classes,
            allow_repeating_parents=allow_repeating_parents,
            use_absolute_page_urls=use_absolute_page_urls,
            add_sub_menus_inline=add_sub_menus_inline,
            template_name=template_name,
            sub_menu_template_name=sub_menu_template_name,
            sub_menu_template_names=sub_menu_template_names,
            **kwargs
        )

    @classmethod
    def get_from_collected_values(cls, contextual_vals, option_vals):
        try:
            return cls.get_for_site(
                option_vals.handle,
                contextual_vals.current_site,
                option_vals.extra['fall_back_to_default_site_menus']
            )
        except cls.DoesNotExist:
            return

    @classmethod
    def get_for_site(cls, handle, site, fall_back_to_default_site_menus=False):
        """Return a FlatMenu instance with a matching ``handle`` for the
        provided ``site``, or for the default site (if suitable). If no
        match is found, returns None."""
        queryset = cls.objects.filter(handle__exact=handle)

        site_q = Q(site=site)
        if fall_back_to_default_site_menus:
            site_q |= Q(site__is_default_site=True)
        queryset = queryset.filter(site_q)

        # return the best match or None
        return queryset.annotate(matched_provided_site=Case(
            When(site_id=site.id, then=1), default=0,
            output_field=BooleanField()
        )).order_by('-matched_provided_site').first()

    @classmethod
    def get_least_specific_template_name(cls):
        return settings.DEFAULT_FLAT_MENU_TEMPLATE

    def __str__(self):
        return '%s (%s)' % (self.title, self.handle)

    def get_heading(self):
        return self.heading

    def get_context_data(self, **kwargs):
        data = {
            'menu_heading': self.get_heading(),
            'menu_handle': self.handle,
            'show_menu_heading': self._option_vals.extra['show_menu_heading'],
            # The below is added for backwards compatibility
            'matched_menu': self,
        }
        data.update(kwargs)
        return super().get_context_data(**data)

    def get_template_names(self):
        """Returns a list of template names to search for when rendering a
        a specific flat menu object (making use of self.handle)"""
        site = self._contextual_vals.current_site
        handle = self.handle
        template_names = []
        if settings.SITE_SPECIFIC_TEMPLATE_DIRS and site:
            hostname = site.hostname
            template_names.extend([
                "menus/%s/flat/%s/level_1.html" % (hostname, handle),
                "menus/%s/flat/%s/menu.html" % (hostname, handle),
                "menus/%s/flat/%s.html" % (hostname, handle),
                "menus/%s/%s/level_1.html" % (hostname, handle),
                "menus/%s/%s/menu.html" % (hostname, handle),
                "menus/%s/%s.html" % (hostname, handle),
                "menus/%s/flat/level_1.html" % hostname,
                "menus/%s/flat/default.html" % hostname,
                "menus/%s/flat/menu.html" % hostname,
                "menus/%s/flat_menu.html" % hostname,
            ])
        template_names.extend([
            "menus/flat/%s/level_1.html" % handle,
            "menus/flat/%s/menu.html" % handle,
            "menus/flat/%s.html" % handle,
            "menus/%s/level_1.html" % handle,
            "menus/%s/menu.html" % handle,
            "menus/%s.html" % handle,
            "menus/flat/level_1.html",
            "menus/flat/default.html",
            "menus/flat/menu.html",
        ])
        lstn = self.get_least_specific_template_name()
        if lstn:
            template_names.append(lstn)
        return template_names

    def get_sub_menu_template_names(self, level=2):
        """Returns a list of template names to search for when rendering a
        a sub menu for a specific flat menu object (making use of self.handle)
        """
        site = self._contextual_vals.current_site
        handle = self.handle
        template_names = []
        if settings.SITE_SPECIFIC_TEMPLATE_DIRS and site:
            hostname = site.hostname
            template_names.extend([
                "menus/%s/flat/%s/level_%s.html" % (hostname, handle, level),
                "menus/%s/flat/%s/sub_menu.html" % (hostname, handle),
                "menus/%s/flat/%s_sub_menu.html" % (hostname, handle),
                "menus/%s/%s/level_%s.html" % (hostname, handle, level),
                "menus/%s/%s/sub_menu.html" % (hostname, handle),
                "menus/%s/%s_sub_menu.html" % (hostname, handle),
                "menus/%s/flat/level_%s.html" % (hostname, level),
                "menus/%s/flat/sub_menu.html" % hostname,
                "menus/%s/sub_menu.html" % hostname,
            ])
        template_names.extend([
            "menus/flat/%s/level_%s.html" % (handle, level),
            "menus/flat/%s/sub_menu.html" % handle,
            "menus/flat/%s_sub_menu.html" % handle,
            "menus/%s/level_%s.html" % (handle, level),
            "menus/%s/sub_menu.html" % handle,
            "menus/%s_sub_menu.html" % handle,
            "menus/flat/level_%s.html" % level,
            "menus/flat/sub_menu.html",
            settings.DEFAULT_SUB_MENU_TEMPLATE,
        ])
        return template_names


# ########################################################
# Concrete models
# ########################################################

class MainMenu(AbstractMainMenu):
    """The default model for 'main menu' instances."""
    pass


class FlatMenu(AbstractFlatMenu):
    """The default model for 'flat menu' instances."""
    pass
