
.. _specific_pages:

==========================
'Specific' pages and menus 
==========================

For pages, Wagtail makes use of a technique in Django called 'multi-table inheritance'. In simple terms, this means that when you create an instance of a custom page type model, the data is saved in two different database tables:

* All of the standard fields from Wagtail's ``Page`` model are stored in one table
* Any data for additional fields specific to your custom model are saved in another one

Because of this, in order for Django to return 'specific' page type instance (e.g. an `EventPage`), it needs to fetch and join data from both tables; which has a negative effect on performance.

Menu generation is particularly resource intensive, because a menu needs to know a lot of data about a lot of pages. Add a need for 'specific' page instances to that mix (perhaps you need to access multilingual field values that only exist in the specific database table, or you want to use other custom field values in your menu templates), and that intensity is understandably greater, as the data will likely be spread over many tables (depending on how many custom page types you are using), needing lots of database joins to put everything together.

Because every project has different needs, wagtailmenus gives you some fine grained control over how 'specific' pages should be used in your menus. When defining a ``MainMenu`` or ``FlatMenu`` in the CMS, the **Specific page use** field allows you to choose one of the following options, which can also be passed to any of the included template tags using the ``use_specific`` parameter.


.. _specific_pages_values:

Supported values for fetching specific pages
--------------------------------------------

* **Off** (value: ``0``): Use only standard ``Page`` model data and methods, and make the minimum number of database methods when rendering. If you aren't using wagtailmenus' ``MenuPage`` model in your project, and don't need to access any custom page model fields or methods in you menu templates, and aren't overriding ``get_url_parts()`` or other ``Page`` methods concerned with URL generation, you should use this option for optimal performance.

* **Auto** (value: ``1``): Only fetch and use specific pages when needed for ``MenuPage`` operations (e.g. for 'repeating menu item' behaviour, and manipulation of sub-menu items via ``has_submenu_items()`` and ``modify_submenu_items()`` methods).

* **Top level** (value: ``2``): Only fetch and return specific page instances for the top-level menu items (pages that were manually added as menu items via the CMS), but only use vanilla ``Page`` objects for any additional levels. 

    .. NOTE::
        Although accepted by all menu tags, using `use_specific=2` will only really effect ``main_menu`` and ``flat_menu`` tags. All other tags will behave the same as if you'd supplied a value of **Auto** (``1``).
    

* **Always** (value: ``3``): Fetch and return specific page instances for ALL pages, so that custom page-type data and methods can be accessed in all menu templates. If you have a multilingual site and want to output translated page content in menus, or if you have models that override ``get_url_parts()``, ``relative_url()`` or other ``Page`` methods involved in returning URLs, this is the option you should use in order to fetch the data as efficiently as possible.


.. _specific_pages_tag_args:

Using the ``use_specific`` template tag argument 
------------------------------------------------

All of the template tags included in wagtailmenus accept a ``use_specific`` argument, allowing you to override any default settings, or the settings applied via the CMS to individual ``MainMenu`` and ``FlatMenu`` objects. As a value, you can pass in the integer value of any of the above options, for example: 

.. code-block:: html

    ...
    {% main_menu use_specific=2 %} 
    ...
    {% section_menu use_specific=3 %}
    ...
    {% children_menu use_specific=1 %}

Or, the following variables should be available in the context for you to use instead: 

* ``USE_SPECIFIC_OFF`` (value: ``0``)
* ``USE_SPECIFIC_AUTO`` (value ``1``)
* ``USE_SPECIFIC_TOP_LEVEL`` (value ``2``)
* ``USE_SPECIFIC_ALWAYS`` (value ``3``) 

For example:

.. code-block:: html

    ...
    {% main_menu use_specific=USE_SPECIFIC_TOP_LEVEL %} 
    ...
    {% section_menu use_specific=USE_SPECIFIC_ALWAYS %}
    ...
    {% children_menu use_specific=USE_SPECIFIC_AUTO %}
