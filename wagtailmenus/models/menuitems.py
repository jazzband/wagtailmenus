from __future__ import absolute_import, unicode_literals

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel
from wagtail.wagtailcore.models import Orderable

from .. import app_settings
from ..managers import MenuItemManager


#########################################################
# Base classes
#########################################################

class MenuItem(object):
    """A base class that all other 'menu item' classes should inherit from."""
    allow_subnav = False


#########################################################
# Abstract models
#########################################################

@python_2_unicode_compatible
class AbstractMenuItem(models.Model, MenuItem):
    """A model class that defines a base set of fields and methods for all
    'menu item' models."""

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
        help_text=_(
            "Provide the text to use for a custom URL, or set on an internal "
            "page link to use instead of the page's title."
        ),
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
        return self.link_text or getattr(
            self.link_page,
            app_settings.PAGE_FIELD_FOR_MENU_ITEM_TEXT,
            self.link_page.title
        )

    def relative_url(self, site=None):
        if self.link_page:
            return self.link_page.relative_url(site) + self.url_append
        return self.link_url + self.url_append

    def clean(self, *args, **kwargs):
        super(AbstractMenuItem, self).clean(*args, **kwargs)

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

    class Meta:
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

    class Meta:
        abstract = True


#########################################################
# Concrete models
#########################################################

class MainMenuItem(AbstractMainMenuItem):
    """The default model class to use for 'main menu' menu items."""
    menu = ParentalKey('wagtailmenus.MainMenu', related_name="menu_items")


class FlatMenuItem(AbstractFlatMenuItem):
    """The default model class to use for 'flat menu' menu items."""
    menu = ParentalKey('wagtailmenus.FlatMenu', related_name="menu_items")
