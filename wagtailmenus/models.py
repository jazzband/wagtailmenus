from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ValidationError
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, PageChooserPanel, FieldRowPanel, InlinePanel)
from wagtail.wagtailcore.models import Orderable


class MenuItem(models.Model):
    show_children_menu = False

    link_text = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "If left blank, the page title will be used. Must be set if you "
            "wish to link to a custom URL."
        )
    )
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        verbose_name=_('Link to an internal page'),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='+',
    )
    link_url = models.CharField(
        max_length=255,
        verbose_name=_('Link to a custom URL'),
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True
        verbose_name = _("menu item")
        verbose_name_plural = _("menu items")

    def clean(self, *args, **kwargs):
        super(MenuItem, self).clean(*args, **kwargs)

        fields_used = 0
        if self.link_page:
            fields_used += 1
        if self.link_url:
            fields_used += 1

        if fields_used == 0:
            raise ValidationError({
                'link_url': [
                    _("This must be set if you're not linking to a page."),
                ]
            })

        if fields_used > 1:
            raise ValidationError(_(
                "You cannot link to both a page and URL. Please review your "
                "link and clear any unwanted values."
            ))

    @property
    def title(self):
        return self.link_text or self.link_page.title

    def __unicode__(self):
        return u'%s' % self.title


class MainMenu(ClusterableModel):
    site = models.OneToOneField('wagtailcore.Site', related_name="main_menu")

    class Meta:
        verbose_name = _("main menu")
        verbose_name_plural = _("main menu")

    def __unicode__(self):
        return 'For %s' % (self.site.site_name or self.site)

    panels = [
        FieldPanel('site'),
        InlinePanel('menu_items', label=_("Menu items")),
    ]


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

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.handle)

    panels = [
        FieldPanel('site'),
        FieldRowPanel(
            classname='label-above',
            children=(
                FieldPanel('title', classname="col6"),
                FieldPanel('handle', classname="col6"),
            )
        ),
        FieldPanel('heading'),
        InlinePanel('menu_items', label=_("Menu items")),
    ]


class MainMenuItem(Orderable, MenuItem):
    menu = ParentalKey('MainMenu', related_name="menu_items")
    show_children_menu = models.BooleanField(
        verbose_name=_("Add a sub-menu for children of this page"),
        default=False,
    )
    repeat_in_children_menu = models.BooleanField(
        verbose_name=_("Include a link to this page in the sub-menu"),
        default=False,
    )
    children_menu_link_text = models.CharField(
        verbose_name=_('Link text for sub-menu item'),
        max_length=255,
        blank=True,
        help_text=_(
            "e.g. Overview. If left blank, the page title will be used."
        )
    )

    @property
    def children_menu_title(self):
        return self.children_menu_link_text or self.link_page.title

    panels = (
        FieldPanel('link_text'),
        FieldPanel('link_url'),
        PageChooserPanel('link_page'),
        FieldPanel('show_children_menu'),
        FieldPanel('repeat_in_children_menu'),
        FieldPanel('children_menu_link_text'),
    )


class FlatMenuItem(Orderable, MenuItem):
    menu = ParentalKey('FlatMenu', related_name="menu_items")

    panels = (
        FieldPanel('link_text'),
        FieldPanel('link_url'),
        PageChooserPanel('link_page'),
    )
