from copy import deepcopy
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, PageChooserPanel, MultiFieldPanel, InlinePanel)
from wagtail.wagtailcore.models import Page, Orderable

from .app_settings import ACTIVE_CLASS
from .managers import MenuItemManager
from .panels import menupage_settings_panels


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
            extra = deepcopy(self)
            setattr(extra, 'text', self.repeated_item_text or self.title)
            setattr(extra, 'href', self.relative_url(current_site))
            active_class = ''
            if(apply_active_classes and self == current_page):
                active_class = ACTIVE_CLASS
            setattr(extra, 'active_class', active_class)

            menu_items.insert(0, extra)

        return menu_items

    def has_submenu_items(self, current_page, check_for_children,
                          allow_repeating_parents, original_menu_tag):
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
        if self.link_page:
            return self.link_text or self.link_page.title
        return self.link_text

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


class MainMenu(ClusterableModel):
    site = models.OneToOneField(
        'wagtailcore.Site', related_name="main_menu",
        db_index=True, editable=False, on_delete=models.CASCADE
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


class FlatMenu(ClusterableModel):
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
