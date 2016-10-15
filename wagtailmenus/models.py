from collections import defaultdict
from copy import copy

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, PageChooserPanel, MultiFieldPanel, InlinePanel)
from wagtail.wagtailcore.models import Page, Orderable

from .app_settings import (
    ACTIVE_CLASS, SECTION_ROOT_DEPTH, DEFAULT_MAIN_MENU_MAX_LEVELS,
    DEFAULT_FLAT_MENU_MAX_LEVELS
)
from .managers import MenuItemManager
from .panels import menupage_settings_panels


MAX_LEVELS_CHOICES = (
    (1, _('1: Single-level (flat)')),
    (2, _('2: One level of sub-navigation')),
    (3, _('3: Two levels of sub-navigation')),
    (4, _('4: Three levels of sub-navigation')),
)


class MenuPage(Page):
    repeat_in_subnav = models.BooleanField(
        verbose_name=_("repeat in sub-navigation"),
        help_text=_(
            "If checked, a link to this page will be repeated alongside it's "
            "direct children when displaying a sub-navigation for this page."
        ),
        default=False,
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
                             original_menu_tag):
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
                active_class = ACTIVE_CLASS
            setattr(extra, 'active_class', active_class)

            menu_items.insert(0, extra)

        return menu_items

    def has_submenu_items(self, current_page, check_for_children,
                          allow_repeating_parents, original_menu_tag,
                          menu=None):
        """
        NOTE: `check_for_children` is always True, so you can ignore it. The
        argument will be removed from this method in a later feature release.

        When rendering pages in a menu template a `has_children_in_menu`
        attribute is added to each page, letting template developers know
        whether or not the item has a submenu that must be rendered.

        By default, we return a boolean indicating whether the page has
        suitable child pages to include in such a menu. But, if you are
        overriding the `modify_submenu_items` method to programatically add
        items that aren't child pages, you'll likely need to alter this method
        too, so the template knows there are sub items to be rendered.
        """
        if menu:
            return menu.page_has_children(self)
        return self.get_children().live().in_menu().exists()


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
        max_length=255,
        verbose_name=_('link to a custom URL'),
        blank=True,
        null=True,
    )
    link_text = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Must be set if you wish to link to a custom URL."),
    )
    handle = models.CharField(
        max_length=100,
        blank=True,
        help_text=_(
            "Use this field to optionally specify an additional value for "
            "each menu item, which you can then reference in custom menu "
            "templates."))
    url_append = models.CharField(
        verbose_name=_("append to URL"),
        max_length=255,
        blank=True,
        help_text=_(
            "Use this to optionally append a #hash or querystring to the "
            "above page's URL.")
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
        FieldPanel('url_append'),
        FieldPanel('link_url'),
        FieldPanel('link_text'),
        FieldPanel('handle'),
        FieldPanel('allow_subnav'),
    )


class Menu(ClusterableModel):

    max_levels = 1

    class Meta:
        abstract = True

    def set_max_levels(self, max_levels):
        if self.max_levels != max_levels:
            """
            Set `self.max_levels` to the supplied value and clear any cached
            attribute values set for a different `max_levels` value.
            """
            self.max_levels = max_levels
            try:
                del self.pages_for_display
            except AttributeError:
                pass
            try:
                del self.page_children_dict
            except AttributeError:
                pass

    @cached_property
    def pages_for_display(self):
        """
        Returns a list of 'specific' pages for rendering the menu, including
        top-level pages (those actually chosen for menu items) and their
        descendants. All pages must be live, not expired, and set to show in
        menus.
        """
        if self.max_levels == 1:
            # Only return the top-level pages
            return Page.objects.filter(
                live=True, expired=False, show_in_menus=True,
                id__in=self.menu_items.values_list('link_page_id', flat=True)
            )

        # Build a queryset to get pages for all levels
        all_pages = Page.objects.none()
        for item in self.menu_items.page_links_for_display().values(
            'allow_subnav',
            'link_page__id',
            'link_page__path',
            'link_page__depth'
        ):
            # Identify all relevant pages for this menu item
            page_path = item['link_page__path']
            page_depth = item['link_page__depth']
            if item['allow_subnav'] and page_depth >= SECTION_ROOT_DEPTH:
                # Get the page for this menuitem and any suitable descendants
                branch_pages = Page.objects.filter(
                    depth__lt=page_depth + self.max_levels,
                    path__startswith=page_path,)
            else:
                # This is either a homepage link or a page we don't need to
                # fetch descendants for, so just include the page itself
                branch_pages = Page.objects.filter(
                    id__exact=item['link_page__id'])
            # Add this branch / page to the full tree queryset
            all_pages = all_pages | branch_pages

        # Filter out any irrelevant pages and run specific()
        return all_pages.filter(
            live=True, expired=False, show_in_menus=True).specific()

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
        """Return a list of child pages for a given page."""
        return self.page_children_dict.get(page.path, [])

    def page_has_children(self, page):
        return page.path in self.page_children_dict

    @cached_property
    def top_level_page_dict(self):
        page_dict = {}
        top_page_ids = self.menu_items.values_list('link_page_id', flat=True)
        for page in self.pages_for_display:
            if page.id in top_page_ids:
                page_dict[page.id] = page
        return page_dict

    @cached_property
    def items_for_display(self):
        """
        Return a list of menu_items with link_page objects supplemented with
        'specific' pages that must to be fetched for rendering anyway
        """
        new_items = []
        for item in self.menu_items.for_display():
            if item.link_page_id:
                item.link_page = self.top_level_page_dict[item.link_page_id]
            new_items.append(item)
        return new_items


class MainMenu(Menu):
    site = models.OneToOneField(
        'wagtailcore.Site', related_name="main_menu",
        db_index=True, editable=False, on_delete=models.CASCADE
    )
    max_levels = models.PositiveSmallIntegerField(
        verbose_name=_('maximum levels'),
        help_text=_(
            'The default number of maximum levels to display when rendering '
            'this menu. The value can be overidden by supplying a different '
            '`max_levels` value to the `main_menu` tag.'
        ),
        default=DEFAULT_MAIN_MENU_MAX_LEVELS,
        choices=MAX_LEVELS_CHOICES,
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
        InlinePanel('menu_items', label=_("Menu items")),
    )


class FlatMenu(Menu):
    site = models.ForeignKey(
        'wagtailcore.Site',
        related_name="flat_menus")
    title = models.CharField(
        max_length=255,
        help_text=_("For internal reference only."))
    handle = models.SlugField(
        max_length=100,
        help_text=_(
            "Used to reference this menu in templates etc. Must be unique "
            "for the selected site."))
    heading = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "If supplied, appears above the menu when rendered."))
    max_levels = models.PositiveSmallIntegerField(
        verbose_name=_('maximum levels'),
        help_text=_(
            'The default number of maximum levels to display when rendering '
            'this menu. The value can be overidden by supplying a different '
            '`max_levels` value to the `flat_menu` tag.'
        ),
        default=DEFAULT_FLAT_MENU_MAX_LEVELS,
        choices=MAX_LEVELS_CHOICES,
    )

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
        InlinePanel('menu_items', label=_("Menu items")),
    )


class MainMenuItem(Orderable, MenuItem):
    menu = ParentalKey('MainMenu', related_name="menu_items")
    allow_subnav = models.BooleanField(
        default=True,
        verbose_name=_("allow sub-menu for this item"),
        help_text=_(
            "NOTE: The sub-menu might not be displayed, even if checked. "
            "It depends on how the menu is used in this project's templates."
        )
    )


class FlatMenuItem(Orderable, MenuItem):
    menu = ParentalKey('FlatMenu', related_name="menu_items")
    allow_subnav = models.BooleanField(
        default=False,
        verbose_name=_("allow sub-menu for this item"),
        help_text=_(
            "NOTE: The sub-menu might not be displayed, even if checked. "
            "It depends on how the menu is used in this project's templates."
        )
    )
