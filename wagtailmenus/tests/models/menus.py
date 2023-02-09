from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PageChooserPanel

from wagtailmenus.models import (AbstractFlatMenu, AbstractFlatMenuItem,
                                 AbstractMainMenu, AbstractMainMenuItem,
                                 ChildrenMenu, SectionMenu)

from .utils import TranslatedField


class CustomChildrenMenu(ChildrenMenu):
    template_name = "menus/custom-overrides/children.html"


class CustomSectionMenu(SectionMenu):
    sub_menu_template_name = "menus/custom-overrides/section-sub.html"


class MultilingualMenuItem(models.Model):
    link_text_de = models.CharField(
        verbose_name='link text (de)',
        max_length=255,
        blank=True,
    )
    link_text_fr = models.CharField(
        verbose_name='link text (fr)',
        max_length=255,
        blank=True,
    )
    translated_link_text = TranslatedField(
        'link_text', 'link_text_de', 'link_text_fr'
    )

    class Meta:
        abstract = True
        ordering = ('sort_order',)

    @property
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
        'wagtailmenus.MainMenu',
        on_delete=models.CASCADE,
        related_name="custom_menu_items"
    )


class FlatMenuCustomMenuItem(MultilingualMenuItem, AbstractFlatMenuItem):
    """Custom MenuItem model for the default FlatMenu model. The default
    model is swapped out for this one using the setting:

    `WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME = 'custom_menu_items'
    """

    menu = ParentalKey(
        'wagtailmenus.FlatMenu',
        on_delete=models.CASCADE,
        related_name="custom_menu_items"
    )


class CustomMainMenu(AbstractMainMenu):
    panels = AbstractMainMenu.content_panels + AbstractMainMenu.settings_panels


class CustomFlatMenu(AbstractFlatMenu):
    heading_de = models.CharField(
        verbose_name='heading (de)',
        max_length=255,
        blank=True,
    )
    heading_fr = models.CharField(
        verbose_name='heading (fr)',
        max_length=255,
        blank=True,
    )
    translated_heading = TranslatedField(
        'heading', 'heading_de', 'heading_fr'
    )

    content_panels = (
        MultiFieldPanel(
            heading="Settings",
            children=(
                FieldPanel('title'),
                FieldPanel('site'),
                FieldPanel('handle'),
            )
        ),
        MultiFieldPanel(
            heading="Heading",
            children=(
                FieldPanel('heading'),
                FieldPanel('heading_de'),
                FieldPanel('heading_fr'),
            ),
            classname='collapsible'
        ),
        AbstractFlatMenu.content_panels[1],
    )


class CustomMainMenuItem(MultilingualMenuItem, AbstractMainMenuItem):
    """Custom MenuItem model for `CustomMainMenu`. Notice the `related_name`
    attribue on the field below is the same as it is on
    wagtailmenus.MainMenuItem. Because of this, the
    `WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME` setting doesn't need to be
    overridden ('menu_items' is the default value)."""

    menu = ParentalKey(
        'CustomMainMenu',
        on_delete=models.CASCADE,
        related_name="menu_items"
    )


class CustomFlatMenuItem(MultilingualMenuItem, AbstractFlatMenuItem):
    """Custom MenuItem model for `CustomFlatMenu`. Notice the `related_name`
    attribue on the field below is the same as it is on
    wagtailmenus.FlatMenuItem. Because of this, the
    `WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME` setting doesn't need to be
    overridden ('menu_items' is the default value)."""

    menu = ParentalKey(
        'CustomFlatMenu',
        on_delete=models.CASCADE,
        related_name="menu_items"
    )
