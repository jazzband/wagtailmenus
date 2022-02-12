
.. _overview:

=========================
Overview and key concepts
=========================

.. contents::
    :local:
    :depth: 1


Better control over top-level menu items
========================================

When you have a 'main navigation' menu powered purely by the page tree, things can get a
little tricky, as the main menu is often designed in a way that is very sensitive to
change. Some moderators might not understand that publishing a new page at the top level
(or reordering those pages) will dramatically affect the main navigation (and possibly
even break the design). And really, *why should they?*

Wagtailmenus solves this problem by allowing you to choose exactly which pages should
appear as top-level items. It adds new functionality to Wagtail's CMS, allowing you to
simply and effectively create and manage menus, using a familiar interface.

You can also use Wagtail's built-in group permissions system to control which users
have permission to make changes to menus.


Link to pages, custom URLs, or a combination of both
====================================================

The custom URL field will not force you to enter a valid URL, so you can add things like
``#request-callback`` or ``#signup`` to link to areas on the active page (perhaps as JS
modals).

You can also define additional values to be added to a page's URL, letting you jump to a
specific anchor point on a page, or include fixed GET parameters for analytics or to
trigger custom functionality.


Multi-level menus generated from your page tree
===============================================

We firmly believe that your page tree is the best place to define the structure and
'natural order' (the ordering applied to all ``PageQuerySet`` results by default) of
pages within your site. Wagtailmenus deliberately only allows you to choose the top-level
items for each menu, because offering anything more would inevitably lead to editors
redefining parts of the page tree in multiple places, doomed to become outdated as the
original tree changes over time. When you move or reorder pages, do you really want to
have to stop and think "Where else do I need to change this?".

To generate multi-level menus, wagtailmenus takes the top-level items you selected and
dynamically generates the rest from your page tree, using the same structure and order.

.. note::
    In the CMS, Wagtail tends to list pages in order of when they were last updated.
    You can list pages in their 'natural order' (and reorder them) by following
    `these instructions from the Wagtail documentation <https://docs.wagtail.io/en/stable/editor_manual/finding_your_way_around/the_explorer_page.html#reordering-pages>`_.


Multi-level menu examples
-------------------------

Imagine your page tree had the following structure:

.. code-block:: none

    Home
    ├── What we do
    │   ├── Aiding and supporting
    │   ├── Researching
    │   └── Driving change
    ├── Latest news
    │   ├── Article one (``show_in_menus=False``)
    │   ├── Article two (``show_in_menus=False``)
    │   └── Article three (``show_in_menus=False``)
    ├── Find an outlet
    │   ├── Bristol
    │   │   └── City Centre outlet (``show_in_menus=False``)
    │   ├── Leicestershire
    │   │   ├── Hinckley outlet (``show_in_menus=False``)
    │   │   └── Leicester outlet (``show_in_menus=False``)
    │   ├── London
    │   │   ├── Camden outlet (``show_in_menus=False``)
    │   │   └── Peckham outlet (``show_in_menus=False``)
    │   └── Oxfordshire (``live=False``)
    │       └── Oxford outlet (``show_in_menus=False``)
    ├── Get involved
    │   ├── Local community groups
    │   ├── Schools and young people
    │   ├── Help as a company
    │   └── Donate
    ├── Careers
    │   ├── Vacancy one (``show_in_menus=False``)
    │   └── Vacancy two (``show_in_menus=False``)
    ├── Policies
    │   ├── Terms and conditions
    │   ├── Cookie policy
    │   └── Privacy policy
    └── Contact us

And for your menu, you selected the following pages as menu items:

- What we do (``allow_subnav=True``)
- Get involved (``allow_subnav=True``)
- Latest news (``allow_subnav=True``)
- Donate (``allow_subnav=True``)

This would generate a menu with the following structure (with ``max_levels=2``):

.. code-block:: none

    ├── What we do
    │   ├── Aiding and supporting
    │   ├── Researching
    │   └── Driving change
    ├── Get involved
    │   ├── Local community groups
    │   ├── Schools and young people
    │   ├── Help as a company
    │   └── Donate
    ├── Latest news
    └── Donate

.. note::
    Have you noticed how the article pages are not shown below the 'Latest news' item,
    despite specifying ``allow_subnav=True`` on the menu item? Only pages with a
    ``show_in_menus`` value of ``True`` will be displayed (at any level) in rendered
    menus. The field is added by Wagtail, so is present for all custom page types.

    For page types that are better suited to showing on listing/index pages (for example:
    news articles or events) -  you can set the ``show_in_menus_default`` attribute on
    the page type class to ``False`` to exclude them from menus by default.

You could also define another menu with the following pages selected as items:

- Careers (``allow_subnav=True``)
- Policies (``allow_subnav=False``)
- Find an outlet (``allow_subnav=True``)

This would generate a menu with the following structure (with ``max_levels=2``):

.. code-block:: none

    ├── Careers
    ├── Policies
    └── Find an outlet
        ├── Bristol
        ├── Leicestershire
        └── London

.. note::
    Have you noticed how 'Oxfordshire' is not shown alongside the other counties below
    'Find an outlet'? Only live/published pages will be displayed (at any level) in
    rendered menus. You can still select unpublished pages as items (in case you want
    to update your menu ahead of publishing), but wagtailmenus will automatically
    exclude unpublished pages at the time of rendering.


Define menus for all your project needs
=======================================

Have you ever hard-coded a menu into a footer at the start of a project, only for those
pages never to come into existence? Or maybe the pages were created, but their URLs
changed later on, breaking the hard-coded links? How about 'secondary navigation' menus
in headers?

As well as giving you control over your 'main menu', wagtailmenus allows you to manage
any number of additional menus via the CMS as 'flat menus', meaning they too can benefit
from page links that dynamically update to reflect tree position or status changes.

Don't hard-code another menu again! CMS-managed menus allow you to make those 'emergency
changes' and 'last-minute tweaks' without having to touch a single line of code.

.. note::
    Despite the name, 'flat menus' can be configured to render as multi-level menus if
    you need them to.


Suitable for single-site or multi-site projects
===============================================

While main menus always have to be defined for each site, for flat menus, you can support
multiple sites using any of the following approaches:

* Define a new menu for each site
* Define a menu for your default site and reuse it for the others
* Create new menus for some sites, but use the default site's menu for others

You can even use different approaches for different flat menus in the same project. If
you'd like to learn more, take a look at the ``fall_back_to_default_site_menus`` option
in :ref:`flat_menu_args`

A **copy** feature is also available from the flat menu management interface, allowing
you to quickly and easily copy existing menus from one site to another.

In a multi-site project, you can also configure wagtailmenus to use separate sets of
templates for each site for rendering (See :ref:`custom_templates_auto`)


Solves the problem of important page links becoming just 'toggles' in multi-level menus
=======================================================================================

Extend the ``wagtailmenus.models.MenuPage`` model instead of the usual
``wagtail.core.models.Page`` model to create your custom page types, and gain a
couple of extra fields that will allow you to configure certain pages to appear again
alongside their children in multi-level menus. Use the menu tags provided, and that
behaviour will remain consistent in all menus throughout your site. To find out more,
see: :ref:`menupage_and_menupagemixin`

    .. image:: _static/images/repeating-item.png
        :alt: Screenshot showing the repeated nav item in effect


Use the default menu templates for rendering, or easily add your own
====================================================================

Each menu tag comes with a default template that's designed to be fully accessible and
compatible with Bootstrap 3. However, if you don't want to use the default templates,
wagtailmenus makes it easy to use your own, using whichever approach works best for you:

-   Use settings to change the default templates used for each tag
-   Specify templates using ``template`` and ``sub_menu_template`` arguments for any of the
    included menu tags (See :ref:`custom_templates_specify`).
-   Put your templates in a preferred location within your project and wagtailmenus will
    pick them up automatically (See :ref:`custom_templates_auto`).
