from __future__ import absolute_import, unicode_literals
import warnings

from collections import defaultdict, namedtuple
from types import GeneratorType

from django.db import models
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.template import Context
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, MultiFieldPanel, InlinePanel)
from wagtail.wagtailcore import hooks
from wagtail.wagtailcore.models import Page, PAGE_TEMPLATE_VAR

from .. import app_settings
from ..forms import FlatMenuAdminForm
from ..utils.deprecation import RemovedInWagtailMenus26Warning
from ..utils.inspection import accepts_kwarg
from ..utils.misc import get_site_from_request
from .menuitems import MenuItem
from .pages import AbstractLinkPage


ContextualVals = namedtuple('ContextualVals', (
    'parent_context', 'request', 'current_site', 'current_level',
    'menu_tag', 'original_menu_tag', 'original_menu_instance', 'current_page',
    'current_section_root_page', 'current_page_ancestor_ids', 'template_engine'
))

OptionVals = namedtuple('OptionVals', (
    'max_levels', 'use_specific', 'apply_active_classes',
    'allow_repeating_parents', 'use_absolute_page_urls', 'parent_page',
    'handle', 'template_name', 'sub_menu_template_name', 'extra'
))


# ########################################################
# Base classes
# ########################################################

class Menu(object):
    """A base class that all other 'menu' classes should inherit from."""

    max_levels = 1
    use_specific = app_settings.USE_SPECIFIC_AUTO
    pages_for_display = None
    root_page = None  # Not relevant for all menu classes
    request = None
    menu_short_name = ''  # used to find templates
    menu_instance_context_name = 'menu'
    sub_menu_class = None

    @classmethod
    def render_from_tag(cls, tag_name, context, **options):
        """
        A template tag should call this method to render menus.
        The ``Context`` instance and other data provided are used to get or
        create a relevant menu instance, prepare it, then render it to a
        an appropriate template.

        It shouldn't be neccessary to override this method, as there
        are more specific methods for overriding the certain behaviour at
        different stages of rendering, such as:

            * get_instance_for_rendering() (class method)
            * prepare_to_render()
            * render_to_template()
        """
        ctx_vals = cls.get_contextual_vals_from_context(tag_name, context)
        opt_vals = cls.get_option_vals_from_options(**options)
        instance = cls.get_instance_for_rendering(ctx_vals, opt_vals)
        if not instance:
            return ''

        instance.prepare_to_render(context['request'], ctx_vals, opt_vals)
        instance.set_request(context['request'])
        return instance.render_to_template()

    @classmethod
    def get_contextual_vals_from_context(cls, tag_name, context):
        """
        Gathers all of the 'contextual' data needed to render a menu instance
        and returns it in a structure that can be conveniently referenced
        throughout the process of preparing the menu and menu items and
        for rendering.
        """
        context_processor_vals = context.get('wagtailmenus_vals', {})
        return ContextualVals(
            context,
            context['request'],
            get_site_from_request(context['request']),
            context.get('current_level', 0) + 1,
            context.get('menu_tag', tag_name),
            context.get('original_menu_tag', tag_name),
            context.get('original_menu_instance'),
            context_processor_vals.get('current_page'),
            context_processor_vals.get('section_root'),
            context_processor_vals.get('current_page_ancestor_ids', ()),
            context.template.engine,
        )

    @classmethod
    def get_option_vals_from_options(cls, **options):
        """
        Takes all of the options passed to the class's ``render_from_tag()``
        method and returns them in a structure that can be conveniently
        referenced throughout the process of rendering.

        Any additionaly options needed for custom menu classes implementations
        should be available as a dictionary using the 'extra' key name. For
        example, when rendering a flat menu, the
        'fall_back_to_default_site_menus' option passed to the tag is available
        as:

        .. code-block:: python

            option_vals.extra['fall_back_to_default_site_menus']
        """
        return OptionVals(
            options.pop('max_levels'),
            options.pop('use_specific'),
            options.pop('apply_active_classes'),
            options.pop('allow_repeating_parents'),
            options.pop('use_absolute_page_urls'),
            options.pop('parent_page', None),  # for MenuFromRootPage
            options.pop('handle', None),  # for AbstractFlatMenu
            options.pop('template_name', ''),
            options.pop('sub_menu_template_name', ''),
            options  # anything left over will be stored as 'extra'
        )

    @classmethod
    def get_instance_for_rendering(cls, contextual_vals, option_vals):
        """
        Called by the class's ``render_from_tag()`` method to get or create a
        relevant instance to use for rendering using the available data. For
        model-based menu classes like ``AbstractMainMenu`` and
        ``AbstractFlatMenu``, this will involve fetching the correct object
        from the database. For others, a new instance should be created and
        returned.
        """
        raise NotImplementedError(
            "Subclasses of 'Menu' must define their own "
            "'get_instance_for_rendering' method")

    @classmethod
    def get_sub_menu_class(cls):
        return cls.sub_menu_class or SubMenu

    def prepare_to_render(self, request, contextual_vals, option_vals):
        """
        Before calling ``render_to_template()``, this method is called to give
        the instance opportunity to prepare itself. For example,
        ``AbstractMainMenu`` and ``AbstractFlatMenu`` needs to call
        ``set_max_levels()`` and ``set_use_specific()`` to update the
        ``max_levels`` and ``use_specific`` field values to alternative values
        passed as option values to the calling menu tag.

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
        Render the current menu instance to a template to return a string
        """
        context_data = self.get_context_data()
        template = self.get_template()
        context_data['current_template'] = template.name
        return template.render(Context(context_data))

    def clear_page_cache(self):
        try:
            del self.pages_for_display
        except AttributeError:
            pass
        try:
            del self.page_children_dict
        except AttributeError:
            pass

    def set_max_levels(self, max_levels):
        if self.max_levels != max_levels:
            """
            Set `self.max_levels` to the supplied value and clear any cached
            attribute values set for a different `max_levels` value.
            """
            self.max_levels = max_levels
            self.clear_page_cache()

    def set_use_specific(self, use_specific):
        if self.use_specific != use_specific:
            """
            Set `self.use_specific` to the supplied value and clear some
            cached values where appropriate.
            """
            if(
                use_specific >= app_settings.USE_SPECIFIC_TOP_LEVEL and
                self.use_specific < app_settings.USE_SPECIFIC_TOP_LEVEL
            ):
                self.clear_page_cache()
                try:
                    del self.top_level_items
                except AttributeError:
                    pass

            self.use_specific = use_specific

    def get_common_hook_kwargs(self, **kwargs):
        opt_vals = self._option_vals
        hook_kwargs = self._contextual_vals._asdict()
        hook_kwargs.update({
            'menu_instance': self,
            'parent_page': self.root_page,
            'max_levels': self.max_levels,
            'use_specific': self.max_levels,
            'apply_active_classes': opt_vals.apply_active_classes,
            'allow_repeating_parents': opt_vals.allow_repeating_parents,
            'use_absolute_page_urls': opt_vals.use_absolute_page_urls,
        })
        hook_kwargs.pop('template_engine')
        if hook_kwargs['original_menu_instance'] is None:
            hook_kwargs['original_menu_instance'] = self
        hook_kwargs.update(kwargs)
        return hook_kwargs

    def set_request(self, request):
        """
        Set `self.request` to the supplied HttpRequest, so that developers can
        make use of it in subclasses
        """
        self.request = request

    def get_base_page_queryset(self):
        qs = Page.objects.filter(live=True, expired=False, show_in_menus=True)
        # allow hooks to modify the queryset
        hook_methods = hooks.get_hooks('menus_modify_base_page_queryset')
        if hook_methods:
            hook_kwargs = self.get_common_hook_kwargs()
            for hook in hook_methods:
                qs = hook(qs, **hook_kwargs)
        return qs

    def get_pages_for_display(self):
        raise NotImplementedError(
            "Subclasses of 'Menu' must define their own "
            "'get_pages_for_display' method")

    @cached_property
    def pages_for_display(self):
        return self.get_pages_for_display()

    def get_page_children_dict(self, page_qs=None):
        """Returns a dictionary of lists, where the keys are 'path' values for
        pages, and the value is a list of children pages for that page."""
        children_dict = defaultdict(list)
        for page in page_qs or self.pages_for_display:
            children_dict[page.path[:-page.steplen]].append(page)
        return children_dict

    @cached_property
    def page_children_dict(self):
        return self.get_page_children_dict()

    def get_children_for_page(self, page):
        """Return a list of relevant child pages for a given page."""
        return self.page_children_dict.get(page.path, [])

    def page_has_children(self, page):
        """Return a boolean indicating whether a given page has any relevant
        child pages."""
        return page.path in self.page_children_dict

    def get_context_data(self, **kwargs):
        ctx_vals = self._contextual_vals
        opt_vals = self._option_vals

        data = ctx_vals.parent_context.flatten()
        data.update(ctx_vals._asdict())
        data.update({
            'sub_menu_class': self.get_sub_menu_class(),
            'apply_active_classes': opt_vals.apply_active_classes,
            'allow_repeating_parents': opt_vals.allow_repeating_parents,
            'use_absolute_page_urls': opt_vals.use_absolute_page_urls,
            'max_levels': self.max_levels,
            'use_specific': self.use_specific,
            'menu_instance': self,
            self.menu_instance_context_name: self,
            # Repeat some vals with backwards-compatible keys
            'section_root': data['current_section_root_page'],
            'current_ancestor_ids': data['current_page_ancestor_ids'],
        })
        if 'menu_items' not in kwargs:
            data['menu_items'] = self.get_menu_items_for_rendering()
        data.update(kwargs)
        return data

    def get_menu_items_for_rendering(self):
        """
        Return a list of 'menu items' to be included in the context for
        rendering the current level of the menu.

        The responsibility for sourcing, priming, and modifying menu items is
        split between 3 methods: ``get_raw_menu_items()``,
        ``prime_menu_items()`` and ``modify_menu_items()`` (respectively).
        """
        items = self.get_raw_menu_items()
        hook_kwargs = self.get_common_hook_kwargs()

        # Allow hooks to modify the raw list
        for hook in hooks.get_hooks('menus_modify_raw_menu_items'):
            items = hook(items, **hook_kwargs)

        # Prime and modify the menu items accordingly
        items = self.modify_menu_items(self.prime_menu_items(items))
        if isinstance(items, GeneratorType):
            items = list(items)

        # Allow hooks to modify the primed/modified list
        hook_methods = hooks.get_hooks('menus_modify_primed_menu_items')
        for hook in hook_methods:
            items = hook(items, **hook_kwargs)
        return items

    def get_raw_menu_items(self):
        raise NotImplementedError("Subclasses of 'Menu' must define their own "
                                  "'get_raw_menu_items' method")

    def modify_menu_items(self, menu_items):
        return menu_items

    def prime_menu_items(self, menu_items):
        """
        Prepare a list of `MenuItem` or `Page` objects for rendering to a menu
        template.
        """
        ctx_vals = self._contextual_vals
        opt_vals = self._option_vals
        current_site = ctx_vals.current_site
        current_page = ctx_vals.current_page
        apply_active_classes = opt_vals.apply_active_classes
        allow_repeating_parents = opt_vals.allow_repeating_parents
        active_css_class = app_settings.ACTIVE_CLASS
        ancestor_css_class = app_settings.ACTIVE_ANCESTOR_CLASS
        stop_at_this_level = (ctx_vals.current_level >= self.max_levels)

        for item in menu_items:

            if isinstance(item, MenuItem):
                """
                `menu_items` is a list of `MenuItem` objects from
                `Menu.top_level_items`. Any `link_page` values will have been
                replaced with specific pages if necessary
                """
                page = item.link_page
                menuitem = item
                setattr(item, 'text', item.menu_text)

            elif issubclass(item.specific_class, AbstractLinkPage):
                """
                Special treatment for link pages
                """
                if type(item) is Page:
                    item = item.specific
                if item.show_in_menus_custom(
                    current_site,
                    self,
                    ctx_vals.original_menu_tag
                ):
                    setattr(item, 'active_class', item.extra_classes)
                    setattr(item, 'text', item.menu_text(self.request))
                    if self._option_vals.use_absolute_page_urls:
                        url = item.get_full_url(request=self.request)
                    else:
                        url = item.relative_url(current_site, self.request)
                    setattr(item, 'href', url)
                    yield item
                continue

            else:
                """
                `menu_items` is a list of `Page` objects
                """
                page = item
                menuitem = None
                text = getattr(
                    page,
                    app_settings.PAGE_FIELD_FOR_MENU_ITEM_TEXT,
                    page.title
                )
                setattr(item, 'text', text)

            if page:
                """
                Work out whether this item should be flagged as needing
                a sub-menu. It can be expensive, so we try to only do the
                working out when absolutely necessary.
                """
                has_children_in_menu = False
                if (
                    not stop_at_this_level and
                    page.depth >= app_settings.SECTION_ROOT_DEPTH and
                    (menuitem is None or menuitem.allow_subnav)
                ):
                    if (
                        self.use_specific and (
                            hasattr(page, 'has_submenu_items') or
                            hasattr(page.specific_class, 'has_submenu_items')
                        )
                    ):
                        if type(page) is Page:
                            page = page.specific
                        """
                        If the page has a `has_submenu_items` method, give
                        responsibilty for determining `has_children_in_menu`
                        to that.
                        """
                        has_children_in_menu = page.has_submenu_items(
                            menu_instance=self,
                            request=self.request,
                            allow_repeating_parents=allow_repeating_parents,
                            current_page=ctx_vals.current_page,
                            original_menu_tag=ctx_vals.original_menu_tag,
                        )

                    else:
                        has_children_in_menu = self.page_has_children(page)

                setattr(item, 'has_children_in_menu', has_children_in_menu)

                if apply_active_classes:
                    active_class = ''
                    if(current_page and page.pk == current_page.pk):
                        # This is the current page, so the menu item should
                        # probably have the 'active' class
                        active_class = active_css_class
                        if (
                            allow_repeating_parents and
                            self.use_specific and
                            has_children_in_menu
                        ):
                            if type(page) is Page:
                                page = page.specific
                            if getattr(page, 'repeat_in_subnav', False):
                                active_class = ancestor_css_class
                    elif page.pk in ctx_vals.current_page_ancestor_ids:
                        active_class = ancestor_css_class
                    setattr(item, 'active_class', active_class)

            elif page is None:
                """
                This is a `MenuItem` for a custom URL. It can be classed as
                'active' if the URL matches the request path.
                """
                request_path = self.request.path
                if apply_active_classes and item.link_url == request_path:
                    setattr(item, 'active_class', app_settings.ACTIVE_CLASS)

            # In case the specific page was fetched during the above operations
            # We'll set `MenuItem.link_page` to that specific page.
            if menuitem and page:
                menuitem.link_page = page

            if opt_vals.use_absolute_page_urls:
                # Pages only have `get_full_url` from Wagtail 1.11 onwards
                if hasattr(item, 'get_full_url'):
                    url = item.get_full_url(request=self.request)
                # Fallback for Wagtail versions prior to 1.11
                else:
                    url = item.full_url
            else:
                # Both `Page` and `MenuItem` objects have a `relative_url`
                # method that we can use to calculate a value for the `href`
                # attribute
                url = item.relative_url(current_site)
            setattr(item, 'href', url)
            yield item

    def get_template(self):
        e = self._contextual_vals.template_engine
        specified = self._option_vals.template_name
        if specified:
            return e.get_template(specified)
        if hasattr(self, 'template_name'):
            return e.get_template(self.template_name)
        return e.select_template(self.get_template_names())

    def get_template_names(self):
        """Return a list (or tuple) of template names to search for when
        rendering an instance of this class. The list should be ordered
        with most specific names first, since the first template found to
        exist will be used for rendering"""
        site = self._contextual_vals.current_site
        template_names = []
        menu_str = self.menu_short_name
        if app_settings.SITE_SPECIFIC_TEMPLATE_DIRS and site:
            hostname = site.hostname
            template_names.extend([
                "menus/%s/%s/menu.html" % (hostname, menu_str),
                "menus/%s/%s_menu.html" % (hostname, menu_str),
            ])
        template_names.append("menus/%s/menu.html" % menu_str)
        lstn = self.get_least_specific_template_name()
        if lstn:
            template_names.append(lstn)
        return template_names

    @classmethod
    def get_least_specific_template_name(cls):
        """Return a template name to be added to the end of the list returned
        by 'get_template_names'. This is defined as a separate method because
        template lists tend to follow a similar pattern, except the last
        item, which typically comes from a setting"""
        return


class MultiLevelMenu(Menu):

    def get_sub_menu_template(self):
        e = self._contextual_vals.template_engine
        specified = self._option_vals.sub_menu_template_name
        if specified:
            return e.get_template(specified)
        return e.select_template(self.get_sub_menu_template_names())

    @cached_property
    def sub_menu_template(self):
        return self.get_sub_menu_template()

    def get_sub_menu_template_names(self):
        """Return a list of template paths/names to search when
        rendering a sub menu for an instance of this class. The list should be
        ordered with most specific names first, since the first template found
        to exist will be used for rendering"""
        current_site = self._contextual_vals.current_site
        template_names = []
        menu_str = self.menu_short_name
        if app_settings.SITE_SPECIFIC_TEMPLATE_DIRS and current_site:
            hostname = current_site.hostname
            template_names.extend([
                "menus/%s/%s/sub_menu.html" % (hostname, menu_str),
                "menus/%s/%s_sub_menu.html" % (hostname, menu_str),
                "menus/%s/sub_menu.html" % hostname,
            ])
        template_names.extend([
            "menus/%s/sub_menu.html" % menu_str,
            "menus/%s_sub_menu.html" % menu_str,
            app_settings.DEFAULT_SUB_MENU_TEMPLATE,
        ])
        return template_names

    def get_context_data(self, **kwargs):
        """
        First-level MultiLevelMenus always add themselves to the context as
        'original_menu_instance', which will stay present in the context
        throughout the process of rendering multiple levels. This is important,
        as it allow sub menus to access the page data that was prefetched when
        the original menu was created. If there's a possibility that sub menus
        might be neded, the template used to render those sub menus is also
        prefetched and added to the context, so that it only needs to happen
        once.
        """
        data = {}
        if self._contextual_vals.current_level == 1:
            data['original_menu_instance'] = self
            if self.max_levels > 1:
                data['sub_menu_template'] = self.sub_menu_template.name
        data.update(kwargs)
        return super(MultiLevelMenu, self).get_context_data(**data)


class MenuFromRootPage(MultiLevelMenu):
    """A 'menu' that is instantiated with a 'root page', and whose 'menu items'
    consist solely of ancestors of that page."""

    root_page = None
    root_page_context_name = 'root_page'

    @classmethod
    def get_instance_for_rendering(cls, contextual_vals, option_vals):
        parent_page = cls.identify_parent_page_from_vals(
            contextual_vals, option_vals)
        return cls(
            parent_page, option_vals.max_levels, option_vals.use_specific)

    @classmethod
    def identify_parent_page_from_vals(cls, contextual_vals, option_vals):
        parent_context = contextual_vals.parent_context
        return option_vals.parent_page or parent_context.get('self') or \
            parent_context.get(PAGE_TEMPLATE_VAR)

    def __init__(self, root_page, max_levels, use_specific):
        self.root_page = root_page
        self.max_levels = max_levels
        self.use_specific = use_specific
        super(MenuFromRootPage, self).__init__()

    def render_to_template(self):
        if not self.root_page:
            return ''
        return super(MenuFromRootPage, self).render_to_template()

    def get_pages_for_display(self):
        """Return all pages needed for rendering all sub-levels for the current
        menu"""
        pages = self.get_base_page_queryset().filter(
            depth__gt=self.root_page.depth,
            depth__lte=self.root_page.depth + self.max_levels,
            path__startswith=self.root_page.path,
        )

        # Return 'specific' page instances if required
        if(self.use_specific == app_settings.USE_SPECIFIC_ALWAYS):
            return pages.specific()

        return pages

    def get_children_for_page(self, page):
        """Return a list of relevant child pages for a given page."""
        if self.max_levels == 1:
            # If there's only a single level of pages to display, skip the
            # dict creation / lookup and just return the QuerySet result
            return self.pages_for_display
        return super(MenuFromRootPage, self).get_children_for_page(page)

    def get_raw_menu_items(self):
        return list(self.get_children_for_page(self.root_page))

    def get_context_data(self, **kwargs):
        data = {self.root_page_context_name: self.root_page}
        data.update(**kwargs)
        return super(MenuFromRootPage, self).get_context_data(**data)

    def modify_menu_items(self, menu_items):
        """
        If the menu's root_page has a ``modify_submenu_items`` method, send
        ``menu_items`` to that method for further modification.
        """
        root = self.root_page
        if not self.use_specific or not hasattr(root, 'modify_submenu_items'):
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
        # Backwards compatibility for 'modify_submenu_items' methods that
        # don't accept a 'use_absolute_page_urls' kwarg
        if not accepts_kwarg(
            root.modify_submenu_items, 'use_absolute_page_urls'
        ):
            kwargs.pop('use_absolute_page_urls')
            warning_msg = (
                "The 'modify_submenu_items' method on '%s' should be "
                "updated to accept a 'use_absolute_page_urls' keyword "
                "argument. View the 2.4 release notes for more info: "
                "https://github.com/rkhleics/wagtailmenus/releases/tag/v.2.4.0"
                % root.__class__.__name__,
            )
            warnings.warn(warning_msg, RemovedInWagtailMenus26Warning)

        # Call `modify_submenu_items` using the above kwargs dict
        return root.modify_submenu_items(list(menu_items), **kwargs)


class SectionMenu(MenuFromRootPage):
    menu_short_name = 'section'  # used to find templates
    menu_instance_context_name = 'section_menu'

    @classmethod
    def identify_parent_page_from_vals(cls, contextual_vals, option_vals):
        return contextual_vals.current_section_root_page

    @classmethod
    def get_least_specific_template_name(cls):
        return app_settings.DEFAULT_SECTION_MENU_TEMPLATE

    def prepare_to_render(self, request, contextual_vals, option_vals):
        super(SectionMenu, self).prepare_to_render(
            request, contextual_vals, option_vals)

        if self.use_specific and type(self.root_page) is Page and (
            contextual_vals.current_level == 1 and
            hasattr(self.root_page.specific_class, 'modify_submenu_items')
        ) or (
            contextual_vals.current_level == 1 and
            self.use_specific >= app_settings.USE_SPECIFIC_TOP_LEVEL
        ):
            self.root_page = self.root_page.specific

    def get_context_data(self, **kwargs):
        ctx_vals = self._contextual_vals
        opt_vals = self._option_vals
        section_root = self.root_page
        current_page = ctx_vals.current_page
        active_css_class = app_settings.ACTIVE_CLASS
        ancestor_css_class = app_settings.ACTIVE_ANCESTOR_CLASS

        data = super(SectionMenu, self).get_context_data()
        data['show_section_root'] = opt_vals.extra['show_section_root']

        if 'section_root' not in kwargs:
            section_root.text = getattr(
                section_root, app_settings.PAGE_FIELD_FOR_MENU_ITEM_TEXT,
                section_root.title
            )
            if opt_vals.use_absolute_page_urls:
                if hasattr(section_root, 'get_full_url'):
                    url = section_root.get_full_url(request=self.request)
                else:
                    url = section_root.full_url
            else:
                url = section_root.relative_url(ctx_vals.current_site)
            section_root.href = url

            if opt_vals.apply_active_classes:
                active_class = ancestor_css_class
                if current_page and section_root.pk == current_page.pk:
                    # `section_root` is the current page, so should probably
                    # have the 'active' class
                    active_class = active_css_class
                    menu_items = data['menu_items']
                    # Unless there's a 'repeated item' in menu_items that
                    # already has the 'active' class
                    if(
                        opt_vals.allow_repeating_parents and self.use_specific
                    ):
                        for item in menu_items:
                            css_class = getattr(item, 'active_class', '')
                            if(
                                css_class == active_css_class and
                                getattr(item, 'pk', 0) == section_root.pk
                            ):
                                active_class = ancestor_css_class
                section_root.active_class = active_class

        data['section_root'] = section_root
        data.update(**kwargs)
        return data


class ChildrenMenu(MenuFromRootPage):
    menu_short_name = 'children'  # used to find templates
    menu_instance_context_name = 'children_menu'
    root_page_context_name = 'parent_page'

    @classmethod
    def get_least_specific_template_name(cls):
        return app_settings.DEFAULT_CHILDREN_MENU_TEMPLATE


class SubMenu(MenuFromRootPage):
    menu_short_name = 'sub'  # used to find templates
    menu_instance_context_name = 'sub_menu'
    root_page_context_name = 'parent_page'

    def prepare_to_render(self, request, contextual_vals, option_vals):
        super(SubMenu, self).prepare_to_render(
            request, contextual_vals, option_vals)
        self.original_menu = option_vals.extra['original_menu']

    def get_template(self):
        if self._option_vals.template_name:
            return super(SubMenu, self).get_template()
        return self.original_menu.sub_menu_template

    def get_raw_menu_items(self):
        if self.original_menu:
            return self.original_menu.get_children_for_page(self.root_page)
        return self.get_children_for_page(self.root_page)


class MenuWithMenuItems(ClusterableModel, MultiLevelMenu):
    """A base model class for menus who's 'menu_items' are defined by
    a set of 'menu item' model instances."""

    class Meta:
        abstract = True

    def get_base_menuitem_queryset(self):
        qs = self.get_menu_items_manager().for_display()
        # allow hooks to modify the queryset
        for hook in hooks.get_hooks('menus_modify_base_menuitem_queryset'):
            common_kwargs = self.get_common_hook_kwargs()
            qs = hook(qs, **common_kwargs)
        return qs

    @cached_property
    def top_level_items(self):
        return self.get_top_level_items()

    def get_top_level_items(self):
        """Return a list of menu items with link_page objects supplemented with
        'specific' pages where appropriate."""
        menu_items = self.get_base_menuitem_queryset()

        # Identify which pages to fetch for the top level items. We use
        # 'get_base_page_queryset' here, so that if that's being overridden
        # or modified by hooks, any pages being excluded there are also
        # excluded at the top level
        top_level_pages = self.get_base_page_queryset().filter(
            id__in=menu_items.values_list('link_page_id', flat=True)
        )
        if self.use_specific >= app_settings.USE_SPECIFIC_TOP_LEVEL:
            """
            The menu is being generated with a specificity level of TOP_LEVEL
            or ALWAYS, so we use PageQuerySet.specific() to fetch specific
            page instances as efficiently as possible
            """
            top_level_pages = top_level_pages.specific()

        # Evaluate the above queryset to a dictionary, using the IDs as keys
        pages_dict = {p.id: p for p in top_level_pages}

        # Now build a list to return
        menu_item_list = []
        for item in menu_items:
            if not item.link_page_id:
                menu_item_list.append(item)
                continue  # skip to next
            if item.link_page_id in pages_dict.keys():
                # Only return menu items for pages where the page was included
                # in the 'get_base_page_queryset' result
                item.link_page = pages_dict.get(item.link_page_id)
                menu_item_list.append(item)
        return menu_item_list

    def get_pages_for_display(self):
        """Return all pages needed for rendering all sub-levels for the current
        menu"""

        # Start with an empty queryset, and expand as needed
        all_pages = Page.objects.none()

        if self.max_levels == 1:
            # If no additional sub-levels are needed, return empty queryset
            return all_pages

        for item in self.top_level_items:

            if item.link_page_id:
                # Fetch a 'branch' of suitable descendants for this item and
                # add to 'all_pages'
                page_depth = item.link_page.depth
                if(
                    item.allow_subnav and
                    page_depth >= app_settings.SECTION_ROOT_DEPTH
                ):
                    all_pages = all_pages | Page.objects.filter(
                        depth__gt=page_depth,
                        depth__lt=page_depth + self.max_levels,
                        path__startswith=item.link_page.path)

        # Filter the entire queryset to include only pages suitable for display
        all_pages = all_pages & self.get_base_page_queryset()

        # Return 'specific' page instances if required
        if self.use_specific == app_settings.USE_SPECIFIC_ALWAYS:
            return all_pages.specific()

        return all_pages

    def get_menu_items_manager(self):
        raise NotImplementedError(
            "Subclasses of 'MenuWithMenuItems' must define their own "
            "'get_menu_items_manager' method")

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

    def get_context_data(self, **kwargs):
        data = {
            'max_levels': self.max_levels,
            'use_specific': self.use_specific,
        }
        data.update(kwargs)
        return super(MenuWithMenuItems, self).get_context_data(**data)

    def get_raw_menu_items(self):
        return self.top_level_items

    def prepare_to_render(self, request, contextual_vals, option_vals):
        if option_vals.max_levels is not None:
            self.set_max_levels(option_vals.max_levels)
        if option_vals.use_specific is not None:
            self.set_use_specific(option_vals.use_specific)
        super(MenuWithMenuItems, self).prepare_to_render(
            request, contextual_vals, option_vals)


# ########################################################
# Abstract models
# ########################################################

@python_2_unicode_compatible
class AbstractMainMenu(MenuWithMenuItems):
    menu_short_name = 'main'  # used to find templates
    menu_instance_context_name = 'main_menu'

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
        choices=app_settings.MAX_LEVELS_CHOICES,
        default=2,
        help_text=mark_safe(_(
            "The maximum number of levels to display when rendering this "
            "menu. The value can be overidden by supplying a different "
            "<code>max_levels</code> value to the <code>{% main_menu %}"
            "</code> tag in your templates."
        ))
    )
    use_specific = models.PositiveSmallIntegerField(
        verbose_name=_('specific page usage'),
        choices=app_settings.USE_SPECIFIC_CHOICES,
        default=app_settings.USE_SPECIFIC_AUTO,
        help_text=mark_safe(_(
            "Controls how 'specific' pages objects are fetched and used when "
            "rendering this menu. This value can be overidden by supplying a "
            "different <code>use_specific</code> value to the <code>"
            "{% main_menu %}</code> tag in your templates."
        ))
    )

    class Meta:
        abstract = True
        verbose_name = _("main menu")
        verbose_name_plural = _("main menu")

    @classmethod
    def get_instance_for_rendering(cls, contextual_vals, option_vals):
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
        return app_settings.DEFAULT_MAIN_MENU_TEMPLATE

    def __str__(self):
        return _('Main menu for %(site_name)s') % {
            'site_name': self.site.site_name or self.site
        }

    def get_menu_items_manager(self):
        try:
            return getattr(self, app_settings.MAIN_MENU_ITEMS_RELATED_NAME)
        except AttributeError:
            raise ImproperlyConfigured(
                "'%s' isn't a valid relationship name for accessing menu "
                "items from %s. Check that your "
                "`WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME` setting matches "
                "the `related_name` used on your MenuItem model's "
                "`ParentalKey` field." % (
                    app_settings.MAIN_MENU_ITEMS_RELATED_NAME,
                    self.__class__.__name__
                )
            )

    panels = (
        InlinePanel(
            app_settings.MAIN_MENU_ITEMS_RELATED_NAME, label=_("menu items")
        ),
        MultiFieldPanel(
            heading=_("Advanced settings"),
            children=(FieldPanel('max_levels'), FieldPanel('use_specific')),
            classname="collapsible collapsed",
        ),
    )


@python_2_unicode_compatible
class AbstractFlatMenu(MenuWithMenuItems):
    menu_short_name = 'flat'  # used to find templates
    menu_instance_context_name = 'flat_menu'

    site = models.ForeignKey(
        'wagtailcore.Site',
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
        choices=app_settings.MAX_LEVELS_CHOICES,
        default=1,
        help_text=mark_safe(_(
            "The maximum number of levels to display when rendering this "
            "menu. The value can be overidden by supplying a different "
            "<code>max_levels</code> value to the <code>{% flat_menu %}"
            "</code> tag in your templates."
        ))
    )
    use_specific = models.PositiveSmallIntegerField(
        verbose_name=_('specific page usage'),
        choices=app_settings.USE_SPECIFIC_CHOICES,
        default=app_settings.USE_SPECIFIC_AUTO,
        help_text=mark_safe(_(
            "Controls how 'specific' pages objects are fetched and used when "
            "rendering this menu. This value can be overidden by supplying a "
            "different <code>use_specific</code> value to the <code>"
            "{% flat_menu %}</code> tag in your templates."
        ))
    )

    base_form_class = FlatMenuAdminForm

    class Meta:
        abstract = True
        unique_together = ("site", "handle")
        verbose_name = _("flat menu")
        verbose_name_plural = _("flat menus")

    @classmethod
    def get_instance_for_rendering(cls, contextual_vals, option_vals):
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
        """Get a FlatMenu instance with a matching `handle` for the `site`
        provided - or for the 'default' site if not found."""
        menu = cls.objects.filter(handle__exact=handle, site=site).first()
        if(
            menu is None and fall_back_to_default_site_menus and
            not site.is_default_site
        ):
            return cls.objects.filter(
                handle__exact=handle, site__is_default_site=True
            ).first()
        return menu

    @classmethod
    def get_least_specific_template_name(cls):
        return app_settings.DEFAULT_FLAT_MENU_TEMPLATE

    def __str__(self):
        return '%s (%s)' % (self.title, self.handle)

    def clean(self, *args, **kwargs):
        """Raise validation error for unique_together constraint, as it's not
        currently handled properly by wagtail."""

        clashes = self.__class__.objects.filter(site=self.site,
                                                handle=self.handle)
        if self.pk:
            clashes = clashes.exclude(pk__exact=self.pk)
        if clashes.exists():
            msg = _("Site and handle must create a unique combination. A menu "
                    "already exists with these same two values.")
            raise ValidationError({
                'site': [msg],
                'handle': [msg],
            })
        super(AbstractFlatMenu, self).clean(*args, **kwargs)

    def get_menu_items_manager(self):
        try:
            return getattr(self, app_settings.FLAT_MENU_ITEMS_RELATED_NAME)
        except AttributeError:
            raise ImproperlyConfigured(
                "'%s' isn't a valid relationship name for accessing menu "
                "items from %s. Check that your "
                "`WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME` setting matches "
                "the `related_name` used on your MenuItem model's "
                "`ParentalKey` field." % (
                    app_settings.FLAT_MENU_ITEMS_RELATED_NAME,
                    self.__class__.__name__
                )
            )

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
        return super(AbstractFlatMenu, self).get_context_data(**data)

    def get_template_names(self):
        """Returns a list of template names to search for when rendering a
        a specific flat menu object (making use of self.handle)"""
        site = self._contextual_vals.current_site
        template_names = []
        if app_settings.SITE_SPECIFIC_TEMPLATE_DIRS and site:
            hn = site.hostname
            template_names.extend([
                "menus/%s/flat/%s/menu.html" % (hn, self.handle),
                "menus/%s/flat/%s.html" % (hn, self.handle),
                "menus/%s/%s/menu.html" % (hn, self.handle),
                "menus/%s/%s.html" % (hn, self.handle),
                "menus/%s/flat/menu.html" % hn,
                "menus/%s/flat/default.html" % hn,
                "menus/%s/flat_menu.html" % hn,
            ])
        template_names.extend([
            "menus/flat/%s/menu.html" % self.handle,
            "menus/flat/%s.html" % self.handle,
            "menus/%s/menu.html" % self.handle,
            "menus/%s.html" % self.handle,
            "menus/flat/default.html",
            "menus/flat/menu.html",
        ])
        lstn = self.get_least_specific_template_name()
        if lstn:
            template_names.append(lstn)
        return template_names

    def get_sub_menu_template_names(self):
        """Returns a list of template names to search for when rendering a
        a sub menu for a specific flat menu object (making use of self.handle)
        """
        site = self._contextual_vals.current_site
        template_names = []
        if app_settings.SITE_SPECIFIC_TEMPLATE_DIRS and site:
            hn = site.hostname
            template_names.extend([
                "menus/%s/flat/%s/sub_menu.html" % (hn, self.handle),
                "menus/%s/flat/%s_sub_menu.html" % (hn, self.handle),
                "menus/%s/%s/sub_menu.html" % (hn, self.handle),
                "menus/%s/%s_sub_menu.html" % (hn, self.handle),
                "menus/%s/flat/sub_menu.html" % hn,
                "menus/%s/sub_menu.html" % hn,
            ])
        template_names.extend([
            "menus/flat/%s/sub_menu.html" % self.handle,
            "menus/flat/%s_sub_menu.html" % self.handle,
            "menus/%s/sub_menu.html" % self.handle,
            "menus/%s_sub_menu.html" % self.handle,
            "menus/flat/sub_menu.html",
            app_settings.DEFAULT_SUB_MENU_TEMPLATE,
        ])
        return template_names

    panels = (
        MultiFieldPanel(
            heading=_("Settings"),
            children=(
                FieldPanel('title'),
                FieldPanel('site'),
                FieldPanel('handle'),
                FieldPanel('heading'),
            )
        ),
        InlinePanel(
            app_settings.FLAT_MENU_ITEMS_RELATED_NAME, label=_("menu items")
        ),
        MultiFieldPanel(
            heading=_("Advanced settings"),
            children=(FieldPanel('max_levels'), FieldPanel('use_specific')),
            classname="collapsible collapsed",
        ),
    )


# ########################################################
# Concrete models
# ########################################################

class MainMenu(AbstractMainMenu):
    """The default model for 'main menu' instances."""
    pass


class FlatMenu(AbstractFlatMenu):
    """The default model for 'flat menu' instances."""
    pass
