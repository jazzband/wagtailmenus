from django.db import models
from django.utils.translation import ugettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, MultiFieldPanel, PageChooserPanel)
from wagtailmenus.models import (
    AbstractMainMenu, AbstractMainMenuItem, AbstractFlatMenu,
    AbstractFlatMenuItem)

from .utils import TranslatedField


class MultilingualMenuItem(models.Model):
    link_text_de = models.CharField(
        verbose_name=_('link text (de)'),
        max_length=255,
        blank=True,
    )
    link_text_fr = models.CharField(
        verbose_name=_('link text (fr)'),
        max_length=255,
        blank=True,
    )
    translated_link_text = TranslatedField(
        'link_text', 'link_text_de', 'link_text_fr'
    )

    class Meta:
        abstract = True

    def menu_text(self):
        return self.translated_link_text or getattr(
            self.link_page, 'translated_title', None
        ) or self.link_page.title

    panels = (
        PageChooserPanel('link_page'),
        FieldPanel('link_url'),
        FieldPanel('url_append'),
        FieldPanel('link_text'),
        FieldPanel('link_text_de'),
        FieldPanel('link_text_fr'),
        FieldPanel('handle'),
        FieldPanel('allow_subnav'),
    )


class MainMenuCustomMenuItem(MultilingualMenuItem, AbstractMainMenuItem):
    """Custom MenuItem model for the default MainMenu model. The default
    model is swapped out for this one using the setting:

    `WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME = 'custom_menu_items'
    """
    menu = ParentalKey(
        'wagtailmenus.MainMenu', related_name="custom_menu_items"
    )


class FlatMenuCustomMenuItem(MultilingualMenuItem, AbstractFlatMenuItem):
    """Custom MenuItem model for the default FlatMenu model. The default
    model is swapped out for this one using the setting:

    `WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME = 'custom_menu_items'
    """

    menu = ParentalKey(
        'wagtailmenus.FlatMenu', related_name="custom_menu_items"
    )


class CustomMainMenu(AbstractMainMenu):
    pass


class CustomFlatMenu(AbstractFlatMenu):
    heading_de = models.CharField(
        verbose_name=_('heading (de)'),
        max_length=255,
        blank=True,
    )
    heading_fr = models.CharField(
        verbose_name=_('heading (fr)'),
        max_length=255,
        blank=True,
    )
    translated_heading = TranslatedField(
        'heading', 'heading_de', 'heading_fr'
    )

    panels = (
        MultiFieldPanel(
            heading=_("Settings"),
            children=(
                FieldPanel('title'),
                FieldPanel('site'),
                FieldPanel('handle'),
            )
        ),
        MultiFieldPanel(
            heading=_("Heading"),
            children=(
                FieldPanel('heading'),
                FieldPanel('heading_de'),
                FieldPanel('heading_fr'),
            ),
            classname='collapsible'
        ),
        AbstractFlatMenu.panels[1],
        AbstractFlatMenu.panels[2],
    )


class CustomMainMenuItem(MultilingualMenuItem, AbstractMainMenuItem):
    """Custom MenuItem model for `CustomMainMenu`. Notice the `related_name`
    attribue on the field below is the same as it is on
    wagtailmenus.MainMenuItem. Because of this, the
    `WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME` setting doesn't need to be
    overridden ('menu_items' is the default value)."""

    menu = ParentalKey('CustomMainMenu', related_name="menu_items")


class CustomFlatMenuItem(MultilingualMenuItem, AbstractFlatMenuItem):
    """Custom MenuItem model for `CustomFlatMenu`. Notice the `related_name`
    attribue on the field below is the same as it is on
    wagtailmenus.FlatMenuItem. Because of this, the
    `WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME` setting doesn't need to be
    overridden ('menu_items' is the default value)."""

    menu = ParentalKey('CustomFlatMenu', related_name="menu_items")
