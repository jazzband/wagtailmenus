from django.template.loader import get_template, select_template

from wagtailmenus.conf import settings


def get_item_by_index_or_last_item(items, index):
    if items is None:
        return
    try:
        return items[index]
    except IndexError:
        return items[-1]


class DefinesSubMenuTemplatesMixin:
    # Use to specify a single sub menu template for all levels
    sub_menu_template_name = None
    # Use to specify sub menu templates for each level
    sub_menu_template_names = None

    def _get_specified_sub_menu_template_name(self, level):
        """
        Called by get_sub_menu_template(). Iterates through the various ways in
        which developers can specify potential sub menu templates for a menu,
        and returns the name of the most suitable template for the
        ``current_level``. Values are checked in the following order:

        1.  The ``sub_menu_template`` value passed to the template tag (if
            provided)
        2.  The most suitable template from the ``sub_menu_templates`` list
            passed to the template tag (if provided)
        3.  The ``sub_menu_template_name`` attribute set on the menu class (if
            set)
        4.  The most suitable template from a list of templates set as the
            ``sub_menu_template_names`` attribute on the menu class (if set)

        Parameters
        ----------
        level : int
            The 'current_level' value from the context, indicating the depth
            of sub menu being rendered as part of a multi-level menu. For sub
            menus, the value will always be greater than or equal to 2.

        Returns
        -------
        str or None
            A template name string (the path to a template in the file system),
            or None if no template has been 'specified'
        """
        ideal_index = level - 2
        return self._option_vals.sub_menu_template_name or \
            get_item_by_index_or_last_item(
                self._option_vals.sub_menu_template_names, ideal_index) or \
            self.sub_menu_template_name or \
            get_item_by_index_or_last_item(
                self.sub_menu_template_names, ideal_index)

    def get_sub_menu_template(self, level=2):
        if not hasattr(self, '_sub_menu_template_cache'):
            # Initialise cache for this menu instance
            self._sub_menu_template_cache = {}
        elif level in self._sub_menu_template_cache:
            # Return a cached template instance
            return self._sub_menu_template_cache[level]

        template_name = self._get_specified_sub_menu_template_name(level)
        if template_name:
            # A template was specified somehow
            template = get_template(template_name)
        else:
            # A template wasn't specified, so search the filesystem
            template = select_template(
                self.get_sub_menu_template_names(level)
            )

        # Cache the template instance before returning
        self._sub_menu_template_cache[level] = template
        return template

    sub_menu_template = property(get_sub_menu_template)

    def get_sub_menu_template_names(self, level=2):
        """Return a list of template paths/names to search for when rendering
        a sub menu for this menu instance at the supplied `level`. The list
        should be ordered with most specific names first, since the first
        template found to exist will be used for rendering."""
        template_names = []
        menu_name = self.menu_short_name
        site = self._contextual_vals.current_site

        if settings.SITE_SPECIFIC_TEMPLATE_DIRS and site:
            hostname = site.hostname
            template_names.extend([
                "menus/%s/%s/level_%s.html" % (hostname, menu_name, level),
                "menus/%s/%s/sub_menu.html" % (hostname, menu_name),
                "menus/%s/%s_sub_menu.html" % (hostname, menu_name),
                "menus/%s/sub_menu.html" % hostname,
            ])
        template_names.extend([
            "menus/%s/level_%s.html" % (menu_name, level),
            "menus/%s/sub_menu.html" % menu_name,
            "menus/%s_sub_menu.html" % menu_name,
            settings.DEFAULT_SUB_MENU_TEMPLATE,
        ])
        return template_names

    def get_context_data(self, **kwargs):
        """
        Include the name of the sub menu template in the context. This is
        purely for backwards compatibility. Any sub menus rendered as part of
        this menu will call `sub_menu_template` on the original menu instance
        to get an actual `Template`
        """
        data = {}
        if self._contextual_vals.current_level == 1 and self.max_levels > 1:
            data['sub_menu_template'] = self.sub_menu_template.template.name
        data.update(kwargs)
        return super().get_context_data(**data)
