
.. _custom_templates:

=============================
Using your own menu templates
=============================

.. contents::
    :local:
    :depth: 2


Writing custom menu templates
=============================

.. _template_context_variables:

What context variables are available to use?
--------------------------------------------

The following variables are added to the context by all included template tags, which you can make use of in your templates:

:``menu_items``: 
    A list of ``MenuItem`` or ``Page`` objects with some additional attributes
    added to help render menu items for the current level. 

    For more details on the attribute values added by wagtailmenus, see:
    :ref:`menu_items_added_attributes`.

:``current_level``: 
    An integer indicating the current level being rendered. This starts at
    ``1`` for the initial template tag call, then increments each time 
    `sub_menu` is called recursively for rendering a particular branch of a
    menu. 

:``max_levels``: 
    An integer indicating the maximum number of levels that should be rendered
    for the current menu, as determined by the original ``main_menu``,
    ``section_menu``, ``flat_menu`` or ``children_menu`` tag call.

:``current_template``: 
    The name of the template currently being used for rendering. This is most 
    useful when rendering a ``sub_menu`` template that calls ``sub_menu`` 
    recursively, and you wish to use the same template for all recursions.

:``sub_menu_template``: 
    The name of the template that should be used for rendering any further 
    levels (should be picked up automatically by the ``sub_menu`` tag).

:``original_menu_tag``: 
    A string value indicating the name of tag was originally called in order to
    render the branch currently being rendered. The value will be one of 
    ``"main_menu"``, ``"flat_menu"``, ``"section_menu"``, ``"children_menu"``
    or ``"sub_menu"``.

:``allow_repeating_parents``: 
    A boolean indicating whether ``MenuPage`` fields should be respected when
    rendering further menu levels.

:``apply_active_classes``: 
    A boolean indicating whether ``sub_menu`` 
    tags should attempt to add  'active' and 'ancestor' classes to menu items
    when rendering further menu levels.

:``use_absolute_page_urls``: 
    A boolean indicating whether absolute page URLs should be used for page
    links when rendering.


.. _menu_items_added_attributes:

Attributes added to each item in ``menu_items`` 
-----------------------------------------------

:``href``: 
    The URL that the menu item should link to.

:``text``:
    The text that should be used for the menu item.

    You can change the field or attribute used to populate the ``text``
    attribute by utilising the :ref:`DEFAULT_PAGE_FIELD_FOR_MENU_ITEM_TEXT`
    setting.

:``active_class``: 
    A class name to indicate the 'active' state of the menu item. The value
    will be 'active' if linking to the current page, or 'ancestor' if linking
    to one of it's ancestors.

    You can change the CSS class strings used to indicate 'active' and 
    'ancestor' statuses by utilising the :ref:`ACTIVE_CLASS` and
    :ref:`ACTIVE_ANCESTOR_CLASS` settings.

:``has_children_in_menu``: 
    A boolean indicating whether the menu item has children that should be
    output as a sub-menu.


Getting wagtailmenus to use your custom menu templates
======================================================


.. _custom_templates_auto:

Using preferred paths and names for your templates 
--------------------------------------------------

This is the easiest (and recommended) approach for getting wagtailmenus to use your custom menu templates for rendering.

When use don't use ``template`` or ``sub_menu_template`` arguments to explicitly specify templates for each tag, wagtailmenus looks in a list of gradually less specific paths for templates to use. If you're familiar with Django, you'll probably already be familiar with this approach. Essentially, you can override existing menu templates or add custom ones simply by putting them at a preferred location within your project.

If you have multi-site project, and want to be able to use different templates for some or all of those sites, wagtailmenus can be configured to look for additional 'site specific' paths for each template. To enable this feature, you need to add the following to your project's settings:

.. code-block:: python

    WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS = True

With this set, tags will look for a ``request`` value in the context, and try to identify the current site being viewed by looking for a ``site`` attribute on ``request`` (which is set by ``wagtail.wagtailcore.middleware.SiteMiddleware``). It then uses the ``domain`` field from that ``Site`` object to look for templates with that domain name included.

The following sections outline the preferred path locations for each tag, in the order that they are searched (most specific first).

.. contents::
    :local:
    :depth: 1


.. _custom_templates_main_menu:

Preferred template paths for ``{% main_menu %}``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. NOTE::
    Template paths marked with an asterisk (*) are only included if you've set the :ref:`SITE_SPECIFIC_TEMPLATE_DIRS` setting to ``True`` in your project settings. They are not used by default.

**For the menu itself:**

- ``"menus/{{ request.site.domain }}/main/menu.html"`` *
- ``"menus/{{ request.site.domain }}/main_menu.html"`` *
- ``"menus/main/menu.html"``
- ``"menus/main_menu.html"``

**For any sub-menus:**

- ``"menus/{{ request.site.domain }}/sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/main_sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/sub_menu.html"`` *
- ``"menus/main/sub_menu.html"``
- ``"menus/main_sub_menu.html"``
- ``"menus/sub_menu.html"``


.. _custom_templates_flat_menu:

Preferred template paths for ``{% flat_menu %}`` 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For flat menus, the tag also uses the `handle` field of the specific menu being rendered, so that you can have wagtailmenus use different templates for different menus.

.. NOTE::
    Template paths marked with an asterisk (*) are only included if you've set the :ref:`SITE_SPECIFIC_TEMPLATE_DIRS` setting to ``True`` in your project settings. They are not used by default.

**For the menu itself:**

- ``"menus/{{ request.site.domain }}/flat/{{ menu.handle }}/menu.html"`` *
- ``"menus/{{ request.site.domain }}/flat/{{ menu.handle }}.html"`` *
- ``"menus/{{ request.site.domain }}/{{ menu.handle }}/menu.html"`` *
- ``"menus/{{ request.site.domain }}/{{ menu.handle }}.html"`` *
- ``"menus/{{ request.site.domain }}/flat/menu.html"`` *
- ``"menus/{{ request.site.domain }}/flat/default.html"`` *
- ``"menus/{{ request.site.domain }}/flat_menu.html"`` *
- ``"menus/flat/{{ menu.handle }}/menu.html"``
- ``"menus/flat/{{ menu.handle }}.html"``
- ``"menus/{{ menu.handle }}/menu.html"``
- ``"menus/{{ menu.handle }}.html"``
- ``"menus/flat/default.html"``
- ``"menus/flat/menu.html"``
- ``"menus/flat_menu.html"``

**For any sub-menus:**

- ``"menus/{{ request.site.domain }}/flat/{{ menu.handle }}/sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/flat/{{ menu.handle }}_sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/{{ menu.handle }}/sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/{{ menu.handle }}_sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/flat/sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/sub_menu.html"`` *
- ``"menus/flat/{{ menu.handle }}/sub_menu.html"``
- ``"menus/flat/{{ menu.handle }}_sub_menu.html"``
- ``"menus/{{ menu.handle }}/sub_menu.html"``
- ``"menus/{{ menu.handle }}_sub_menu.html"``
- ``"menus/flat/sub_menu.html"``
- ``"menus/sub_menu.html"``


.. _custom_templates_section_menu:

Preferred template paths for ``{% section_menu %}`` 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. NOTE::
    Template paths marked with an asterisk (*) are only included if you've set the :ref:`SITE_SPECIFIC_TEMPLATE_DIRS` setting to ``True`` in your project settings. They are not used by default.

**For the menu itself:**

- ``"menus/{{ request.site.domain }}/section/menu.html"`` *
- ``"menus/{{ request.site.domain }}/section_menu.html"`` *
- ``"menus/section/menu.html"``
- ``"menus/section_menu.html"``

**For any sub-menus:**

- ``"menus/{{ request.site.domain }}/section/sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/section_sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/sub_menu.html"`` *
- ``"menus/section/sub_menu.html"``
- ``"menus/section_sub_menu.html"``
- ``"menus/sub_menu.html"``


.. _custom_templates_children_menu:

Preferred template paths for ``{% children_menu %}`` 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. NOTE::
    Template paths marked with an asterisk (*) are only included if you've set the :ref:`SITE_SPECIFIC_TEMPLATE_DIRS` setting to ``True`` in your project settings. They are not used by default.

**For the menu itself:**

- ``"menus/{{ request.site.domain }}/children/menu.html"`` *
- ``"menus/{{ request.site.domain }}/children_menu.html"`` *
- ``"menus/children/menu.html"``
- ``"menus/children_menu.html"``

**For any sub-menus:**

- ``"menus/{{ request.site.domain }}/children/sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/children_sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/sub_menu.html"`` *
- ``"menus/children/sub_menu.html"``
- ``"menus/children_sub_menu.html"``
- ``"menus/sub_menu.html"``


.. _custom_templates_specify:

Specifying menu templates using template tag parameters
-------------------------------------------------------

All template tags included in wagtailmenus support ``template`` and ``sub_menu_template`` arguments to allow you to explicitly override the templates used during rendering. 

For example, if you had created the following templates in your project's root 'templates' directory:

- ``"templates/custom_menus/main_menu.html"``
- ``"templates/custom_menus/main_menu_sub_menu.html"``

You could make :ref:`main_menu` use those templates for rendering by specifying them in your template, like so:

.. code-block:: html

    {% main_menu max_levels=2 template="custom_menus/main_menu.html" sub_menu_template="templates/custom_menus/main_menu_sub_menu.html" %}

Or you could just override one or the other (you don't have to override both). e.g:

.. code-block:: html

    {# Just override the template for the top-level #}
    {% main_menu max_levels=2 template="custom_menus/main_menu.html" %}

    {# Just override the template used for sub-menus #}
    {% main_menu max_levels=2 sub_menu_template="custom_menus/main_menu.html" %}
