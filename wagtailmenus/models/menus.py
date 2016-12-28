from __future__ import absolute_import, unicode_literals

from collections import defaultdict

from django.db import models
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from modelcluster.models import ClusterableModel

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, MultiFieldPanel, InlinePanel)
from wagtail.wagtailcore.models import Page

from .. import app_settings
from ..forms import FlatMenuAdminForm


# ########################################################
# Base classes
# ########################################################

class Menu(object):
    """A base class that all other 'menu' classes should inherit from."""

    max_levels = 1
    use_specific = app_settings.USE_SPECIFIC_AUTO
    pages_for_display = None

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

    @cached_property
    def page_children_dict(self):
        """Returns a dictionary of lists, where the keys are 'path' values for
        pages, and the value is a list of children pages for that page."""
        children_dict = defaultdict(list)
        for page in self.pages_for_display:
            children_dict[page.path[:-page.steplen]].append(page)
        return children_dict

    def get_children_for_page(self, page):
        """Return a list of relevant child pages for a given page."""
        return self.page_children_dict.get(page.path, [])

    def page_has_children(self, page):
        """Return a boolean indicating whether a given page has any relevant
        child pages."""
        return page.path in self.page_children_dict


class MenuFromRootPage(Menu):
    """A 'menu' that is instantiated with a 'root page', and whose 'menu items'
    consist solely of ancestors of that page."""

    root_page = None

    def __init__(self, root_page, max_levels, use_specific):
        self.root_page = root_page
        self.max_levels = max_levels
        self.use_specific = use_specific
        super(MenuFromRootPage, self).__init__()

    @cached_property
    def pages_for_display(self):
        """Returns a list of pages for rendering all levels of the menu. All
        pages must be live, not expired, and set to show in menus."""
        pages = Page.objects.filter(
            depth__gt=self.root_page.depth,
            depth__lte=self.root_page.depth + self.max_levels,
            path__startswith=self.root_page.path,
            live=True,
            expired=False,
            show_in_menus=True,
        )

        # Return 'specific' page instances if required
        if self.use_specific == app_settings.USE_SPECIFIC_ALWAYS:
            return pages.specific()

        return pages

    def get_children_for_page(self, page):
        """Return a list of relevant child pages for a given page."""
        if self.max_levels == 1:
            # If there's only a single level of pages to display, skip the
            # dict creation / lookup and just return the QuerySet result
            return self.pages_for_display
        return super(MenuFromRootPage, self).get_children_for_page(page)


class MenuWithMenuItems(ClusterableModel, Menu):
    """A base model class for menus who's 'menu_items' are defined by
    a set of 'menu item' model instances."""

    class Meta:
        abstract = True

    @cached_property
    def top_level_items(self):
        """Return a list of menu items with link_page objects supplemented with
        'specific' pages where appropriate."""
        items_qs = self.get_menu_items_manager().for_display()
        if self.use_specific < app_settings.USE_SPECIFIC_TOP_LEVEL:
            return items_qs.all()

        """
        The menu is being generated with a specificity level of TOP_LEVEL
        or ALWAYS, which means we need to replace 'link_page' values on
        MenuItem objects with their 'specific' equivalents.
        """
        updated_items = []
        for item in items_qs.all():
            if item.link_page_id:
                item.link_page = item.link_page.specific
            updated_items.append(item)
        return updated_items

    @cached_property
    def pages_for_display(self):
        """Return a list of pages for rendering the entire menu (excluding
        those chosen as menu items). All pages must be live, not expired, and
        set to show in menus."""

        # Build a queryset to get pages for all levels
        all_pages = Page.objects.none()

        if self.max_levels == 1:
            # If no additional menus are needed, return an empty queryset
            return all_pages

        for item in self.top_level_items:

            if item.link_page_id:
                # If necessary, fetch a 'branch' of suitable descendants for
                # this menu item and add to the full queryset
                page_path = item.link_page.path
                page_depth = item.link_page.depth
                if(
                    item.allow_subnav and
                    page_depth >= app_settings.SECTION_ROOT_DEPTH
                ):
                    all_pages = all_pages | Page.objects.filter(
                        depth__gt=page_depth,
                        depth__lt=page_depth + self.max_levels,
                        path__startswith=page_path)

        # Filter the queryset to include only the pages we need for display
        all_pages = all_pages.filter(
            live=True, expired=False, show_in_menus=True)

        # Return 'specific' page instances if required
        if self.use_specific == app_settings.USE_SPECIFIC_ALWAYS:
            return all_pages.specific()

        return all_pages


# ########################################################
# Abstract models
# ########################################################

@python_2_unicode_compatible
class AbstractMainMenu(MenuWithMenuItems):
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
    def get_for_site(cls, site):
        """Get a mainmenu instance for the site."""
        instance, created = cls.objects.get_or_create(site=site)
        return instance

    def __str__(self):
        return _('Main menu for %s') % (self.site.site_name or self.site)

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
    def get_for_site(cls, handle, site,
                     fall_back_to_default_site_menus=False):
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

    def __str__(self):
        return '%s (%s)' % (self.title, self.handle)

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
