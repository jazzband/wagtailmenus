from __future__ import absolute_import, unicode_literals

from django.utils.functional import cached_property

from .. import app_settings


class DefinesSubMenuTemplatesMixin(object):
    sub_menu_template_name = None  # set to use a specific default template

    def get_sub_menu_template(self):
        engine = self.get_template_engine()
        specified = self._option_vals.sub_menu_template_name
        if specified:
            return engine.get_template(specified)
        if self.sub_menu_template_name:
            return engine.get_template(self.sub_menu_template_name)
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
        Include the name of the sub-menu template in the context. This is
        purely for backwards compatibility. Any sub menus rendered as part of
        this menu will call `sub_menu_template` on the original menu instance
        to get an actual `Template`
        """
        data = {}
        if self._contextual_vals.current_level == 1 and self.max_levels > 1:
            data['sub_menu_template'] = self.sub_menu_template.name
        data.update(kwargs)
        return super(DefinesSubMenuTemplatesMixin, self).get_context_data(
            **data)
