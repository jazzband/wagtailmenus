
.. _flat_menus_cms:

===============================
Managing flat menus via the CMS
===============================

The flat menu list
==================

All of the flat menus created for a project will appear in the menu list page, making it easy to find, update, copy or delete your menus later. As soon as you create menus for more than one site in a multi-site project, the listing page will give you additional information and filters to help manage your menus: 

    .. image:: _static/images/wagtailmenus-flatmenu-list.png
        :alt: Screenshot showing the FlatMenu listing page for a multi-site setup

To access the flat menu list, do the following: 

1.  Log into the Wagtail CMS for your project (as a superuser).

2.  Click on "Settings" in the side menu, then on "Flat menus".


Adding a new flat menu
======================

1.  From the listing page above, click the "Add flat menu" button
    
    .. image:: _static/images/wagtailmenus-flatmenu-add.png
        :alt: Screenshot indicating the location of the "Add flat menu" button

2.  Fill out the form, choosing a unique-for-site "handle", which you'll use
    to reference the menu when using the ``{% flat_menu %}`` tag. 

    .. image:: _static/images/wagtailmenus-flatmenu-edit.png
        :alt: Screenshot showing the FlatMenu edit interface

    .. NOTE::
        If you know in advance what menus you're likely to have in your
        project, you can define some pre-set choices for the ``handle`` field
        using the :ref:`FLAT_MENUS_HANDLE_CHOICES` setting. When used, 
        the ``handle`` field will become a select field, saving you from
        having to enter values manually.
    
3.  Use the "MENU ITEMS" inline panel to define the links you want the menu
    to have. If you wish, you can use the **handle** field to specify an
    additional value for each item, which you'll be able to access from
    within menu templates.
    
    .. NOTE:: 
        Even if selected as menu items, pages must be 'live' and have a 
        ``show_in_menus`` value of ``True`` in order to appear in menus. If
        you're expecting to see new page links in a menu, but the pages are not
        showing up, edit the page and check whether the "Show in menus"
        checkbox is checked (found under the "Promote" tab by default).

4.  At the very bottom of the form, you'll find the "ADVANCED SETTINGS"
    panel, which is collapsed by default. Click on the arrow icon next to the
    heading to reveal the **Maximum levels** and **Specific usage** fields,
    which you can alter to fit the needs of your project. For more information
    about usage specific pages in menus, see :ref:`specific_pages`

5.  Click on the **Save** button at the bottom of the page to save your
    changes.
