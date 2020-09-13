
.. _hooks:

===========================
Using hooks to modify menus
===========================

On loading, Wagtail will search for any app with the file ``wagtail_hooks.py`` and execute the contents. This provides a way to register your own functions to execute at certain points in Wagtail's execution, such as when a ``Page`` object is saved or when the main menu is constructed.

Registering functions with a Wagtail hook is done through the ``@hooks.register`` decorator:

.. code-block:: python

  from wagtail.core import hooks

  @hooks.register('name_of_hook')
  def my_hook_function(arg1, arg2...)
      # your code here


Alternatively, ``hooks.register`` can be called as an ordinary function, passing in the name of the hook and a handler function defined elsewhere:

.. code-block:: python

  hooks.register('name_of_hook', my_hook_function)


Wagtailmenus utilises this same 'hooks' mechanism to allow you make modifications to menus at certain points during the rendering process.

.. contents::
    :local:
    :depth: 2


Hooks for modifying QuerySets
=============================

When a menu instance is gathering the data it needs to render itself, it typically uses one or more QuerySets to fetch ``Page`` and ``MenuItem`` data from the database. These hooks allow you to modify those QuerySets before they are evaluated, allowing you to efficiently control menu contents.

If you need to override a lot of menu class behaviour, and you're comfortable with the idea of subclassing the existing classes and models to override the necessary methods, you might want to look at :ref:`custom_menu_classes`. But, if all you want to do is change the result of a menu's ``get_base_page_queryset()`` or ``get_base_menuitem_queryset()`` (say, to limit the links that appear based on the permissions of the currently logged-in user), you may find it quicker & easier to use the following hooks instead.

.. _menus_modify_base_page_queryset:

menus_modify_base_page_queryset
-------------------------------

Whenever a menu needs ``Page`` data, the menu's ``get_base_page_queryset()`` method is called to get a 'base' queryset, which then has additional ``filter()`` and ``exclude()`` statements added to it as required.

By default, ``get_base_page_queryset()`` applies a few simple filters to prevent certain pages appearing in your menus:


.. code-block:: python

    Page.objects.filter(live=True, expired=False, show_in_menus=True)


However, if you'd like to filter this result down further, you can do so using something like the following:


.. NOTE::
    The below example shows only a subset of the arguments that are passed to methods using this hook. For a full list of the arguments supplied, see the :ref:`hooks_argument_reference` below.


.. code-block:: python

    from wagtail.core import hooks

    @hooks.register('menus_modify_base_page_queryset')
    def make_some_changes(
        queryset, request, menu_instance, original_menu_tag, current_site,
        **kwargs
    ):
        """
        Ensure only pages 'owned' by the currently logged in user are included.
        NOTE: MUST ALWAYS RETURN A QUERYSET
        """
        if not request.user.is_authenticated():
            return queryset.none()
        return queryset.filter(owner=request.user)


This would ensure that only pages 'owned' by currently logged-in user will appear in menus. And the changes will be applied to ALL types of menu, regardless of what template tag is being called to do the rendering.

Or, if you only wanted to change the queryset for a menu of a specific type, you could modify the code slightly like so:


.. code-block:: python

    from wagtail.core import hooks

    @hooks.register('menus_modify_base_page_queryset')
    def make_some_changes(
        queryset, request, menu_instance, original_menu_tag, current_site,
        **kwargs
    ):
        """
        Ensure only pages 'owned' by the currently logged in user are included,
        but only for 'main' or 'flat' menus.
        NOTE: MUST ALWAYS RETURN A QUERYSET
        """
        if menu_type in ('main_menu', 'flat_menu'):
            if not request.user.is_authenticated():
                return queryset.none()
            queryset = queryset.filter(owner=request.user)

        return queryset  # always return a queryset


.. _menus_modify_base_menuitem_queryset:

menus_modify_base_menuitem_queryset
-----------------------------------

When rendering a main or flat menu, top-level items are defined in the CMS, so the menu must fetch that data first, before it can work out whatever additional data is required for rendering.

By default, ``get_base_menuitem_queryset()`` simply returns all of the menu items that were defined in the CMS. Any page data is then fetched separately (using ``get_base_page_queryset()``), and the two results are combined to ensure that only links to appropriate pages are included in the menu being rendered.

However, if you'd only like to include a subset of the CMS-defined menu item, or make any further modifications, you can do so using something like the following:


.. NOTE::
    The below example shows only a subset of the arguments that are passed to methods using this hook. For a full list of the arguments supplied, see the :ref:`hooks_argument_reference` below.


.. code-block:: python

    from wagtail.core import hooks

    @hooks.register('menus_modify_base_menuitem_queryset')
    def make_some_changes(
        queryset, request, menu_instance, original_menu_tag, current_site,
        **kwargs
    ):
        """
        If the request is from a specific site, and the current user is
        authenticated, don't show links to some custom URLs.
        NOTE: MUST ALWAYS RETURN A QUERYSET
        """
        if(
            current_site.hostname.startswith('intranet.') and
            request.user.is_authenticated()
        ):
            queryset = queryset.exclude(handle__contains="visiting-only")
        return queryset  # always return a queryset


These changes would be applied to all menu types that use menu items to define the top-level (main and flat menus). If you only wanted to change the queryset for a flat menus, or even a specific flat menu, you could modify the code slightly like so:


.. code-block:: python

    from wagtail.core import hooks

    @hooks.register('menus_modify_base_menuitem_queryset')
    def make_some_changes(
        queryset, request, menu_instance, original_menu_tag, current_site,
        **kwargs
    ):
        """
        When generating a flat menu with the 'action-links' handle, and the
        request is for a specific site, and the current user is authenticated,
        don't show links to some custom URLs.
        NOTE: MUST ALWAYS RETURN A QUERYSET
        """
        if(
            original_menu_tag == 'flat_menu' and
            menu_instance.handle == 'action-links' and
            current_site.hostname.startswith('intranet.') and
            request.user.is_authenticated()
        ):
            queryset = queryset.exclude(handle__contains="visiting-only")
        return queryset  # always return a queryset


Hooks for modifying menu items
==============================

While the above tags are concerned with modifying the data used in a menu, the following hooks are called later on in the rendering process, and allow you to modify the list of ``MenuItem`` or ``Page`` objects before they are sent to a template to be rendered.

There are two hooks you can use to modify menu items, which are called at different stages of preparation.


.. _menus_modify_raw_menu_items:

menus_modify_raw_menu_items
---------------------------

This hook allows you to modify the list **before** it is 'primed' (a process that sets ``href``, ``text``, ``active_class`` and ``has_children_in_menu`` attributes on each item), and **before** being sent to a parent page's ``modify_submenu_items()`` method for further modification (see :ref:`manipulating_submenu_items`).

.. NOTE::
    The below example shows only a subset of the arguments that are passed to methods using this hook. For a full list of the arguments supplied, see the :ref:`hooks_argument_reference` below.


.. code-block:: python

    from wagtail.core import hooks

    @hooks.register('menus_modify_raw_menu_items')
    def make_some_changes(
        menu_items, request, parent_page, original_menu_tag, menu_instance,
        current_level, **kwargs
    ):
        """
        When rendering the first level of a 'section menu', add a copy of the
        first page to the end of the list.

        NOTE: prime_menu_items() will attempt to add 'href', 'text' and other
        attributes to these items before rendering, so ideally, menu items
        should all be `MenuItem` or `Page` instances.
        """
        if original_menu_tag == 'section_menu' and current_level == 1:
            # Try/except in case menu_items is an empty list
            try:
                menu_items.append(menu_items[0])
            except KeyError:
                pass
        return menu_items  # always return a list


The modified list of menu items will then continue to be processed as normal, being passed to the menu's 'prime_menu_items()' method for priming, and then on to the parent page's ``modify_submenu_items()`` for further modification.


.. _menus_modify_primed_menu_items:

menus_modify_primed_menu_items
------------------------------

This hook allows you to modify the list of items **after** they have been 'primed' and the modified by a parent page's ``modify_submenu_items()`` methods (see :ref:`manipulating_submenu_items`).

.. NOTE::
    The below example shows only a subset of the arguments that are passed to methods using this hook. For a full list of the arguments supplied, see the :ref:`hooks_argument_reference` below.


.. code-block:: python

    from wagtail.core import hooks

    @hooks.register('menus_modify_primed_menu_items')
    def make_some_changes(
        menu_items, request, parent_page, original_menu_tag, menu_instance,
        current_level, **kwargs
    ):
        """
        When rendering the first level of a 'main menu', add an additional
        link to the RKH website

        NOTE: This result won't undergo any more processing before sending to
        a template for rendering, so you may need to set 'href' and
        'text' attributes / keys so that those values are picked up by menu
        templates.
        """
        if original_menu_tag == 'main_menu' and current_level == 1:
            # Just adding a simple dict here, as these values are all the
            # template needs to render the link
            menu_items.append({
                'href': 'https://rkh.co.uk',
                'text': 'VISIT RKH.CO.UK',
                'active_class': 'external',
            })
        return menu_items  # always return a list


.. _hooks_argument_reference:

Argument reference
==================

In the above examples, ``**kwargs`` is used in hook method signatures to make them *accepting* of other keyword arguments, without having to declare every single argument that should be passed in. Using this approach helps create leaner, tidier code, and also makes it more 'future-proof', since the methods will automatically accept any new arguments that may be added by wagtailmenus in future releases.

Below is a full list of the additional arguments that are passed to methods using the above hooks:

``request``
    The ``HttpRequest`` instance that the menu is currently being rendered for.

``parent_context``
    The ``Context`` instance that the menu is being rendered from.

``parent_page``
    If the menu being rendered is showing 'children' of a specific page, this will be the ``Page`` instance who's children pages are being displayed. The value might also be ``None`` if no parent page is involved. For example, if rendering the top level items of a main or flat menu.

``menu_tag``
    The name of the tag that was called to render the current part of the menu. If rendering the first level of a menu, this will have the same value as ``original_menu_tag``. If not, it will have the value `'sub_menu'` (unless you're using custom tags that pass a different 'tag_name' value to the menu class's 'render_from_tag' method)

``original_menu_tag``
    The name of the tag that was called to initiate rendering of the menu that is currently being rendered. For example, if you're using the ``main_menu`` tag to render a multi-level main menu, even though ``sub_menu`` may be called to render subsequent additional levels, 'original_menu_tag' should retain the value ``'main_menu'``. Should be one of: ``'main_menu'``, ``'flat_menu'``, ``'section_menu'`` or ``'children_menu'``. Comparable to the ``menu_type`` values supplied to other hooks.

``menu_instance``
    The menu instance that is supplying the data required to generate the current menu. This could be an instance of a model class, like ``MainMenu`` or ``FlatMenu``, or a standard python class like ``ChildrenMenu`` or ``SectionMenu``.

``original_menu_instance``
    The menu instance that is supplying the data required to generate the current menu. This could be an instance of a model class, like ``MainMenu`` or ``FlatMenu``, or a standard python class like ``ChildrenMenu`` or ``SectionMenu``.

``current_level``
    An integer value indicating the 'level' or 'depth' that is currently being rendered in the process of rendering a multi-level menu. This will start at `1` for the first/top-level items of a menu, and increment by `1` for each additional level.

``max_levels``
    An integer value indicating the maximum number of levels that should be rendered for the current menu. This will either have been specified by the developer using the ``max_levels`` argument of a menu tag, or might have been set in the CMS for a specific ``MainMenu`` or ``FlatMenu`` instance.

``current_site``
    A Wagtail ``Site`` instance, indicating the site that the current request is for (usually also available as ``request.site``)

``current_page``
    A Wagtail ``Page`` instance, indicating what wagtailmenus believes to be the page that is currently being viewed / requested by a user. This might be ``None`` if you're using additional views in your project to provide functionality at URLs that don't map to a ``Page`` in Wagtail.

``current_page_ancestor_ids``
    A list of ids of ``Page`` instances that are an 'ancestor' of ``current_page``.

``current_section_root_page``
    If ``current_page`` has a value, this will be the top-most ancestor of that page, from just below the site's root page. For example, if your page tree looked like the following::

        Home (Set as 'root page' for the site)
        ├── About us
        ├── What we do
        ├── Careers
        │   ├── Vacancy one
        │   └── Vacancy two
        ├── News & events
        │   ├── News
        │   │   ├── Article one
        │   │   └── Article two
        │   └── Events
        └── Contact us

    If the current page was 'Vacancy one', the section root page would be 'Careers'. Or, if the current page was 'Article one', the section root page would be 'News & events'.

``allow_repeating_parents``
    A boolean value indicating the preferred policy for having pages that subclass ``MenuPageMixin`` add a repeated versions of themselves to it's children pages (when rendering a `sub_menu` for that page). For more information see: :ref:`menupage_and_menupagemixin`.

``apply_active_classes``
    A boolean value indicating the preferred policy for setting ``active_class`` attributes on menu items for the current menu.

``use_absolute_page_urls``
    A boolean value indicating the preferred policy for using full/absolute page URLs for menu items representing pages (observed by ``prime_menu_items()`` when setting the ``href`` attribute on each menu item). In most cases this will be ``False``, as the default behaviour is to use 'relative' URLs for pages.
