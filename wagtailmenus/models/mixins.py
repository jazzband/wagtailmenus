from django.utils.functional import cached_property
from django.template.loader import get_template, select_template

from .. import app_settings


class DefinesSubMenuTemplatesMixin:
    sub_menu_template_name = None  # set to use a specific default template

    def get_sub_menu_template(self):
        template_name = self._option_vals.sub_menu_template_name or \
            self.sub_menu_template_name

        # TODO: To be removed in v2.8.0
        if not app_settings.USE_BACKEND_SPECIFIC_TEMPLATES:
            engine = self.get_template_engine()
            if template_name:
                return engine.get_template(template_name)
            return engine.select_template(self.get_sub_menu_template_names())

        if template_name:
            return get_template(template_name)
        return select_template(self.get_sub_menu_template_names())

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
            # TODO: Below conditional to be removed in v2.8.0
            t = self.sub_menu_template
            if not app_settings.USE_BACKEND_SPECIFIC_TEMPLATES:
                data['sub_menu_template'] = t.name
            else:
                data['sub_menu_template'] = t.template.name
        data.update(kwargs)
        return super().get_context_data(**data)
