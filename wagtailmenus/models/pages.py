from __future__ import absolute_import, unicode_literals

import warnings
from copy import copy

from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore.models import Page

from wagtailmenus.utils.inspection import accepts_kwarg
from wagtailmenus.utils.deprecation import RemovedInWagtailMenus25Warning
from .. import app_settings
from ..forms import LinkPageAdminForm
from ..panels import menupage_settings_panels, linkpage_edit_handler


class MenuPageMixin(models.Model):
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

    class Meta:
        abstract = True

    def modify_submenu_items(
        self, menu_items, current_page, current_ancestor_ids, current_site,
        allow_repeating_parents, apply_active_classes, original_menu_tag,
        menu_instance=None, request=None
    ):
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

            # Create dict of kwargs to send to `get_repeated_menu_item`
            method_kwargs = {
                'current_page': current_page,
                'current_site': current_site,
                'apply_active_classes': apply_active_classes,
                'original_menu_tag': original_menu_tag,
            }
            if accepts_kwarg(self.get_repeated_menu_item, 'request'):
                method_kwargs['request'] = request
            else:
                msg = (
                    "The 'get_repeated_menu_item' method on '%s' should be "
                    "updated to accept a 'request' keyword argument. View the "
                    "2.3 release notes for more info: https://github.com/"
                    "rkhleics/wagtailmenus/releases/tag/v.2.3.0" %
                    self.__class__.__name__
                )
                warnings.warn(msg, RemovedInWagtailMenus25Warning)
            # Call `get_repeated_menu_item` using the above kwargs dict
            repeated_item = self.get_repeated_menu_item(**method_kwargs)
            menu_items.insert(0, repeated_item)
        return menu_items

    def has_submenu_items(self, current_page, allow_repeating_parents,
                          original_menu_tag, menu_instance=None, request=None):
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
        return menu_instance.page_has_children(self)

    def get_repeated_menu_item(
        self, current_page, current_site, apply_active_classes,
        original_menu_tag, request=None
    ):
        """Return something that can be used to display a 'repeated' menu item
        for this specific page."""

        menuitem = copy(self)
        setattr(menuitem, 'text', self.repeated_item_text or self.title)
        setattr(menuitem, 'href', self.relative_url(current_site))
        active_class = ''
        if apply_active_classes and self == current_page:
            active_class = app_settings.ACTIVE_CLASS
        setattr(menuitem, 'active_class', active_class)
        setattr(menuitem, 'has_children_in_menu', False)
        return menuitem


class MenuPage(Page, MenuPageMixin):

    settings_panels = menupage_settings_panels

    class Meta:
        abstract = True


class AbstractLinkPage(Page):
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        verbose_name=_('link to an internal page'),
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
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
            "Use this to optionally append a #hash or querystring to the URL."
        )
    )
    extra_classes = models.CharField(
        verbose_name=_('menu item css classes'),
        max_length=100,
        blank=True,
        help_text=_(
            "Optionally specify css classes to be added to this page when it "
            "appears in menus."
        )
    )

    subpage_types = []  # Don't allow subpages
    search_fields = []  # Don't surface these pages in search results
    base_form_class = LinkPageAdminForm

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        # Set `show_in_menus` to True by default, but leave as False if
        # it has been set
        super(AbstractLinkPage, self).__init__(*args, **kwargs)
        if not self.pk:
            self.show_in_menus = True

    def menu_text(self, request=None):
        """Return a string to use as link text when this page appears in
        menus."""
        if(
            app_settings.PAGE_FIELD_FOR_MENU_ITEM_TEXT != 'menu_text' and
            hasattr(self, app_settings.PAGE_FIELD_FOR_MENU_ITEM_TEXT)
        ):
            return getattr(self, app_settings.PAGE_FIELD_FOR_MENU_ITEM_TEXT)
        return self.title

    def clean(self, *args, **kwargs):
        if self.link_page and isinstance(
            self.link_page.specific, AbstractLinkPage
        ):
            msg = _("A link page cannot link to another link page")
            raise ValidationError({'link_page': msg})
        if not self.link_url and not self.link_page:
            msg = _("Please choose an internal page or provide a custom URL")
            raise ValidationError({'link_url': msg, 'link_page': msg})
        if self.link_url and self.link_page:
            msg = _("Linking to both a page and custom URL is not permitted")
            raise ValidationError({'link_url': msg, 'link_page': msg})
        super(AbstractLinkPage, self).clean(*args, **kwargs)

    def link_page_is_suitable_for_display(
        self, request=None, current_site=None, menu_instance=None,
        original_menu_tag=''
    ):
        """
        Like menu items, link pages linking to pages should only be included
        in menus when the target page is live and is itself configured to
        appear in menus. Returns a boolean indicating as much
        """
        if self.link_page:
            if(
                not self.link_page.show_in_menus or
                not self.link_page.live or
                self.link_page.expired
            ):
                return False
        return True

    def show_in_menus_custom(self, request=None, current_site=None,
                             menu_instance=None, original_menu_tag=''):
        """
        Return a boolean indicating whether this page should be included in
        menus being rendered.
        """
        if not self.show_in_menus:
            return False
        if not self.link_page:
            return True
        return self.link_page_is_suitable_for_display()

    def get_sitemap_urls(self):
        return []  # don't include pages of this type in sitemaps

    def _url_base(self, request=None, current_site=None, full_url=False):
        # Return the url of the page being linked to, or the custom URL
        if self.link_url:
            return self.link_url

        p = self.link_page.specific  # for tidier referencing below
        if full_url:
            # Try for 'get_full_url' method (added in Wagtail 1.11) or fall
            # back to 'full_url' property
            if hasattr(p, 'get_full_url'):
                return p.get_full_url(request=request)
            return p.full_url

        # Try for 'get_url' method (added in Wagtail 1.11) or fall back to
        # established 'relative_url' method or 'url' property
        if hasattr(p, 'get_url'):
            return p.get_url(request=request, current_site=current_site)
        if current_site:
            return p.relative_url(current_site=current_site)
        return p.url

    def get_url(self, request=None, current_site=None):
        try:
            base = self._url_base(request=request, current_site=current_site)
            return base + self.url_append
        except TypeError:
            pass  # self.link_page is not routable
        return ''

    url = property(get_url)

    def get_full_url(self, request=None):
        try:
            base = self._url_base(request=request, full_url=True)
            return base + self.url_append
        except TypeError:
            pass  # self.link_page is not routable
        return ''

    full_url = property(get_full_url)

    def relative_url(self, current_site, request=None):
        return self.get_url(request=request, current_site=current_site)

    def serve(self, request, *args, **kwargs):
        # Display appropriate message if previewing
        if getattr(request, 'is_preview', False):
            return HttpResponse(_("This page redirects to: %(url)s") % {
                'url': self.get_full_url(request)
            })
        # Redirect to target URL if served
        site = getattr(request, 'site', None)
        return redirect(
            self.relative_url(current_site=site, request=request)
        )

    edit_handler = linkpage_edit_handler
