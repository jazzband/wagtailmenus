from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, PageChooserPanel
from wagtail.models import Orderable, Page

from wagtailmenus.conf import settings
from wagtailmenus.managers import MenuItemManager

#########################################################
# Base classes
#########################################################


class MenuItem:
    """A base class that all other 'menu item' classes should inherit from."""
    allow_subnav = False


#########################################################
# Abstract models
#########################################################

class AbstractMenuItem(models.Model, MenuItem):
    """A model class that defines a base set of fields and methods for all
    'menu item' models."""
    link_page = models.ForeignKey(
        Page,
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
    url_append = models.CharField(
        verbose_name=_("append to URL"),
        max_length=255,
        blank=True,
        help_text=_(
            "Use this to optionally append a #hash or querystring to the "
            "above page's URL."
        )
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
    link_text = models.CharField(
        verbose_name=_('link text'),
        max_length=255,
        blank=True,
        help_text=_(
            "Provide the text to use for a custom URL, or set on an internal "
            "page link to use instead of the page's title."
        ),
    )

    objects = MenuItemManager()

    class Meta:
        abstract = True
        verbose_name = _("menu item")
        verbose_name_plural = _("menu items")
        ordering = ('sort_order',)

    @property
    def menu_text(self):
        if self.link_text:
            return self.link_text
        if not self.link_page:
            return ''
        return getattr(
            self.link_page,
            settings.PAGE_FIELD_FOR_MENU_ITEM_TEXT,
            self.link_page.title
        )

    def relative_url(self, site=None, request=None):
        if self.link_page:
            try:
                page_url = self.link_page.get_url(
                    request=request, current_site=site)
                return page_url + self.url_append
            except TypeError:
                return ''
        return self.link_url + self.url_append

    def get_full_url(self, request=None):
        if self.link_page:
            try:
                page_url = self.link_page.get_full_url(request=request)
                return page_url + self.url_append
            except TypeError:
                return ''
        return self.link_url + self.url_append

    def clean(self, *args, **kwargs):
        if not self.link_url and not self.link_page:
            msg = _("Please choose an internal page or provide a custom URL")
            raise ValidationError({'link_url': msg})
        if self.link_url and self.link_page:
            msg = _("Linking to both a page and custom URL is not permitted")
            raise ValidationError({'link_page': msg, 'link_url': msg})
        if self.link_url and not self.link_text:
            msg = _("This field is required when linking to a custom URL")
            raise ValidationError({'link_text': msg})
        super().clean(*args, **kwargs)

    def get_active_class_for_request(self, request=None):
        """
        Return the most appropriate 'active_class' for this menu item (only
        used when 'link_url' is used instead of 'link_page').
        """
        parsed_url = urlparse(self.link_url)
        if parsed_url.netloc:
            return ''
        if request.path == parsed_url.path:
            return settings.ACTIVE_CLASS
        if (
            request.path.startswith(parsed_url.path) and
            parsed_url.path != '/'
        ):
            return settings.ACTIVE_ANCESTOR_CLASS
        return ''

    def __str__(self):
        return self.menu_text

    panels = [
        PageChooserPanel('link_page'),
        FieldPanel('link_url'),
        FieldPanel('url_append'),
        FieldPanel('link_text'),
        FieldPanel('handle'),
        FieldPanel('allow_subnav'),
    ]


class AbstractMainMenuItem(Orderable, AbstractMenuItem):
    """Defines additional fields just for 'main menu' menu items."""

    allow_subnav = models.BooleanField(
        verbose_name=_("allow sub-menu for this item"),
        default=True,
        help_text=_(
            "NOTE: The sub-menu might not be displayed, even if checked. "
            "It depends on how the menu is used in this project's templates."
        )
    )

    class Meta(AbstractMenuItem.Meta):
        abstract = True


class AbstractFlatMenuItem(Orderable, AbstractMenuItem):
    """Defines additional fields just for 'flat menu' menu items."""

    allow_subnav = models.BooleanField(
        verbose_name=_("allow sub-menu for this item"),
        default=False,
        help_text=_(
            "NOTE: The sub-menu might not be displayed, even if checked. "
            "It depends on how the menu is used in this project's templates."
        )
    )

    class Meta(AbstractMenuItem.Meta):
        abstract = True


#########################################################
# Concrete models
#########################################################

class MainMenuItem(AbstractMainMenuItem):
    """The default model class to use for 'main menu' menu items."""
    menu = ParentalKey(
        'wagtailmenus.MainMenu',
        on_delete=models.CASCADE,
        related_name="menu_items"
    )


class FlatMenuItem(AbstractFlatMenuItem):
    """The default model class to use for 'flat menu' menu items."""
    menu = ParentalKey(
        'wagtailmenus.FlatMenu',
        on_delete=models.CASCADE,
        related_name="menu_items"
    )
