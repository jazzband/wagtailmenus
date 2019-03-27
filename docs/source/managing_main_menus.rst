
.. _main_menus_cms:

===============================
Managing main menus via the CMS
===============================

1.  Log into the Wagtail CMS for your project (as a superuser).

2.  Click on **Settings** in the side menu, then select **Main menu** from the
    options that appear.

3.  You'll be automatically redirected to an edit page for the current site
    (or the 'default' site, if the current site cannot be identified). For 
    multi-site projects, a 'site switcher' will appear in the top right,
    allowing you to edit main menus for each site. 

    .. image:: _static/images/wagtailmenus-mainmenu-edit.png
        :alt: Screenshot of main menu edit page in Wagtail admin

4.  Use the **MENU ITEMS** inline panel to define the root-level items. If you
    wish, you can use the **handle** field to specify an additional value for
    each item, which you'll be able to access in a custom main menu template.

    .. NOTE:: 
        Even if selected as menu items, pages must be 'live' and have a 
        ``show_in_menus`` value of ``True`` in order to appear in menus. If
        you're expecting to see new page links in a menu, but the pages are not
        showing up, edit the page and check whether the "Show in menus"
        checkbox is checked (found under the "Promote" tab by default).

5.  Use the **SETTINGS** inline panel to define the **Maximum levels** and **Specific usage** fields,
    which you can alter to fit the needs of your project. For more information
    about specific usage see :ref:`specific_pages`.

6.  Click on the **Save** button at the bottom of the page to save your
    changes.
