=======================
Template tags reference
=======================

.. contents::
    :local:
    :depth: 2


.. _main_menu:

The ``main_menu`` tag
=====================

The ``main_menu`` tag allows you to display the ``MainMenu`` defined for the current site in your Wagtail project, with CSS classes automatically applied to each item to indicate the current page or ancestors of the current page. It also does a few sensible things, like never adding the 'ancestor' class for a homepage link, or outputting children for it.

Example usage
-------------

.. code-block:: html

    ...
    {% load menu_tags %}
    ...
    {% main_menu max_levels=3 use_specific=USE_SPECIFIC_TOP_LEVEL template="menus/custom_main_menu.html" sub_menu_template="menus/custom_sub_menu.html" %}
    ...


.. _main_menu_args:

Supported arguments
-------------------


``show_multiple_levels``
~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``True``
=========  ===================  =============

Adding ``show_multiple_levels=False`` to the tag in your template is essentially a more descriptive way of adding ``max_levels`` to ``1``.


``max_levels``
~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``int``              ``None``
=========  ===================  =============

Provide an integer value to override the ``max_levels`` field value defined on your menu. Controls how many levels should be rendered (when ``show_multiple_levels`` is ``True``).


``use_specific``
~~~~~~~~~~~~~~~~

=========  ==========================================   =============
Required?  Expected value type                          Default value
=========  ==========================================   =============
No         ``int`` (see :ref:`specific_pages_values`)   ``None``
=========  ==========================================   =============

Provide a value to override the ``use_specific`` field value defined on your main menu. Allows you to control how wagtailmenus makes use of ``PageQuerySet.specific()`` and ``Page.specific`` when rendering the menu. For more information and examples, see: :ref:`specific_pages_tag_args`.


``allow_repeating_parents``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``True``
=========  ===================  =============

Item repetition settings set on each page are respected by default, but you can add ``allow_repeating_parents=False`` to ignore them, and not repeat any pages in sub-menus when rendering multiple levels.


``apply_active_classes``
~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``True``
=========  ===================  =============

The tag will attempt to add 'active' and 'ancestor' CSS classes to the menu items (where applicable) to indicate the active page and ancestors of that page. To disable this behaviour, add ``apply_active_classes=False`` to the tag in your template.

You can change the CSS class strings used to indicate 'active' and 'ancestor' statuses by utilising the :ref:`ACTIVE_CLASS` and :ref:`ACTIVE_ANCESTOR_CLASS` settings.


``template``
~~~~~~~~~~~~

=========  =======================  =============
Required?  Expected value type      Default value
=========  =======================  =============
No         Template path (``str``)  ``''``
=========  =======================  =============

Lets you render the menu to a template of your choosing. If not provided, wagtailmenus will attempt to find a suitable template automatically.

For more information about overriding templates, see: :ref:`custom_templates`.

For a list of preferred template paths this tag, see: :ref:`custom_templates_main_menu`.


``sub_menu_template``
~~~~~~~~~~~~~~~~~~~~~

=========  =======================  =============
Required?  Expected value type      Default value
=========  =======================  =============
No         Template path (``str``)  ``''``
=========  =======================  =============

Lets you specify a template to be used for rendering sub menus. All subsequent calls to ``{% sub_menu %}`` within the context of the section menu will use this template unless overridden by providing a ``template`` value to ``{% sub_menu %}`` in a menu template. If not provided, wagtailmenus will attempt to find a suitable template automatically.

For more information about overriding templates, see: :ref:`custom_templates`.

For a list of preferred template paths this tag, see: :ref:`custom_templates_main_menu`.


``use_absolute_page_urls``
~~~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``False``
=========  ===================  =============


By default, relative page URLs are used for the ``href`` attribute on page links when rendering your menu. If you wish to use absolute page URLs instead, add ``use_absolute_page_urls=True`` to the ``main_menu`` tag in your template. The preference will also be respected automatically by any subsequent calls to ``{% sub_menu %}`` during the course of rendering the menu (unless explicitly overridden in custom menu templates ).

    .. NOTE:
        Using absolute URLs will have a negative impact on performance, especially if you're using a Wagtail version prior to 1.11.


.. _flat_menu:

The ``flat_menu`` tag
=====================


Example usage
-------------

.. code-block:: html
    
    ...
    {% load menu_tags %}
    ...
    {% flat_menu 'footer' max_levels=1 show_menu_heading=False  use_specific=USE_SPECIFIC_TOP_LEVEL  fall_back_to_default_site_menus=True %}
    ...


.. _flat_menu_args:

Supported arguments
-------------------


``handle``
~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
**Yes**    ``str``              ``None``
=========  ===================  =============

The unique handle for the flat menu you want to render, e.g. ``'info'``,
``'contact'``, or ``'services'``. You don't need to include the ``handle`` key if supplying as the first argument to the tag (you can just do ``{% flat_menu 'menu_handle' %}``).


``show_menu_heading``
~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``True``
=========  ===================  =============

Passed through to the template used for rendering, where it can be used to conditionally display a heading above the menu.


``show_multiple_levels``
~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``True``
=========  ===================  =============

Flat menus are designed for outputting simple, flat lists of links. But, you can alter the ``max_levels`` field value on your ``FlatMenu`` objects in the CMS to enable multi-level output for specific menus. If you want to absolutely never show anything but the ``MenuItem`` objects defined on the menu, you can override this behaviour by adding ``show_multiple_levels=False`` to the tag in your template.


``max_levels``
~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``int``              ``None``
=========  ===================  =============

Provide an integer value to override the ``max_levels`` field value defined on your menu. Controls how many levels should be rendered (when ``show_multiple_levels`` is ``True``).


``use_specific``
~~~~~~~~~~~~~~~~

=========  ==========================================  =============
Required?  Expected value type                         Default value
=========  ==========================================  =============
No         ``int`` (see :ref:`specific_pages_values`)  ``None``
=========  ==========================================  =============

Provide a value to override the ``use_specific`` field value defined on your flat menu. Allows you to control how wagtailmenus makes use of ``PageQuerySet.specific()`` and ``Page.specific`` when rendering the menu. 

For more information and examples, see: :ref:`specific_pages_tag_args`.


``apply_active_classes``
~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``False``
=========  ===================  =============

Unlike ``main_menu`` and ``section_menu``, ``flat_menu`` will NOT attempt to add ``'active'`` and ``'ancestor'`` classes to the menu items by default, as this is often not useful. You can override this by adding ``apply_active_classes=true`` to the tag in your template.

You can change the CSS class strings used to indicate 'active' and 'ancestor' statuses by utilising the :ref:`ACTIVE_CLASS` and :ref:`ACTIVE_ANCESTOR_CLASS` settings.


``allow_repeating_parents``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``True``
=========  ===================  =============

Repetition-related settings on your pages are respected by default, but you can add ``allow_repeating_parents=False`` to ignore them, and not repeat any pages in sub-menus when rendering. Please note that using this option will only have an effect if ``use_specific`` has a value of ``1`` or higher.


``fall_back_to_default_site_menus``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``False``
=========  ===================  =============

When using the ``flat_menu`` tag, wagtailmenus identifies the 'current site', and attempts to find a menu for that site, matching the ``handle`` provided. By default, if no menu is found for the current site, nothing is rendered. However, if ``fall_back_to_default_site_menus=True`` is provided, wagtailmenus will search search the 'default' site (In the CMS, this will be the site with the '**Is default site**' checkbox ticked) for a menu with the same handle, and use that instead before giving up. 

The default value can be changed to ``True`` by utilising the :ref:`FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS` setting.


``template``
~~~~~~~~~~~~

=========  =======================  =============
Required?  Expected value type      Default value
=========  =======================  =============
No         Template path (``str``)  ``''``
=========  =======================  =============

Lets you render the menu to a template of your choosing. If not provided, wagtailmenus will attempt to find a suitable template automatically.

For more information about overriding templates, see: :ref:`custom_templates`.

For a list of preferred template paths this tag, see: :ref:`custom_templates_flat_menu`.


``sub_menu_template``
~~~~~~~~~~~~~~~~~~~~~

=========  =======================  =============
Required?  Expected value type      Default value
=========  =======================  =============
No         Template path (``str``)  ``''``
=========  =======================  =============

Lets you specify a template to be used for rendering sub menus (if enabled using ``show_multiple_levels``). All subsequent calls to ``{% sub_menu %}`` within the context of the flat menu will use this template unless overridden by providing a ``template`` value to ``{% sub_menu %}`` directly in a menu template. If not provided, wagtailmenus will attempt to find a suitable template automatically.

For more information about overriding templates, see: :ref:`custom_templates`.

For a list of preferred template paths this tag, see: :ref:`custom_templates_flat_menu`.


``use_absolute_page_urls``
~~~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``False``
=========  ===================  =============

By default, relative page URLs are used for the ``href`` attribute on page links when rendering your menu. If you wish to use absolute page URLs instead, add ``use_absolute_page_urls=True`` to the ``{% flat_menu %}`` tag in your template. The preference will also be respected automatically by any subsequent calls to ``{% sub_menu %}`` during the course of rendering the menu (unless explicitly overridden in custom menu templates). 

    .. NOTE:
        Using absolute URLs will have a negative impact on performance, especially if you're using a Wagtail version prior to 1.11.


.. _section_menu:

The ``section_menu`` tag
========================

The ``section_menu`` tag allows you to display a context-aware, page-driven menu in your project's templates, with CSS classes automatically applied to each item to indicate the active page or ancestors of the active page. 


Example usage
------------- 

.. code-block:: html
    
    ...
    {% load menu_tags %}
    ...
    {% section_menu max_levels=3 use_specific=USE_SPECIFIC_OFF template="menus/custom_section_menu.html" sub_menu_template="menus/custom_section_sub_menu.html" %}
    ...


.. _section_menu_args:

Supported arguments
-------------------


``show_section_root``
~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``True``
=========  ===================  =============

Passed through to the template used for rendering, where it can be used to conditionally display the root page of the current section.


``max_levels``
~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``int``              ``2``
=========  ===================  =============

Lets you control how many levels of pages should be rendered (the section root page does not count as a level, just the first set of pages below it). If you only want to display the first level of pages below the section root page (whether pages linked to have children or not), add ``max_levels=1`` to the tag in your template. You can display additional levels by providing a higher value.

The default value can be changed by utilising the :ref:`DEFAULT_SECTION_MENU_MAX_LEVELS` setting.


``use_specific``
~~~~~~~~~~~~~~~~

=========  ==========================================  =============
Required?  Expected value type                         Default value
=========  ==========================================  =============
No         ``int`` (see :ref:`specific_pages_values`)  ``1`` (Auto)
=========  ==========================================  =============

Allows you to control how wagtailmenus makes use of ``PageQuerySet.specific()`` and ``Page.specific`` when rendering the menu, helping you to find the right balance between functionality and performance.

For more information and examples, see: :ref:`specific_pages_tag_args`.

The default value can be altered by utilising the :ref:`DEFAULT_SECTION_MENU_USE_SPECIFIC` setting.


``show_multiple_levels``
~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``True``
=========  ===================  =============

Adding ``show_multiple_levels=False`` to the tag in your template essentially overrides ``max_levels`` to ``1``. It's just a little more descriptive.  


``apply_active_classes``
~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``True``
=========  ===================  =============

The tag will add 'active' and 'ancestor' classes to the menu items where applicable, to indicate the active page and ancestors of that page. To disable this behaviour, add ``apply_active_classes=False`` to the tag in your template.

You can change the CSS class strings used to indicate 'active' and 'ancestor' statuses by utilising the :ref:`ACTIVE_CLASS` and :ref:`ACTIVE_ANCESTOR_CLASS` settings.


``allow_repeating_parents``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``True``
=========  ===================  =============

Repetition-related settings on your pages are respected by default, but you can add ``allow_repeating_parents=False`` to ignore them, and not repeat any pages in sub-menus when rendering. Please note that using this option will only have an effect if ``use_specific`` has a value of ``1`` or higher.


``template``
~~~~~~~~~~~~

=========  =======================  =============
Required?  Expected value type      Default value
=========  =======================  =============
No         Template path (``str``)  ``''``
=========  =======================  =============

Lets you render the menu to a template of your choosing. If not provided, wagtailmenus will attempt to find a suitable template automatically.

For more information about overriding templates, see: :ref:`custom_templates`.

For a list of preferred template paths this tag, see: :ref:`custom_templates_section_menu`.


``sub_menu_template``
~~~~~~~~~~~~~~~~~~~~~

=========  =======================  =============
Required?  Expected value type      Default value
=========  =======================  =============
No         Template path (``str``)  ``''``
=========  =======================  =============

Lets you specify a template to be used for rendering sub menus. All subsequent calls to ``{% sub_menu %}`` within the context of the section menu will use this template unless overridden by providing a ``template`` value to ``{% sub_menu %}`` in a menu template. If not provided, wagtailmenus will attempt to find a suitable template automatically.

For more information about overriding templates, see: :ref:`custom_templates`.

For a list of preferred template paths this tag, see: :ref:`custom_templates_section_menu`.


``use_absolute_page_urls``
~~~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``False``
=========  ===================  =============

By default, relative page URLs are used for the ``href`` attribute on page links when rendering your menu. If you wish to use absolute page URLs instead, add ``use_absolute_page_urls=True`` to the ``{% section_menu %}`` tag in your template. The preference will also be respected automatically by any subsequent calls to ``{% sub_menu %}`` during the course of rendering the menu (unless explicitly overridden in custom menu templates). 
    
    .. NOTE:
        Using absolute URLs will have a negative impact on performance, especially if you're using a Wagtail version prior to 1.11.


.. _children_menu:

The ``children_menu`` tag
=========================

The ``children_menu`` tag can be used in page templates to display a menu of children of the current page. You can also use the `parent_page` argument to show children of a different page.

Example usage
------------- 

.. code-block:: html
    
    ...
    {% load menu_tags %}
    ...
    {% children_menu some_other_page max_levels=2 use_specific=USE_SPECIFIC_OFF template="menus/custom_children_menu.html" sub_menu_template="menus/custom_children_sub_menu.html" %}
    ...


.. _children_menu_args:

Supported arguments
-------------------


``parent_page``
~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         A ``Page`` object    ``None``
=========  ===================  =============

Allows you to specify a page to output children for. If no alternate page is specified, the tag will automatically use ``self`` from the context to render children pages for the current/active page. 


``max_levels``
~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``int``              ``1``
=========  ===================  =============

Allows you to specify how many levels of pages should be rendered. For example, if you want to display the direct children pages and their children too, add ``max_levels=2`` to the tag in your template.

The default value can be changed by utilising the :ref:`DEFAULT_CHILDREN_MENU_MAX_LEVELS` setting.


``use_specific``
~~~~~~~~~~~~~~~~

=========  ==========================================  =============
Required?  Expected value type                         Default value
=========  ==========================================  =============
No         ``int`` (see :ref:`specific_pages_values`)  ``1`` (Auto)
=========  ==========================================  =============

Allows you to specify how wagtailmenus makes use of ``PageQuerySet.specific()`` and ``Page.specific`` when rendering the menu. 

For more information and examples, see: :ref:`specific_pages_tag_args`.

The default value can be altered by adding a :ref:`DEFAULT_CHILDREN_MENU_USE_SPECIFIC` setting to your project's settings.


``apply_active_classes``
~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``False``
=========  ===================  =============

Unlike ``main_menu`` and `section_menu``, ``children_menu`` will NOT attempt to add ``'active'`` and ``'ancestor'`` classes to the menu items by default, as this is often not useful. You can override this by adding ``apply_active_classes=true`` to the tag in your template.

You can change the CSS class strings used to indicate 'active' and 'ancestor' statuses by utilising the :ref:`ACTIVE_CLASS` and :ref:`ACTIVE_ANCESTOR_CLASS` settings.


``allow_repeating_parents``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``True``
=========  ===================  =============

Repetition-related settings on your pages are respected by default, but you can add ``allow_repeating_parents=False`` to ignore them, and not repeat any pages in sub-menus when rendering. Please note that using this option will only have an effect if ``use_specific`` has a value of ``1`` or higher.


``template``
~~~~~~~~~~~~

=========  =======================  =============
Required?  Expected value type      Default value
=========  =======================  =============
No         Template path (``str``)  ``''``
=========  =======================  =============

Lets you render the menu to a template of your choosing. If not provided, wagtailmenus will attempt to find a suitable template automatically (see below for more details).

For more information about overriding templates, see: :ref:`custom_templates`

For a list of preferred template paths this tag, see: :ref:`custom_templates_children_menu`


``sub_menu_template``
~~~~~~~~~~~~~~~~~~~~~

=========  =======================  =============
Required?  Expected value type      Default value
=========  =======================  =============
No         Template path (``str``)  ``''``
=========  =======================  =============

Lets you specify a template to be used for rendering sub menus. All subsequent calls to ``{% sub_menu %}`` within the context of the section menu will use this template unless overridden by providing a ``template`` value to ``{% sub_menu %}`` in a menu template. If not provided, wagtailmenus will attempt to find a suitable template automatically

For more information about overriding templates, see: :ref:`custom_templates`

For a list of preferred template paths this tag, see: :ref:`custom_templates_children_menu`


``use_absolute_page_urls``
~~~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  =============
Required?  Expected value type  Default value
=========  ===================  =============
No         ``bool``             ``False``
=========  ===================  =============

By default, relative page URLs are used for the ``href`` attribute on page links when rendering your menu. If you wish to use absolute page URLs instead, add ``use_absolute_page_urls=True`` to the ``{% children_menu %}`` tag in your template. The preference will also be respected automatically by any subsequent calls to ``{% sub_menu %}`` during the course of rendering the menu (unless explicitly overridden in custom menu templates).

    .. NOTE:
        Using absolute URLs will have a negative impact on performance,
        especially if you're using a Wagtail version prior to 1.11.


.. _sub_menu:

The ``sub_menu`` tag
====================

The ``sub_menu`` tag is used within menu templates to render additional levels of pages within a menu. It's designed to pick up on variables added to the context by the other menu tags, and so can behave a little unpredictably if called directly, without those context variables having been set. It requires only one parameter to work, which is ``menuitem_or_page``.


Example usage
------------- 

.. code-block:: html
    
    ...
    {% load menu_tags %}
    ...
    {% for item in menu_items %}
        <li class="{{ item.active_class }}">
            <a href="{{ item.href }}">{{ item.text }}</a>
            {% if item.has_children_in_menu %}
                {% sub_menu item %}
            {% endif %}
        </li>
    {% endfor %}
    ...


.. _sub_menu_args:

Supported arguments
-------------------


``menuitem_or_page``
~~~~~~~~~~~~~~~~~~~~

=========  ====================================  ====================================
Required?  Expected value type                   Default value
=========  ====================================  ====================================
**Yes**    An item from the ``menu_items`` list  ``None`` (inherit from original tag)
=========  ====================================  ====================================

When iterating through a list of ``menu_items`` within a menu template, the current 
item must be passed to ``{% sub_menu %}`` so that it knows which page to render a sub-menu for. You don't need to include the ``menuitem_or_page`` key if supplying the value as the first argument to the tag (you can just do ``{% sub_menu item %}``).


``stop_at_this_level``
~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  ====================================
Required?  Expected value type  Default value
=========  ===================  ====================================
No         ``bool``             ``None`` (inherit from original tag)
=========  ===================  ====================================

The ``sub_menu`` tag will automatically figure out whether further levels should be rendered or not by comparing the ``max_levels`` value from the original menu tag with the current level being rendered. However, you can override that behaviour by adding either ``stop_at_this_level=True`` or ``stop_at_this_level=False`` to the tag in a custom menu template.


``apply_active_classes``
~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  ====================================
Required?  Expected value type  Default value
=========  ===================  ====================================
No         ``bool``             ``None`` (inherit from original tag)
=========  ===================  ====================================

Allows you to override the value set by the original tag by adding an alternative value to the ``{% sub_menu %}`` tag in a custom menu template.


``allow_repeating_parents``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  ====================================
Required?  Expected value type  Default value
=========  ===================  ====================================
No         ``bool``             ``None`` (inherit from original tag)
=========  ===================  ====================================

Allows you to override the value set by the original tag by adding an alternative value to the ``{% sub_menu %}`` tag in a custom menu template.


``template``
~~~~~~~~~~~~

=========  =======================  =============
Required?  Expected value type      Default value
=========  =======================  =============
No         Template path (``str``)  ``''``
=========  =======================  =============

Allows you to override the template set by the original menu tag (``sub_menu_template`` in the context) by passing a fixed template path to the  ``{% sub_menu %}`` tag in a custom menu template.

For more information about overriding templates, see: :ref:`custom_templates`


``use_specific``
~~~~~~~~~~~~~~~~

=========  ==========================================  =============
Required?  Expected value type                         Default value
=========  ==========================================  =============
No         ``int`` (see :ref:`specific_pages_values`)  ``None``
=========  ==========================================  =============

Allows you to override the value set on the original tag by adding an alternative value to the ``{% sub_menu %}`` tag in a custom menu template.

For more information and examples, see: :ref:`specific_pages_tag_args`.


``use_absolute_page_urls``
~~~~~~~~~~~~~~~~~~~~~~~~~~

=========  ===================  ====================================
Required?  Expected value type  Default value
=========  ===================  ====================================
No         ``bool``             ``None`` (inherit from original tag)
=========  ===================  ====================================

Allows you to override the value set on the original tag by explicitly adding ``use_absolute_page_urls=True`` or ``use_absolute_page_urls=False`` to a ``{% sub_menu %}`` tag in a custom menu template. 

If ``True``, absolute page URLs will be used for the ``href`` attributes on page links instead of relative URLs.
