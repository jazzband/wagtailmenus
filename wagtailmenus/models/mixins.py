from __future__ import absolute_import, unicode_literals

import warnings
from types import GeneratorType

from django.utils.functional import cached_property

from .. import app_settings
from ..utils.deprecation import RemovedInWagtailMenus26Warning
from ..utils.inspection import accepts_kwarg


class PageModifiesMenuItemsMixin(object):

    def let_page_modify_menu_items(self, page, menu_items):
        """
        If the menu has menu items that can be modified by a parent or root
        page's ``modify_submenu_items`` method, send the ``menu_items`` to that
        method for further modification and return them. The menu class is
        responsible for ensuring the this method is only called when it should
        be, and that the page is 'specific' already (if not, the method will
        have no effect).
        """
        if not hasattr(page, 'modify_submenu_items'):
            return menu_items

        ctx_vals = self._contextual_vals
        opt_vals = self._option_vals
        kwargs = {
            'request': self.request,
            'menu_instance': self,
            'original_menu_tag': ctx_vals.original_menu_tag,
            'current_site': ctx_vals.current_site,
            'current_page': ctx_vals.current_page,
            'current_ancestor_ids': ctx_vals.current_page_ancestor_ids,
            'allow_repeating_parents': opt_vals.allow_repeating_parents,
            'apply_active_classes': opt_vals.apply_active_classes,
            'use_absolute_page_urls': opt_vals.use_absolute_page_urls,
        }
        # Backwards compatibility for 'modify_submenu_items' methods that
        # don't accept a 'use_absolute_page_urls' kwarg
        if not accepts_kwarg(
            page.modify_submenu_items, 'use_absolute_page_urls'
        ):
            kwargs.pop('use_absolute_page_urls')
            warning_msg = (
                "The 'modify_submenu_items' method on '%s' should be "
                "updated to accept a 'use_absolute_page_urls' keyword "
                "argument. View the 2.4 release notes for more info: "
                "https://github.com/rkhleics/wagtailmenus/releases/tag/v.2.4.0"
                % page.__class__.__name__,
            )
            warnings.warn(warning_msg, RemovedInWagtailMenus26Warning)

        # Call `modify_submenu_items` using the above kwargs dict
        if isinstance(menu_items, GeneratorType):
            menu_items = list(menu_items)
        return page.modify_submenu_items(menu_items, **kwargs)


class DefinesSubMenuTemplatesMixin(object):

    def get_sub_menu_template(self):
        engine = self.get_template_engine()
        specified = self._option_vals.sub_menu_template_name
        if specified:
            return engine.get_template(specified)
        return engine.select_template(self.get_sub_menu_template_names())

    @cached_property
    def sub_menu_template(self):
        return self.get_sub_menu_template()

    def get_sub_menu_template_names(self):
        """Return a list of template paths/names to search when
        rendering a sub menu for an instance of this class. The list should be
        ordered with most specific names first, since the first template found
        to exist will be used for rendering"""
        current_site = self._contextual_vals.current_site
        template_names = []
        menu_str = self.menu_short_name
        if app_settings.SITE_SPECIFIC_TEMPLATE_DIRS and current_site:
            hostname = current_site.hostname
            template_names.extend([
                "menus/%s/%s/sub_menu.html" % (hostname, menu_str),
                "menus/%s/%s_sub_menu.html" % (hostname, menu_str),
                "menus/%s/sub_menu.html" % hostname,
            ])
        template_names.extend([
            "menus/%s/sub_menu.html" % menu_str,
            "menus/%s_sub_menu.html" % menu_str,
            app_settings.DEFAULT_SUB_MENU_TEMPLATE,
        ])
        return template_names

    def get_context_data(self, **kwargs):
        """
        If there's a possibility that sub menus might be neded, prefetch the
        template to be used for render them and add it to the context, so that
        it only needs to happen once.
        """
        data = {}
        if self._contextual_vals.current_level == 1 and self.max_levels > 1:
            data['sub_menu_template'] = self.sub_menu_template.name
        data.update(kwargs)
        return super(DefinesSubMenuTemplatesMixin, self).get_context_data(
            **data)
