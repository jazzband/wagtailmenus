
.. _overview:

=========================
Overview and key concepts
=========================

.. contents::
    :local:
    :depth: 1


Better control over top-level menu items
========================================

When you have a 'main navigation' menu powered purely by the page tree, things can get a little tricky, as they are often designed in a way that is very sensitive to change. Some moderators might not understand that publishing a new page at the top level (or reordering those pages) will dramatically affect the main navigation (and possibly even break the design). And really, *why should they?* 

Wagtailmenus solves this problem by allowing you to choose exactly which pages should appear as top-level items. It adds new functionality to Wagtail's CMS, allowing you to simply and effectively create and manage menus, using a familiar interface.

You can also use Wagtail's built-in group permissions system to control which users have permission to make changes to menus.


Link to pages, custom URLs, or a combination of both
====================================================

The custom URL field won't force you to enter a valid URL, so you can add things like ``#request-callback`` or ``#signup`` to link to areas on the active page (perhaps as JS modals).

You can also define additional values to be added to a page's URL, letting you jump to a specific anchor point on a page, or include fixed GET parameters for analytics or to trigger custom functionality.


Multi-level menus generated from your existing page tree
========================================================

We firmly beleive that your page tree is the best place to define the structure, and the 'natural order' of pages within your site. Wagtailmenus only allows you to define the top-level items for each menu, because offering anything more would inevitably lead to site managers redefining parts of the page tree in multiple places, doomed to become outdated as the original tree changes over time.

To generate multi-level menus, wagtailmenus takes the top-level items you define for each menu and automatically combines it with your page tree, efficiently identifying ancestors for each selected pages and outputting them as sub-menus following the same structure and order.

You can prevent any page from appearing menus simply by setting ``show_in_menus`` to ``False``. Pages will also no longer be included in menus if they are unpublished.


Define menus for all your project needs
=======================================

Have you ever hard-coded a menu into a footer at the start of a project, only for those pages never to come into existence? Or maybe the pages were created, but their URLs changed later on, breaking the hard-coded links? How about 'secondary navigation' menus in headers?

As well as giving you control over your 'main menu', wagtailmenus allows you to manage any number of additional menus via the CMS as 'flat menus', meaning they too can benefit from page links that dynamically update to reflect tree position or status changes. 

Don't hard-code another menu again! CMS-managed menus allow you to make those 'emergency changes' and 'last-minute tweaks' without having to touch a single line of code.

.. NOTE::
    Despite the name, 'flat menus' can be configured to render as a multi-level menus if you need them to.


Suitable for single-site or multi-site projects
===============================================

While main menus always have to be defined for each site, for flat menus, you can support multiple sites using any of the following approaches:

* Define a new menu for each site
* Define a menu for your default site and reuse it for the others
* Create new menus for some sites, but use the default site's menu for others 

You can even use different approaches for different flat menus in the same project. If you'd like to learn more, take a look at the ``fall_back_to_default_site_menus`` option in :ref:`flat_menu_args` 

A **copy** feature in also available from the flat menu management interface, allowing you to quickly and easily copy existing menus from one site to another.

In a multi-site project, you can also configure wagtailmenus to use separate sets of templates for each site for rendering (See :ref:`custom_templates_auto`)


Solves the problem of important page links becoming just 'toggles' in multi-level menus
=======================================================================================

Extend the ``wagtailmenus.models.MenuPage`` model instead of the usual ``wagtail.wagtailcore.models.Page`` model to create your custom page types, and gain a couple of extra fields that will allow you to configure certain pages to appear again alongside their children in multi-level menus. Use the menu tags provided, and that behaviour will remain consistent in all menus throughout your site. To find out more, see: :ref:`menupage_and_menupagemixin`

    .. image:: _static/images/repeating-item.png
        :alt: Screenshot showing the repeated nav item in effect


Use the default menu templates for rendering, or easily add your own
====================================================================

Each menu tag comes with a default template that's designed to be fully accessible and compatible with Bootstrap 3. However, if you don't want to use the default templates, wagtailmenus makes it easy to use your own, using whichever approach works best for you:

- Use settings to change the default templates used for each tag
- Specify templates using ``template`` and ``sub_menu_template`` arguments for any of the included menu tags (See :ref:`custom_templates_specify`).
- Put your templates in a preferred location within your project and wagtailmenus will pick them up automatically (See :ref:`custom_templates_auto`).
