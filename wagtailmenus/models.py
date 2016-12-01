from __future__ import absolute_import, unicode_literals

from collections import defaultdict
from copy import copy

from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.forms import WagtailAdminModelForm
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, PageChooserPanel, MultiFieldPanel, InlinePanel)
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailsearch import index

from wagtailmenus import app_settings
from .managers import MenuItemManager
from .panels import menupage_settings_panels


class MenuPage(Page):
    repeat_in_subnav = models.BooleanField(
        verbose_name=_("repeat in sub-navigation"),
        default=False,
        help_text=_(
            "If checked, a link to this page will be repeated alongside it's "
            "direct children when displaying a sub-navigation for this page."
        ),
    )
    repeated_item_text = models.CharField(
        verbose_name=_('repeated item link text'),
        max_length=255,
        blank=True,
        help_text=_(
            "e.g. 'Section home' or 'Overview'. If left blank, the page title "
            "will be used."
        )
    )

    settings_panels = menupage_settings_panels

    class Meta:
        abstract = True

    def modify_submenu_items(self, menu_items, current_page,
                             current_ancestor_ids, current_site,
                             allow_repeating_parents, apply_active_classes,
                             original_menu_tag, menu_instance=None):
        """
        Make any necessary modifications to `menu_items` and return the list
        back to the calling menu tag to render in templates. Any additional
        items added should have a `text` and `href` attribute as a minimum.

        `original_menu_tag` should be one of 'main_menu', 'section_menu' or
        'children_menu', which should be useful when extending/overriding.
        """
        if (allow_repeating_parents and menu_items and self.repeat_in_subnav):
            """
            This page should have a version of itself repeated alongside
            children in the subnav, so we create a new item and prepend it to
            menu_items.
            """
            extra = copy(self)
            setattr(extra, 'text', self.repeated_item_text or self.title)
            setattr(extra, 'href', self.relative_url(current_site))
            active_class = ''
            if(apply_active_classes and self == current_page):
                active_class = app_settings.ACTIVE_CLASS
            setattr(extra, 'active_class', active_class)

            menu_items.insert(0, extra)

        return menu_items

    def has_submenu_items(self, current_page, allow_repeating_parents,
                          original_menu_tag, menu_instance=None):
        """
        When rendering pages in a menu template a `has_children_in_menu`
        attribute is added to each page, letting template developers know
        whether or not the item has a submenu that must be rendered.

        By default, we return a boolean indicating whether the page has
        suitable child pages to include in such a menu. But, if you are
        overriding the `modify_submenu_items` method to programatically add
        items that aren't child pages, you'll likely need to alter this method
        too, so the template knows there are sub items to be rendered.
        """
        if menu_instance:
            return menu_instance.page_has_children(self)
        return self.get_children().live().in_menu().exists()


@python_2_unicode_compatible
class MenuItem(models.Model):
    allow_subnav = False

    link_page = models.ForeignKey(
        'wagtailcore.Page',
        verbose_name=_('link to an internal page'),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    link_url = models.CharField(
        verbose_name=_('link to a custom URL'),
        max_length=255,
        blank=True,
        null=True,
    )
    link_text = models.CharField(
        verbose_name=_('link text'),
        max_length=255,
        blank=True,
        help_text=_("Must be set if you wish to link to a custom URL."),
    )
    handle = models.CharField(
        verbose_name=_('handle'),
        max_length=100,
        blank=True,
        help_text=_(
            "Use this field to optionally specify an additional value for "
            "each menu item, which you can then reference in custom menu "
            "templates."
        )
    )
    url_append = models.CharField(
        verbose_name=_("append to URL"),
        max_length=255,
        blank=True,
        help_text=_(
            "Use this to optionally append a #hash or querystring to the "
            "above page's URL."
        )
    )

    objects = MenuItemManager()

    class Meta:
        abstract = True
        verbose_name = _("menu item")
        verbose_name_plural = _("menu items")

    @property
    def menu_text(self):
        return self.link_text or self.link_page.title

    def relative_url(self, site=None):
        if self.link_page:
            return self.link_page.relative_url(site) + self.url_append
        return self.link_url + self.url_append

    def clean(self, *args, **kwargs):
        super(MenuItem, self).clean(*args, **kwargs)

        if self.link_url and not self.link_text:
            raise ValidationError({
                'link_text': [
                    _("This must be set if you're linking to a custom URL."),
                ]
            })

        if not self.link_url and not self.link_page:
            raise ValidationError({
                'link_url': [
                    _("This must be set if you're not linking to a page."),
                ]
            })

        if self.link_url and self.link_page:
            raise ValidationError(_(
                "You cannot link to both a page and URL. Please review your "
                "link and clear any unwanted values."
            ))

    def __str__(self):
        return self.menu_text

    panels = (
        PageChooserPanel('link_page'),
        FieldPanel('link_url'),
        FieldPanel('url_append'),
        FieldPanel('link_text'),
        FieldPanel('handle'),
        FieldPanel('allow_subnav'),
    )


class Menu(ClusterableModel):

    max_levels = 1
    use_specific = app_settings.USE_SPECIFIC_AUTO

    class Meta:
        abstract = True

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
    def top_level_items(self):
        """
        Return a list of menu_items with link_page objects supplemented with
        'specific' pages where appropriate.
        """
        items_qs = self.menu_items.for_display()
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
        """
        Returns a list of pages for rendering the entire menu (excluding those
        chosen as menu items). All pages must be live, not expired, and set to
        show in menus.
        """

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

    @cached_property
    def page_children_dict(self):
        """
        Returns a dictionary of lists, where the keys are 'path' values for
        pages, and the value is a list of children pages for that page.
        """
        children_dict = defaultdict(list)
        for page in self.pages_for_display:
            children_dict[page.path[:-page.steplen]].append(page)
        return children_dict

    def get_children_for_page(self, page):
        """Return a list of relevant child pages for a given page."""
        return self.page_children_dict.get(page.path, [])

    def page_has_children(self, page):
        """
        Return a boolean indicating whether a given page has any relevant
        child pages.
        """
        return page.path in self.page_children_dict


class MainMenu(Menu):
    site = models.OneToOneField(
        'wagtailcore.Site',
        related_name="main_menu",
        db_index=True,
        editable=False,
        on_delete=models.CASCADE
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
        verbose_name = _("main menu")
        verbose_name_plural = _("main menu")

    @classmethod
    def get_for_site(cls, site):
        """
        Get a mainmenu instance for the site.
        """
        instance, created = cls.objects.get_or_create(site=site)
        return instance

    def __str__(self):
        return _('Main menu for %s') % (self.site.site_name or self.site)

    panels = (
        InlinePanel('menu_items', label=_("menu items")),
        MultiFieldPanel(
            heading=_("Advanced settings"),
            children=(FieldPanel('max_levels'), FieldPanel('use_specific')),
            classname="collapsible collapsed",
        ),
    )


class FlatMenuAdminForm(WagtailAdminModelForm):
    def __init__(self, *args, **kwargs):
        super(FlatMenuAdminForm, self).__init__(*args, **kwargs)
        if app_settings.FLAT_MENUS_HANDLE_CHOICES:
            self.fields['handle'] = forms.ChoiceField(
                choices=app_settings.FLAT_MENUS_HANDLE_CHOICES)


class FlatMenu(Menu, index.Indexed):
    site = models.ForeignKey(
        'wagtailcore.Site',
        verbose_name=_('site'),
        related_name="flat_menus",
        db_index=True, on_delete=models.CASCADE
    )
    title = models.CharField(
        max_length=255,
        help_text=_("For internal reference only."))
    handle = models.SlugField(
        max_length=100,
        help_text=_(
            "Used to reference this menu in templates etc. Must be unique "
            "for the selected site."
        )
    )
    heading = models.CharField(
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
        unique_together = ("site", "handle")
        verbose_name = _("flat menu")
        verbose_name_plural = _("flat menus")

    @classmethod
    def get_for_site(cls, handle, site,
                     fall_back_to_default_site_menus=False):
        """
        Get a FlatMenu instance with a matching `handle` for the `site`
        provided - or for the 'default' site if not found.
        """
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

    def clean(self, *args, **kwargs):
        # Raise validation error for unique_together constraint, as it's not
        # currently handled properly by wagtail
        clashes = FlatMenu.objects.filter(site=self.site, handle=self.handle)
        if self.pk:
            clashes = clashes.exclude(pk__exact=self.pk)
        if clashes.count():
            msg = _("Site and handle must create a unique combination. A menu "
                    "already exists with these same two values.")
            raise ValidationError({
                'site': [msg],
                'handle': [msg],
            })
        super(FlatMenu, self).clean(*args, **kwargs)

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
        InlinePanel('menu_items', label=_("menu items")),
        MultiFieldPanel(
            heading=_("Advanced settings"),
            children=(FieldPanel('max_levels'), FieldPanel('use_specific')),
            classname="collapsible collapsed",
        ),
    )
    
    search_fields = [
        index.SearchField('title', partial_match = True),
        index.SearchField('handle', partial_match = True),
        index.SearchField('heading', partial_match = True),
    ]


class MainMenuItem(Orderable, MenuItem):
    menu = ParentalKey('MainMenu', related_name="menu_items")
    allow_subnav = models.BooleanField(
        verbose_name=_("allow sub-menu for this item"),
        default=True,
        help_text=_(
            "NOTE: The sub-menu might not be displayed, even if checked. "
            "It depends on how the menu is used in this project's templates."
        )
    )


class FlatMenuItem(Orderable, MenuItem):
    menu = ParentalKey('FlatMenu', related_name="menu_items")
    allow_subnav = models.BooleanField(
        verbose_name=_("allow sub-menu for this item"),
        default=False,
        help_text=_(
            "NOTE: The sub-menu might not be displayed, even if checked. "
            "It depends on how the menu is used in this project's templates."
        )
    )
