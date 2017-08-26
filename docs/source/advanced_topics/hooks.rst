
.. _hooks:

===============================
Using hooks to manipulate menus
===============================

On loading, Wagtail will search for any app with the file ``wagtail_hooks.py`` and execute the contents. This provides a way to register your own functions to execute at certain points in Wagtail's execution, such as when a ``Page`` object is saved or when the main menu is constructed.

Registering functions with a Wagtail hook is done through the ``@hooks.register`` decorator:

.. code-block:: python

  from wagtail.wagtailcore import hooks

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


Hooks for modifying data used in menus
======================================

Menu classes are responsible for fetching all of the data needed for rendering a menu, and feeding it back to the various template tags as and when that data is needed. 

If you need to override a lot of behaviour on menu classes, and you're comfortable with the idea of subclassing the existing classes and models to override the necessary methods, you might want to look at :ref:`custom_menu_classes`. But, if all you want to do is change the result of ``get_base_page_queryset()`` or ``get_base_menuitem_queryset()`` (say, to limit the links that appear based on the currently logged-in user's permissions), you may find it quicker & easier to use the following hooks instead.

.. _menus_modify_base_page_queryset:

menus_modify_base_page_queryset
-------------------------------

Whenever a menu needs ``Page`` data (whether it be for pages selected as menu items in the CMS, or for something entirely page-tree powered), it calls the ``get_base_page_queryset()`` method to get a 'base' queryset to work from, then applies additional ``filter()`` and ``exclude()`` statements to filter the result down further.

By default, ``get_base_page_queryset()`` applies a few simple filters to prevent certain pages appearing in your menus:


.. code-block:: python

    Page.objects.filter(live=True, expired=False, show_in_menus=True)


However, if you'd like to filter this result down further, you can do so using something like the following: 


.. NOTE::
    The below examples only show a subset of the arguments that are passed to methods using the 'menus_modify_base_page_queryset' hook. For a full list of the arguments supplied, see :ref:`arg_reference_menu_hooks` below.


.. code-block:: python

    from wagtail.wagtailcore import hooks

    @hooks.register('menus_modify_base_page_queryset')
    def make_some_changes(
        queryset, request, menu_type, root_page, menu_instance, **kwargs
    ):
        """
        Ensure only pages 'owned' by the currently logged in user are included
        """
        if not request.user.is_authenticated():
            return queryset.none()
        return queryset.filter(owner=self.request.user)


This would ensure that only pages 'owned' by currently logged-in user will appear in menus. And the changes will be applied to ALL types of menu, regardless of what template tag is being called to do the rendering.

Or, if you only wanted to change the queryset for a menu of a specific type, you could modify the code slightly like so:


.. code-block:: python

    from wagtail.wagtailcore import hooks

    @hooks.register('menus_modify_base_page_queryset')
    def make_some_changes(
        queryset, request, menu_type, root_page, menu_instance, **kwargs
    ):
        """
        Ensure only pages 'owned' by the currently logged in user are included,
        but only for 'main' or 'flat' menus
        """
        if menu_type in ('main_menu', 'flat_menu'):
            if not request.user.is_authenticated():
                return queryset.none()
            queryset = queryset.filter(owner=self.request.user)

        return queryset  # always return a queryset


.. _menus_modify_base_menuitem_queryset:

menus_modify_base_menuitem_queryset
-----------------------------------

When rendering a main or flat menu, top-level items are defined in the CMS, so the menu must fetch that data first, before it can work out whatever additional data is required for rendering.

By default, ``get_base_menuitem_queryset()`` simply returns all of the menu items that were defined in the CMS. Any page data is then fetched separately (using ``get_base_page_queryset()``), and the two results are combined to ensure that only links to appropriate pages are included in the menu being rendered.

However, if you'd only like to include a subset of the CMS-defined menu item, or make any further modifications, you can do so using something like the following:


.. NOTE::
    The below examples only show a subset of the arguments that are passed to methods using the 'menus_modify_base_menuitem_queryset' hook. For a full list of the arguments supplied, see :ref:`arg_reference_menu_hooks` below.


.. code-block:: python

    from wagtail.wagtailcore import hooks

    @hooks.register('menus_modify_base_menuitem_queryset')
    def make_some_changes(
        queryset, request, menu_type, menu_instance, **kwargs
    ):
        """
        If the request is from a specific site, and the current user is
        authenticated, don't show links to some custom custom URLs
        """
        if(
            request.site.hostname.startswith('intranet.') and 
            request.user.is_authenticated()
        ):
            queryset = queryset.exclude(handle__contains="visiting-only")
        return queryset  # always return a queryset


These changes would be applied to all menu types that use menu items to define the top-level (main and flat menus). If you only wanted to change the queryset for a flat menus, or even a specific flat menu, you could modify the code slightly like so:


.. code-block:: python

    from wagtail.wagtailcore import hooks

    @hooks.register('menus_modify_base_menuitem_queryset')
    def make_some_changes(
        queryset, request, menu_type, menu_instance, **kwargs
    ):
        """
        When generating a flat menu with the 'action-links' handle, and the
        request is for a specific site, and the current user is authenticated,
        don't show links to some custom custom URLs
        """
        if(
            menu_type == 'flat_menu' and 
            menu_instance.handle == 'action-links' and
            request.site.hostname.startswith('intranet.') and 
            request.user.is_authenticated()
        ):
            queryset = queryset.exclude(handle__contains="visiting-only")
        return queryset  # always return a queryset


.. _arg_reference_menu_hooks:

Argument reference
------------------

In the above examples, ``**kwargs`` is used in hook method signatures to make them *accepting* of other keyword arguments, without having to declare every single argument that should be passed in. Using this approach helps keep code tidier, and also makes it more 'future-proof', since the methods will automatically accept any new arguments that may be added by wagtailmenus in future releases.

Below is a full list of arguments passed that are passed to the above hooks and what they mean:

``queryset``
    The Django ``QuerySet`` instance to be modified. For the 'menus_modify_base_page_queryset' hook, this will be a queryset of ``Page`` objects. For the 'menus_modify_base_menuitem_queryset' hook, this will be a queryset of ``MainMenuItem`` or ``FlatMenuItem`` objects, depending on the type of menu being rendered (or custom menu item models, if you've implemented thrm)

``request``
    The ``HttpRequest`` object that the menu is currently being rendered for

``menu_type``
    A string value indicating the 'type' of menu currently being rendered. Should be one of: ``'main_menu'``, ``'flat_menu'``, ``'section_menu'`` or ``'children_menu'``. Comparable to the ``original_menu_tag`` values supplied to other hooks.

``root_page``
    Supplied to the :ref:`menus_modify_base_page_queryset` hook only. A value will only be provided if the hook is being called from an instance of ``ChildrenMenu`` or ``SecionMenu``, where the contents of the menu is based entirely around a specific page, and it's position in the page tree. For an instance of ChildrenMenu, ``root_page`` will be generally be the page the ``{% children_menu %}`` tag is being rendered on. For an instance of SectionMenu, ``root_page`` will indicate the 'section root' page for the page being rendered (Usually the 'ancestor' page directly below the 'Home page' for the current site).

``menu_instance``
    The menu instance that is supplying the data required to generate the current menu. This could be an instance of a model class, like ``MainMenu`` or ``FlatMenu``, or a standard python class like ``ChildrenMenu`` or ``SectionMenu``.

``max_levels``
    An integer value indicatiing the maxiumum number of levels that should be rendered for the current menu. This will either have been specified by the developer using the ``max_levels`` argument of a menu tag, or might have been set in the CMS for a specific ``MainMenu`` or ``FlatMenu`` instance. 

``use_specific``
    An integer value indicating the preferred policy for using ``PageQuerySet.specific()`` and ``Page.specific`` in rendering the current menu. For more information see: :ref:`specific_pages_tag_args`.


Hooks for modifying menu items before rendering
===============================================

While the above tags are focussed on sourcing data required for a menu, the following hooks are called from within the various menu tags, as they prepare menu items for rendering.

There are two hooks you can use to modify menu items, which are called at different stages of preparation.


.. _menus_modify_raw_menu_items:

menus_modify_raw_menu_items
---------------------------

Whichever menu tag is being used, and whatever the current level being rendered, the tag starts by querying a Menu instance to fetch the items that need to be included as menu items for the current level.

This hook allows you to modify the list of items *as soon as it is fetched* from the menu class, **before** 'priming' (which sets 'href', 'text', 'active_class' and 'has_children_in_menu' attributes on each item), and **before** being sent to any 'modify_submenu_items()' methods for further modification (see :ref:`manipulating_submenu_items`).


.. NOTE::
    The below example only shows a subset of the arguments that are passed to methods using the 'menus_modify_raw_menu_items' hook. For a full list of the arguments supplied, see :ref:`arg_reference_tag_hooks` below.


.. code-block:: python

    from wagtail.wagtailcore import hooks

    @hooks.register('menus_modify_base_menuitem_queryset')
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
        return menu_items


The modified list of menu items will then continue to be processed as normal, being passed to `prime_menu_items` for priming, and then on to the parent page's 'modify_submenu_items()' for further modification.


.. _menus_modify_primed_menu_items:

menus_modify_primed_menu_items
------------------------------

This hook allows you to modify the list of items *just before it is passed to a template for rendering*. So, **after** 'priming' (sets 'href', 'text', 'active_class' and 'has_children_in_menu' attributes on each item), and **after** any 'modify_submenu_items()' methods have made their modifications (see :ref:`manipulating_submenu_items`).

.. NOTE::
    The below example only shows a subset of the arguments that are passed to methods using the 'menus_modify_primed_menu_items' hook. For a full list of the arguments supplied, see :ref:`arg_reference_tag_hooks` below.


.. code-block:: python

    from wagtail.wagtailcore import hooks

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
        return menu_items


.. _arg_reference_tag_hooks:

Argument reference
------------------

InIn the above examples, ``**kwargs`` is used in hook method signatures to make them *accepting* of other keyword arguments, without having to declare every single argument that should be passed in. Using this approach helps keep code tidier, and also makes it more 'future-proof', since the methods will automatically accept any new arguments that may be added by wagtailmenus in future releases.

Below is a full list of arguments passed that are passed to the above hooks, and what they mean:

``menu_items``
    The list of menu items to be modified. 

``request``
    The ``HttpRequest`` object that the menu is currently being rendered for.

``parent_page``
    If the menu being rendered is showing 'children' of a specific page, this will be the ``Page`` instance who's children pages are being displayed. The value might also be ``None`` if no parent page is involved. For example, if rendering the top level items of a main or flat menu.

``original_menu_tag``
    The name of the tag that was called to initiate rendering of the menu that is currently being rendered. For example, if you're using the ``main_menu`` tag to render a multi-level menu, even though ``sub_menu`` may be called to render subsequent additional levels, 'original_menu_tag' should retain the value ``'main_menu'``. Should be one of: ``'main_menu'``, ``'flat_menu'``, ``'section_menu'`` or ``'children_menu'``. Comparable to the ``menu_type`` values supplied to other hooks.

``menu_instance``
    The menu instance that is supplying the data required to generate the current menu. This could be an instance of a model class, like ``MainMenu`` or ``FlatMenu``, or a standard python class like ``ChildrenMenu`` or ``SectionMenu``.

``current_level``
    An integer value indicating the 'level' or 'depth' that is currently being rendered in the process of rendering a multi-level menu. This will start at `1` for the first/top-level items of a menu, and increment by `1` for each additional level.

``max_levels``
    An integer value indicatiing the maxiumum number of levels that should be rendered for the current menu. This will either have been specified by the developer using the ``max_levels`` argument of a menu tag, or might have been set in the CMS for a specific ``MainMenu`` or ``FlatMenu`` instance. 

``current_site``
    A Wagtail ``Site`` instance, indicating the site that the current request is for (usually also available as ``request.site``)

``current_page``
    A Wagtail ``Page`` instance, indicating what wagtailmenus beleives to be the page that is currently being viewed / requested by a user. This might be ``None`` if you're using standard additional views to provide functionality at urls that don't map to a ``Page`` in Wagtail.

``current_ancestor_ids``
    A list of ids of ``Page`` instances that are an 'ancestor' of ``current_page``.

``use_specific``
    An integer value indicating the preferred policy for using ``PageQuerySet.specific()`` and ``Page.specific`` in rendering the current menu. For more information see: :ref:`specific_pages`.

``allow_repeating_parents``
    A boolean value indicating the preferred policy for having pages that subclass ``MenuPageMixin`` add a repeated versions of themselves to it's children pages (when rendering a `sub_menu` for that page). For more information see: :ref:`menupage_and_menupagemixin`.

``apply_active_classes``
    A boolean value indicating the preferred policy for setting ``active_class`` attributes on menu items for the current menu.  

``use_absolute_page_urls``
    A boolean value indicating the preferred policy for using full/absolute page URLs for menu items representing pages (observed by ``prime_menu_items()`` when setting the ``href`` attribute on each menu item). In most cases this will be ``False``, as the default behaviour is to use 'relative' URLs for pages.


