
.. _abstractlinkpage:

==============================
The ``AbstractLinkPage`` model
==============================

Because main and flat menus only allow editors to define the top-level items in a menu, the ``AbstractLinkPage`` model was introduced to give them a way to easily add additional links to menus, by adding additional pages to the page tree.

Just like menu items defined for a menu via the CMS, link pages can link to other pages or custom URLs, and if linking to another page, the link will automatically become hidden if the target page is unpublished, expires, or is set to no longer show in menus. It will also appear again if the target page is published or set to show in menus again.

By default, link pages are not allowed to have children pages, and shouldn't appear in wagtail-generated sitemaps or search results.


.. _implementing_abstractlinkpage:

Implementing ``AbstractLinkPage`` into your project
===================================================

Like ``MenuPage``, ``AbstractLinkPage`` is an abstract model, so in order to use it in your project, you need to subclass it.


1.   Subclass ``AbstractLinkPage`` to create a new page type model in your project:

    .. code-block:: python

        # appname/models.py

        from wagtailmenus.models import AbstractLinkPage


        class LinkPage(AbstractLinkPage):
            pass


2.   Create migtations for any models you've updated by running:
    
    .. code-block:: console

        python manage.py makemigrations appname

3.   Apply the new migrations by running:

    .. code-block:: console

        python manage.py migrate appname

