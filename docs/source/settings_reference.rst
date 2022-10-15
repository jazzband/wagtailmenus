.. _settings_reference:

==================
Settings reference
==================

You can override some of wagtailmenus' default behaviour by adding one of more of the following to your project's settings.

.. contents::
    :local:
    :depth: 2


-------------------
Admin / UI settings
-------------------


.. _ADD_EDITOR_OVERRIDE_STYLES:

``WAGTAILMENUS_ADD_EDITOR_OVERRIDE_STYLES``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``True``

By default, wagtailmenus adds some additional styles to improve the readability of the forms on the menu management pages in the Wagtail admin area. If for some reason you don't want to override any styles, you can disable this behaviour by setting to ``False``.


.. _FLATMENU_MENU_ICON:

``WAGTAILMENUS_FLATMENU_MENU_ICON``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'list-ol'``

Use this to change the icon used to represent 'Flat menus' in the Wagtail CMS.


.. _FLAT_MENUS_HANDLE_CHOICES:

``WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``None``

Can be set to a tuple of choices in the `standard Django choices format
<https://docs.djangoproject.com/en/1.10/ref/models/fields/#field-choices>`_ to change the presentation of the ``FlatMenu.handle`` field from a text field, to a select field with fixed choices, when adding, editing or copying a flat menus in Wagtail's CMS.

For example, if your project uses an 'info' menu in the header, a 'footer' menu in the footer, and a 'help' menu in the sidebar, you could do the following:

.. code-block:: python

    # e.g. settings/base.py

    WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES = (
        ('info', 'Info'),
        ('help', 'Help'),
        ('footer', 'Footer'),
    )


.. _FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN:

``WAGTAILMENUS_FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``True``

By default, 'Flat menus' are editable in the Wagtail CMS. Setting this to ``False`` in your project's settings will disable this functionality, and remove the **Flat menus** item from Wagtail's **Settings** menu.


.. _FLAT_MENUS_MODELADMIN_CLASS:

``WAGTAILMENUS_FLAT_MENUS_MODELADMIN_CLASS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'wagtailmenus.modeladmin.FlatMenuAdmin'``

If you wish to override the ``ModelAdmin`` class used to represent **'Flat menus'** in the Wagtail admin area for your project (e.g. to display additional custom fields in the listing view, or change/add new views), you can do so by using this setting to swap out the default class for a custom one. e.g.

.. code-block:: python

    # e.g. settings/base.py

    WAGTAILMENUS_FLAT_MENUS_MODELADMIN_CLASS = "projectname.appname.modulename.ClassName"


The value should be an import path string, rather than a direct pointer to the class itself. wagtailmenus will lazily import the class from this path when it is required. If the path is invalid, an ``ImproperlyConfigured`` exception will be raised.


.. _MAINMENU_MENU_ICON:

``WAGTAILMENUS_MAINMENU_MENU_ICON``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'list-ol'``

Use this to change the icon used to represent 'Main menus' in the Wagtail CMS.


.. _MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN:

``WAGTAILMENUS_MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``True``

By default, 'Main menus' are editable in the Wagtail CMS. Setting this to ``False`` in your project's settings will disable this functionality, and remove the **Main menus** item from Wagtail's **Settings** menu.


.. _MAIN_MENUS_MODELADMIN_CLASS:

``WAGTAILMENUS_MAIN_MENUS_MODELADMIN_CLASS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'wagtailmenus.modeladmin.MainMenuAdmin'``

If you wish to override the ``ModelAdmin`` class used to represent **'Main menus'** in the Wagtail admin area for your project (e.g. to display additional custom fields in the listing view, or change/add new views), you can do so by using this setting to swap out the default class for a custom one. e.g.

.. code-block:: python

    # e.g. settings/base.py

    WAGTAILMENUS_MAIN_MENUS_MODELADMIN_CLASS = "projectname.appname.modulename.ClassName"

The value should be an import path string, rather than a direct pointer to the class itself. Wagtailmenus will lazily import the class from this path when it is required. If the path is invalid, and ``ImproperlyConfigured`` exception will be raised.


----------------------------------------------
Default templates and template finder settings
----------------------------------------------


.. _DEFAULT_CHILDREN_MENU_TEMPLATE:

``WAGTAILMENUS_DEFAULT_CHILDREN_MENU_TEMPLATE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'menus/children_menu.html'``

The name of the template used for rendering by the ``{% children_menu %}`` tag when no other template has been specified using the ``template`` parameter.


.. _DEFAULT_FLAT_MENU_TEMPLATE:

``WAGTAILMENUS_DEFAULT_FLAT_MENU_TEMPLATE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'menus/flat_menu.html'``

The name of the template used for rendering by the ``{% flat_menu %}`` tag when no other template has been specified using the ``template`` parameter.


.. _DEFAULT_MAIN_MENU_TEMPLATE:

``WAGTAILMENUS_DEFAULT_MAIN_MENU_TEMPLATE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'menus/main_menu.html'``

The name of the template used for rendering by the ``{% main_menu %}`` tag when no other template has been specified using the ``template`` parameter.


.. _DEFAULT_SECTION_MENU_TEMPLATE:

``WAGTAILMENUS_DEFAULT_SECTION_MENU_TEMPLATE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'menus/section_menu.html'``

The name of the template used for rendering by the ``{% section_menu %}`` tag when no other template has been specified using the ``template`` parameter.


.. _DEFAULT_SUB_MENU_TEMPLATE:

``WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'menus/sub_menu.html'``

The name of the template used for rendering by the ``{% sub_menu %}`` tag when no other template has been specified using the ``template`` parameter or using the ``sub_menu_template`` parameter on the original menu tag.


.. _SITE_SPECIFIC_TEMPLATE_DIRS:

``WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``False``

If you have a multi-site project, and want to be able to use different templates for some or all of those sites, wagtailmenus can be configured to look for additional 'site specific' paths for each template. To enable this feature, you add the following to your project's settings:

.. code-block:: python

    # e.g. settings/base.py

    WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS = True

With this set, menu tags will attempt to identify the relevant ``wagtail.core.models.Site`` instance for the current ``request``. Wagtailmenus will then look for template names with the ``domain`` value of that ``Site`` object in their path.

For more information about where wagtailmenus looks for templates, see: :ref:`custom_templates_auto`


------------------------------
Default tag behaviour settings
------------------------------


.. _FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS:

``WAGTAILMENUS_FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``False``

The default value used for ``fall_back_to_default_site_menus`` option of the ``{% flat_menu %}`` tag when a parameter value isn't provided.


.. _GUESS_TREE_POSITION_FROM_PATH:

``WAGTAILMENUS_GUESS_TREE_POSITION_FROM_PATH``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``True``

When not using wagtail's routing/serving mechanism to serve page objects, wagtailmenus can use the request path to attempt to identify a 'current' page, 'section root' page, allowing ``{% section_menu %}`` and active item highlighting to work. If this functionality is not required for your project, you can disable it by setting this value to ``False``.


.. _DEFAULT_ADD_SUB_MENUS_INLINE:

``WAGTAILMENUS_DEFAULT_ADD_SUB_MENUS_INLINE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 2.12

Default value: ``False``

For all menu types, when preparing menu items for rendering, sub menus are not added to menu items directly by default, because it's more common for developers to use the ``{% sub_menu %}`` tag in a menu templates to render additional branches of the menu. In which case, the sub menu is created by the tag.

This behaviour can be overridden on an 'individual use' basis by utilising the ``add_sub_menus_inline`` option available for each template tag. However, users wishing to change the default behaviour (so that sub menus are appended directly to menu items, without having to specify) can do so by providing a value of ``True`` in their project settings.


.. _DEFAULT_CHILDREN_MENU_MAX_LEVELS:

``WAGTAILMENUS_DEFAULT_CHILDREN_MENU_MAX_LEVELS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``1``

The maximum number of levels rendered by the ``{% children_menu %}`` tag when no value has been specified using the ``max_levels`` parameter.


.. _DEFAULT_SECTION_MENU_MAX_LEVELS:

``WAGTAILMENUS_DEFAULT_SECTION_MENU_MAX_LEVELS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``2``

The maximum number of levels rendered by the ``{% section_menu %}`` tag when no value has been specified using the ``max_levels`` parameter.


--------------------------------------
Menu class and model override settings
--------------------------------------


.. _CHILDREN_MENU_CLASS:

``WAGTAILMENUS_CHILDREN_MENU_CLASS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'wagtailmenus.models.menus.ChildrenMenu'``

Use this to specify a custom menu class to be used by wagtailmenus' ``children_menu`` tag. The value should be the import path of your custom class as a string, e.g. ``'mysite.appname.models.CustomClass'``.

For more details see: :ref:`custom_childrenmenu_class`


.. _FLAT_MENU_MODEL:

``WAGTAILMENUS_FLAT_MENU_MODEL``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'wagtailmenus.FlatMenu'``

Use this to specify a custom model to use for flat menus instead of the default. The model should be a subclass of ``wagtailmenus.AbstractFlatMenu``.

For more details see: :ref:`custom_flat_menu_models`


.. _FLAT_MENU_ITEMS_RELATED_NAME:

``WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'menu_items'``

Use this to specify the 'related name' that should be used to access menu items from flat menu instances. Used to replace the default `FlatMenuItem` model with a custom one.

For more details see: :ref:`custom_flat_menu_models`


.. _MAIN_MENU_MODEL:

``WAGTAILMENUS_MAIN_MENU_MODEL``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'wagtailmenus.MainMenu'``

Use this to specify an alternative model to use for main menus. The model should be a subclass of ``wagtailmenus.AbstractMainMenu``.

For more details see: :ref:`custom_main_menu_models`


.. _MAIN_MENU_ITEMS_RELATED_NAME:

``WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'menu_items'``

Use this to specify the 'related name' that should be used to access menu items from main menu instances. Used to replace the default ``MainMenuItem`` model with a custom one.

For more details see: :ref:`custom_main_menu_models`


.. _SECTION_MENU_CLASS:

``WAGTAILMENUS_SECTION_MENU_CLASS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'wagtailmenus.models.menus.SectionMenu'``

Use this to specify a custom class to be used by wagtailmenus' ``section_menu`` tag. The value should be the import path of your custom class as a string, e.g. ``'mysite.appname.models.CustomClass'``.

For more details see: :ref:`custom_sectionmenu_class`


----------------------
Miscellaneous settings
----------------------

.. _ACTIVE_CLASS:

``WAGTAILMENUS_ACTIVE_CLASS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'active'``

The class added to menu items for the currently active page (when using a menu template with ``apply_active_classes=True``)


.. _ACTIVE_ANCESTOR_CLASS:

``WAGTAILMENUS_ACTIVE_ANCESTOR_CLASS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'ancestor'``

The class added to any menu items for pages that are ancestors of the currently active page (when using a menu template with ``apply_active_classes=True``)


.. _DEFAULT_PAGE_FIELD_FOR_MENU_ITEM_TEXT:

``WAGTAILMENUS_PAGE_FIELD_FOR_MENU_ITEM_TEXT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``'title'``

When preparing menu items for rendering, wagtailmenus looks for a field, attribute or property method on each page with this name to set a ``text`` attribute value, which is used in menu templates as the label for each item. The ``title`` field is used by default.

.. NOTE::
    wagtailmenus will only be able to access custom page fields or methods if 'specific' pages are being used. If no attribute can be found matching the specified name, wagtailmenus will silently fall back to using the page's ``title`` field value.


.. _SECTION_ROOT_DEPTH:

``WAGTAILMENUS_SECTION_ROOT_DEPTH``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``3``

Use this to specify the 'depth' value of a project's 'section root' pages. For most Wagtail projects, this should be ``3`` (Root page depth = ``1``, Home page depth = ``2``), but it may well differ, depending on the needs of the project.


.. _CUSTOM_URL_SMART_ACTIVE_CLASSES:

``WAGTAILMENUS_CUSTOM_URL_SMART_ACTIVE_CLASSES``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default value: ``False``

By default, menu items linking to custom URLs are attributed with the 'active' class only if their ``link_url`` value matches the path of the current request _exactly_. Setting this to `True` in your project's settings will enable a smarter approach to active class attribution for custom URLs, where only the 'path' part of the ``link_url`` value is used to determine what active class should be used. The new approach will also attribute the  'ancestor'  class to menu items if the ``link_url`` looks like an ancestor of the current request URL.
