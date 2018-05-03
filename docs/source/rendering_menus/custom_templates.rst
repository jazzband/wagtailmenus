
.. _custom_templates:

=============================
Using your own menu templates
=============================

.. contents::
    :local:
    :depth: 2

-----

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

-----

Getting wagtailmenus to use your custom menu templates
======================================================


.. _custom_templates_auto:

Using preferred paths and names for your templates 
--------------------------------------------------

This is the easiest (and recommended) approach for getting wagtailmenus to use your custom menu templates for rendering.

When you don't use ``template``, ``sub_menu_template``, or ``sub_menu_templates`` arguments to explicitly specify templates for each tag, wagtailmenus looks in a list of gradually less specific paths until it finds an appropriate template to use. If you're familiar with Django, you'll probably already be familiar with this concept. Essentially, you override the default menu templates by simply putting your custom templates in a preferred location within your project.

The following sections outline the preferred template paths for each tag, in the order that they are searched for (most specific first).

.. contents::
    :local:
    :depth: 1


.. _custom_templates_main_menu:

Preferred template paths for ``{% main_menu %}``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. NOTE::
    Template paths marked with an asterisk (*) are only included if you've set the :ref:`SITE_SPECIFIC_TEMPLATE_DIRS` setting to ``True`` in your project settings. They are not used by default.

**For the menu itself:**

- ``"menus/{{ request.site.domain }}/main/level_1.html"`` *
- ``"menus/{{ request.site.domain }}/main/menu.html"`` *
- ``"menus/{{ request.site.domain }}/main_menu.html"`` *
- ``"menus/main/level_1.html"``
- ``"menus/main/menu.html"``
- ``"menus/main_menu.html"``

**For any sub-menus:**

- ``"menus/{{ request.site.domain }}/level_{{ current_level }}.html"`` *
- ``"menus/{{ request.site.domain }}/sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/main_sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/sub_menu.html"`` *
- ``"menus/main/level_{{ current_level }}.html"``
- ``"menus/main/sub_menu.html"``
- ``"menus/main_sub_menu.html"``
- ``"menus/sub_menu.html"``

**Examples**

For a multi-level main menu that displays three levels of links, your templates directory might look like this:
::

    templates
    └── menus
        └── main
            ├── level_1.html  # Used by the {% main_menu %} tag for the 1st level
            ├── level_2.html  # Used by the {% sub_menu %} tag for the 2nd level
            └── level_3.html  # Used by the {% sub_menu %} tag for the 3rd level

.. TIP::
    
    Even if the various menus in your project share a lot of common templates between them, you might to still consider following this level-specific pattern of template definition, even if some of the templates simply use ``{% extends %}`` or ``{% include %}`` to include a common template. It'll make it much easier to identify which menu templates are being used by which menus at a later time.


.. _custom_templates_flat_menu:

Preferred template paths for ``{% flat_menu %}`` 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For flat menus, the tag also uses the `handle` field of the specific menu being rendered, so that you can have wagtailmenus use different templates for different menus.

.. NOTE::
    Template paths marked with an asterisk (*) are only included if you've set the :ref:`SITE_SPECIFIC_TEMPLATE_DIRS` setting to ``True`` in your project settings. They are not used by default.

**For the menu itself:**

- ``"menus/{{ request.site.domain }}/flat/{{ menu.handle }}/level_1.html"`` *
- ``"menus/{{ request.site.domain }}/flat/{{ menu.handle }}/menu.html"`` *
- ``"menus/{{ request.site.domain }}/flat/{{ menu.handle }}.html"`` *
- ``"menus/{{ request.site.domain }}/{{ menu.handle }}/level_1.html"`` *
- ``"menus/{{ request.site.domain }}/{{ menu.handle }}/menu.html"`` *
- ``"menus/{{ request.site.domain }}/{{ menu.handle }}.html"`` *
- ``"menus/{{ request.site.domain }}/flat/menu.html"`` *
- ``"menus/{{ request.site.domain }}/flat/default.html"`` *
- ``"menus/{{ request.site.domain }}/flat_menu.html"`` *
- ``"menus/flat/{{ menu.handle }}/level_1.html"``
- ``"menus/flat/{{ menu.handle }}/menu.html"``
- ``"menus/flat/{{ menu.handle }}.html"``
- ``"menus/{{ menu.handle }}/level_1.html"``
- ``"menus/{{ menu.handle }}/menu.html"``
- ``"menus/{{ menu.handle }}.html"``
- ``"menus/flat/level_1.html"``
- ``"menus/flat/default.html"``
- ``"menus/flat/menu.html"``
- ``"menus/flat_menu.html"``

**For any sub-menus:**

- ``"menus/{{ request.site.domain }}/flat/{{ menu.handle }}/level_{{ current_level }}.html"`` *
- ``"menus/{{ request.site.domain }}/flat/{{ menu.handle }}/sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/flat/{{ menu.handle }}_sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/{{ menu.handle }}/level_{{ current_level }}.html"`` *
- ``"menus/{{ request.site.domain }}/{{ menu.handle }}/sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/{{ menu.handle }}_sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/flat/level_{{ current_level }}.html"`` *
- ``"menus/{{ request.site.domain }}/flat/sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/sub_menu.html"`` *
- ``"menus/flat/{{ menu.handle }}/level_{{ current_level }}.html"``
- ``"menus/flat/{{ menu.handle }}/sub_menu.html"``
- ``"menus/flat/{{ menu.handle }}_sub_menu.html"``
- ``"menus/{{ menu.handle }}/level_{{ current_level }}.html"``
- ``"menus/{{ menu.handle }}/sub_menu.html"``
- ``"menus/{{ menu.handle }}_sub_menu.html"``
- ``"menus/flat/level_{{ current_level }}.html"``
- ``"menus/flat/sub_menu.html"``
- ``"menus/sub_menu.html"``

**Examples**

If your project had a flat menu with the handle ``info``, that was designed to display two levels of links, your templates directory might look like this:
::

    templates
    └── menus
        └── info
            ├── level_1.html  # Used by the {% flat_menu %} tag for the 1st level
            └── level_2.html  # Used by the {% sub_menu %} tag for the 2nd level


Or, if the ``info`` menu only needed to show a single level of links, you might prefer to keep things simple, like so:
::

    templates
    └── menus
        └── info.html

.. TIP::
    
    If your menu is currently single-level only, but might grow in future to include more levels, you might find it easier to embrace level-specific template names now rather than later. So, in the above example, that would mean renaming ``templates/menus/info.html`` to ``templates/menus/info/level_1.html``.  


Or, if your project needs multiple flat menus with different ``handle`` values, but you are happy for them to share the same templates, you might structure things like so:

::

    templates
    └── menus
        └── flat
            ├── level_1.html  # Used by the {% flat_menu %} tag for the 1st level
            ├── level_2.html  # Used by the {% sub_menu %} tag for the 2nd level
            └── level_3.html  # Used by the {% sub_menu %} tag for the 3rd level

.. NOTE::
    
    In this example, the ``level_2.html`` and ``level_3.html`` templates would only ever be used when needed. You can control how many levels are rendered on a per-menu basis, or by using the ``max_levels`` template tag argument.


.. _custom_templates_section_menu:

Preferred template paths for ``{% section_menu %}`` 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. NOTE::
    Template paths marked with an asterisk (*) are only included if you've set the :ref:`SITE_SPECIFIC_TEMPLATE_DIRS` setting to ``True`` in your project settings. They are not used by default.

**For the menu itself:**

- ``"menus/{{ request.site.domain }}/section/level_1.html"`` *
- ``"menus/{{ request.site.domain }}/section/menu.html"`` *
- ``"menus/{{ request.site.domain }}/section_menu.html"`` *
- ``"menus/section/level_1.html"``
- ``"menus/section/menu.html"``
- ``"menus/section_menu.html"``

**For any sub-menus:**

- ``"menus/{{ request.site.domain }}/section/level_{{ current_level }}.html"`` *
- ``"menus/{{ request.site.domain }}/section/sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/section_sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/sub_menu.html"`` *
- ``"menus/section/level_{{ current_level }}.html"``
- ``"menus/section/sub_menu.html"``
- ``"menus/section_sub_menu.html"``
- ``"menus/sub_menu.html"``

**Examples**

If your project needs a multi-level section menu, displaying three levels of links, your templates directory might look something like this:
::

    templates
    └── menus
        └── section
            ├── level_1.html  # Used by the {% section_menu %} tag for the 1st level
            ├── level_2.html  # Used by the {% sub_menu %} tag for the 2nd level
            └── level_3.html  # Used by the {% sub_menu %} tag for the 3rd level


Or, if your section menu only needs to surface the first of level of pages within a section, you might structure things more simply, like so:
::

    templates
    └── menus
        └── section_menu.html


.. _custom_templates_children_menu:

Preferred template paths for ``{% children_menu %}`` 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. NOTE::
    Template paths marked with an asterisk (*) are only included if you've set the :ref:`SITE_SPECIFIC_TEMPLATE_DIRS` setting to ``True`` in your project settings. They are not used by default.

**For the menu itself:**

- ``"menus/{{ request.site.domain }}/children/level_1.html"`` *
- ``"menus/{{ request.site.domain }}/children/menu.html"`` *
- ``"menus/{{ request.site.domain }}/children_menu.html"`` *
- ``"menus/children/level_1.html"``
- ``"menus/children/menu.html"``
- ``"menus/children_menu.html"``

**For any sub-menus:**

- ``"menus/{{ request.site.domain }}/children/level_{{ current_level }}.html"`` *
- ``"menus/{{ request.site.domain }}/children/sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/children_sub_menu.html"`` *
- ``"menus/{{ request.site.domain }}/sub_menu.html"`` *
- ``"menus/children/level_{{ current_level }}.html"``
- ``"menus/children/sub_menu.html"``
- ``"menus/children_sub_menu.html"``
- ``"menus/sub_menu.html"``

**Examples**

If your project needs multi-level children menus, displaying two levels of links, your templates directory might look something like this:
::

    templates
    └── menus
        └── children
            ├── level_1.html  # Used by the {% section_menu %} tag for the 1st level
            └── level_2.html  # Used by the {% sub_menu %} tag for the 2nd level 


Or, if you only need single-level children menus, you might structure things more simply, like so:
::

    templates
    └── menus
        └── children_menu.html


.. _custom_templates_specify:

Specifying menu templates using template tag parameters
-------------------------------------------------------

All template tags included in wagtailmenus support ``template``, ``sub_menu_template`` and ``sub_menu_templates`` arguments to allow you to explicitly override the templates used during rendering. 

For example, if you had created the following templates in your project's root 'templates' directory:

- ``"templates/custom_menus/main_menu.html"``
- ``"templates/custom_menus/main_menu_sub.html"``
- ``"templates/custom_menus/main_menu_sub_level_2.html"``

You could make :ref:`main_menu` use those templates for rendering by specifying them in your template, like so:

.. code-block:: html

    {% main_menu max_levels=3 template="custom_menus/main_menu.html" sub_menu_templates="custom_menus/main_menu_sub.html, custom_menus/main_menu_sub_level_2.html" %}

Or, if you only wanted to use a single template for sub menus, you could specify that template like so:

.. code-block:: html
    
    {# A 'sub_menu_templates' value without commas is recognised as a single template #}
    {% main_menu max_levels=3 template="custom_menus/main_menu.html" sub_menu_templates="custom_menus/main_menu_sub.html" %}

    {# You can also use the 'sub_menu_template' (no plural) option, which is slightly more verbose #}
    {% main_menu max_levels=3 template="custom_menus/main_menu.html" sub_menu_template="custom_menus/main_menu_sub.html" %}

Or you could just override one or the other, like so:

.. code-block:: html

    {# Just override the top-level template #}
    {% main_menu max_levels=3 template="custom_menus/main_menu.html" %}

    {# Just override the sub menu templates #}
    {% main_menu max_levels=3 sub_menu_templates="custom_menus/main_menu_sub.html, custom_menus/main_menu_sub_level_2.html" %}

    {# Just override the sub menu templates with a single template #}
    {% main_menu max_levels=3 sub_menu_template="custom_menus/main_menu_sub.html" %}


.. _custom_templates_specify_settings:

Specifying menu templates with project settings
-----------------------------------------------
