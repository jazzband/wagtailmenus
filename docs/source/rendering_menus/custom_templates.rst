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

The following variables are added to the context for each menu template or sub-menu template that you create:

:``menu_items``: 
    If the template is for rendering the first level of a main or flat menu,
    then ``menu_items`` will be a list of ``MainMenuItem`` or ``FlatMenuItem``
    objects (respectively). In all other cases. it will be a list ``Page``
    objects.

    In either case, wagtailmenus adds a number of additional attributes to each
    item to help keep you menu templates consistent. For more information
    see: :ref:`menu_items_added_attributes`

:``current_level``: 
    An integer indicating the current level being rendered. This starts at
    ``1`` for the initial template tag call, then increments by one for each 
    additional ``<ul>`` level that is added by calling the ``{% sub_menu %}`` 
    tag

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
    A string value indicating the name of the tag that was originally called in order to
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

Whether ``menu_items`` is a list of ``Page``, ``MainMenuItem`` or ``FlatMenuItem`` objects, the following additional attributes are added to each item to help improve consistency of menu templates: 

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

When you do not specify templates names using the ``template``, ``sub_menu_template``, or ``sub_menu_templates`` template tag arguments, wagtailmenus looks in a list of gradually less specific paths until it finds an appropriate template to use. If you're familiar with Django, you'll probably already be familiar with this concept. Essentially, you can easily override the default menu templates by putting your custom templates in a preferred location within your project.

The following sections outline the preferred template paths for each tag, in the order that they are searched for (most specific first).

.. contents::
    :local:
    :depth: 1


.. _custom_templates_main_menu:

Preferred template paths for ``{% main_menu %}``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. NOTE::
    Template paths marked with an asterisk (*) will only be searched if you have set the :ref:`SITE_SPECIFIC_TEMPLATE_DIRS` setting to ``True`` for your project.

**For the first/top level menu items:**

1. ``"menus/{{ current_site.domain }}/main/level_1.html"`` *
2. ``"menus/{{ current_site.domain }}/main/menu.html"`` *
3. ``"menus/{{ current_site.domain }}/main_menu.html"`` *
4. ``"menus/main/level_1.html"``
5. ``"menus/main/menu.html"``
6. ``"menus/main_menu.html"``

**For any sub-menus:**

1. ``"menus/{{ current_site.domain }}/level_{{ current_level }}.html"`` *
2. ``"menus/{{ current_site.domain }}/sub_menu.html"`` *
3. ``"menus/{{ current_site.domain }}/main_sub_menu.html"`` *
4. ``"menus/{{ current_site.domain }}/sub_menu.html"`` *
5. ``"menus/main/level_{{ current_level }}.html"``
6. ``"menus/main/sub_menu.html"``
7. ``"menus/main_sub_menu.html"``
8. ``"menus/sub_menu.html"``

**Examples**

For a multi-level main menu that displays three levels of links, your templates directory might look like this:
::

    templates
    └── menus
        └── main
            ├── level_1.html  # Used by {% main_menu %} for the 1st level
            ├── level_2.html  # Used by {% sub_menu %} for the 2nd level
            └── level_3.html  # Used by {% sub_menu %} for the 3rd level


.. _custom_templates_flat_menu:

Preferred template paths for ``{% flat_menu %}`` 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For flat menus, the tag also uses the `handle` field of the specific menu being rendered, so that you can have wagtailmenus use different templates for different menus.

.. NOTE::
    Template paths marked with an asterisk (*) are only searched if you have set the :ref:`SITE_SPECIFIC_TEMPLATE_DIRS` setting to ``True`` for your project.

**For the first/top level menu items:**

1. ``"menus/{{ current_site.domain }}/flat/{{ menu.handle }}/level_1.html"`` *
2. ``"menus/{{ current_site.domain }}/flat/{{ menu.handle }}/menu.html"`` *
3. ``"menus/{{ current_site.domain }}/flat/{{ menu.handle }}.html"`` *
4. ``"menus/{{ current_site.domain }}/{{ menu.handle }}/level_1.html"`` *
5. ``"menus/{{ current_site.domain }}/{{ menu.handle }}/menu.html"`` *
6. ``"menus/{{ current_site.domain }}/{{ menu.handle }}.html"`` *
7. ``"menus/{{ current_site.domain }}/flat/level_1.html"`` *
8. ``"menus/{{ current_site.domain }}/flat/default.html"`` *
9. ``"menus/{{ current_site.domain }}/flat/menu.html"`` *
10. ``"menus/{{ current_site.domain }}/flat_menu.html"`` *
11. ``"menus/flat/{{ menu.handle }}/level_1.html"``
12. ``"menus/flat/{{ menu.handle }}/menu.html"``
13. ``"menus/flat/{{ menu.handle }}.html"``
14. ``"menus/{{ menu.handle }}/level_1.html"``
15. ``"menus/{{ menu.handle }}/menu.html"``
16. ``"menus/{{ menu.handle }}.html"``
17. ``"menus/flat/level_1.html"``
18. ``"menus/flat/default.html"``
19. ``"menus/flat/menu.html"``
20. ``"menus/flat_menu.html"``

**For any sub-menus:**

1. ``"menus/{{ current_site.domain }}/flat/{{ menu.handle }}/level_{{ current_level }}.html"`` *
2. ``"menus/{{ current_site.domain }}/flat/{{ menu.handle }}/sub_menu.html"`` *
3. ``"menus/{{ current_site.domain }}/flat/{{ menu.handle }}_sub_menu.html"`` *
4. ``"menus/{{ current_site.domain }}/{{ menu.handle }}/level_{{ current_level }}.html"`` *
5. ``"menus/{{ current_site.domain }}/{{ menu.handle }}/sub_menu.html"`` *
6. ``"menus/{{ current_site.domain }}/{{ menu.handle }}_sub_menu.html"`` *
7. ``"menus/{{ current_site.domain }}/flat/level_{{ current_level }}.html"`` *
8. ``"menus/{{ current_site.domain }}/flat/sub_menu.html"`` *
9. ``"menus/{{ current_site.domain }}/sub_menu.html"`` *
10. ``"menus/flat/{{ menu.handle }}/level_{{ current_level }}.html"``
11. ``"menus/flat/{{ menu.handle }}/sub_menu.html"``
12. ``"menus/flat/{{ menu.handle }}_sub_menu.html"``
13. ``"menus/{{ menu.handle }}/level_{{ current_level }}.html"``
14. ``"menus/{{ menu.handle }}/sub_menu.html"``
15. ``"menus/{{ menu.handle }}_sub_menu.html"``
16. ``"menus/flat/level_{{ current_level }}.html"``
17. ``"menus/flat/sub_menu.html"``
18. ``"menus/sub_menu.html"``

**Examples**

For a flat menu with the handle ``info`` that is required to show two levels of menu items, your templates directory might look like this:
::

    templates
    └── menus
        └── info
            ├── level_1.html  # Used by the {% flat_menu %} tag for the 1st level
            └── level_2.html  # Used by the {% sub_menu %} tag for the 2nd level


Or, if the ``info`` menu only ever needed to show one level of menu items, you might prefer to keep things simple, like so:
::

    templates
    └── menus
        └── info.html 


If your were happy for most of your flat menus to share the same templates, you might put those common templates in the same folder where they'd automatically get selected for all flat menus:
::

    templates
    └── menus
        └── flat
            ├── level_1.html  # Used by the {% flat_menu %} tag for the 1st level
            ├── level_2.html  # Used by the {% sub_menu %} tag for the 2nd level
            └── level_3.html  # Used by the {% sub_menu %} tag for the 3rd level


Building on the above example, you could then override menu templates for certain menus as required, by putting templates in a preferred location for just those menus. For example:
::

    templates
    └── menus
        └── flat
            ├── level_1.html 
            ├── level_2.html 
            ├── level_3.html 
            ├── info
            |   |   # This location is preferred when rendering an 'info' menu
            |   └── level_2.html  # Only override the level 2 template
            └── contact
                |   # This location is preferred when rendering a 'contact' menu
                └── level_1.html  # Only override the level 1 template


With the above structure, the following templates would be used for rendering the ``info`` menu if three levels were needed:

1. `menus/flat/level_1.html`
2. `menus/flat/info/level_2.html`
3. `menus/flat/level_3.html`

For rendering a ``contact`` menu, the following templates would be used:

1. `menus/flat/contact/level_1.html`
2. `menus/flat/level_2.html`
3. `menus/flat/level_3.html`

The above structure would work, but it's not ideal. Imagine if a new front-end developer joined the team, and had no experience with wagtailmenus, or even if you came back to the project after not working with wagtailmenus for a while - It wouldn't be so easy to figure out which templates were being used by each menu. A better approach might be to do something like this:
::

    templates
        └── menus
            └── flat
                |   # Still used by default (e.g. for menus with different handles)
                ├── level_1.html 
                ├── level_2.html 
                ├── level_3.html 
                ├── info
                |   |   # This location is preferred when rendering an 'info' menu
                |   ├── level_1.html  # {% extends 'menus/flat/level_1.html' %}
                |   └── level_2.html  # Our custom template from before
                └── contact
                    |   # This location is preferred when rendering a 'contact' menu
                    ├── level_1.html  # Our custom template from before
                    └── level_2.html  # {% extends 'menus/flat/level_2.html' %}


That's better, but you might even like to make the ``info`` and ``contact`` templates even easier to find, by moving those folders out to the root ``menus`` folder.
::

    templates
        └── menus
            ├── flat
            |   |   # Still used by default (e.g. for menus with different handles)
            |   ├── level_1.html 
            |   ├── level_2.html 
            |   └── level_3.html 
            ├── info
            |   |   # This location is still preferred when rendering an 'info' menu
            |   ├── level_1.html  # {% includes 'menus/flat/level_1.html' %}
            |   └── level_2.html  # Our custom template from before
            └── contact
                |   # This location is still preferred when rendering a 'contact' menu
                ├── level_1.html  # Our custom template from before
                └── level_2.html  # {% includes 'menus/flat/level_2.html' %}


The templates in the ``info`` and ``contact`` folders will still be preferred over the ones in ``flat``, because the folder names are more specific.


.. _custom_templates_section_menu:

Preferred template paths for ``{% section_menu %}`` 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. NOTE::
    Template paths marked with an asterisk (*) are only searched if you have set the :ref:`SITE_SPECIFIC_TEMPLATE_DIRS` setting to ``True`` for your project.

**For the first/top level menu items:**

1. ``"menus/{{ current_site.domain }}/section/level_1.html"`` *
2. ``"menus/{{ current_site.domain }}/section/menu.html"`` *
3. ``"menus/{{ current_site.domain }}/section_menu.html"`` *
4. ``"menus/section/level_1.html"``
5. ``"menus/section/menu.html"``
6. ``"menus/section_menu.html"``

**For any sub-menus:**

1. ``"menus/{{ current_site.domain }}/section/level_{{ current_level }}.html"`` *
2. ``"menus/{{ current_site.domain }}/section/sub_menu.html"`` *
3. ``"menus/{{ current_site.domain }}/section_sub_menu.html"`` *
4. ``"menus/{{ current_site.domain }}/sub_menu.html"`` *
5. ``"menus/section/level_{{ current_level }}.html"``
6. ``"menus/section/sub_menu.html"``
7. ``"menus/section_sub_menu.html"``
8. ``"menus/sub_menu.html"``

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
    Template paths marked with an asterisk (*) are only searched if you have set the :ref:`SITE_SPECIFIC_TEMPLATE_DIRS` setting to ``True`` for your project.

**For the first/top level menu items:**

1. ``"menus/{{ current_site.domain }}/children/level_1.html"`` *
2. ``"menus/{{ current_site.domain }}/children/menu.html"`` *
3. ``"menus/{{ current_site.domain }}/children_menu.html"`` *
4. ``"menus/children/level_1.html"``
5. ``"menus/children/menu.html"``
6. ``"menus/children_menu.html"``

**For any sub-menus:**

1. ``"menus/{{ current_site.domain }}/children/level_{{ current_level }}.html"`` *
2. ``"menus/{{ current_site.domain }}/children/sub_menu.html"`` *
3. ``"menus/{{ current_site.domain }}/children_sub_menu.html"`` *
4. ``"menus/{{ current_site.domain }}/sub_menu.html"`` *
5. ``"menus/children/level_{{ current_level }}.html"``
6. ``"menus/children/sub_menu.html"``
7. ``"menus/children_sub_menu.html"``
8. ``"menus/sub_menu.html"``

**Examples**

If your project needs multi-level children menus, displaying two levels of links, your templates directory might look something like this:
::

    templates
    └── menus
        └── children
            ├── level_1.html  # Used by the {% children_menu %} tag for the 1st level
            └── level_2.html  # Used by the {% sub_menu %} tag for the 2nd level 


Or, if you only need single-level children menus, you might structure things more simply, like so:
::

    templates
    └── menus
        └── children_menu.html


.. _using_a_consistent_template_structure:

Using a consistent template structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Even if the various menus in your project tend to share a lot of common templates between them, for the sake of consistency, it might pay you to follow a 'level-specific' pattern of template definition for each menu, even if some of the templates simply use ``{% extends %}`` or ``{% include %}`` to include a common template. It'll make it much easier to identify which menu templates are being used by which menus at a later time.


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
