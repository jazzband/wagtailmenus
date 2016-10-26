|Build Status| |PyPi Version| |Coverage Status|

What is wagtailmenus?
=====================

It's an extension for Torchbox's `Wagtail CMS <https://github.com/torchbox/wagtail>`_ to help you manage and
render multi-level navigation and simple flat menus in a consistent, flexible way.

The current version is compatible with Wagtail >= 1.5, and Python 2.7,
3.3, 3.4 and 3.5.

What does wagtailmenus do?
--------------------------

1. Gives you independent control over your root-level main menu items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :code:`wagtailmenus.models.MainMenu` model lets you define the root-level items for your
projects's main navigation (or one for each site, if it's a multi-site
project) using an inline model :code:`wagtailmenus.models.MainMenuItem`. These items can link to
pages (you can append an optional hash or querystring to the URL, too)
or custom URLs. The custom URL field won't force you to enter a valid
URL either, so you can add things like *#request-callback* or *#signup*
to link to areas on the active page (perhaps as JS modals).

The site's page tree powers everything past the root level, so you don't
have to recreate it elsewhere. And as you'd expect, only links to
published pages will appear when rendering.

2. Allows you to manage multiple 'flat menus' via the CMS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Have you ever hard-coded a menu into a footer at the start of a project,
only for those pages never to come into existence? Or maybe the pages
were created, but their URLs changed later on, breaking the hard-coded
links? How about 'secondary navigation' menus in headers? Flat menus
allow you to manage these kind of menus via the CMS, instead of
hard-coding them. This means that the page URLs dynamically update to
reflect changes, and making updates is possible without having to touch
a single line of code.

Flat menus are designed for outputting simple, flat lists of links, but
they CAN be made to display multiple levels of pages too. See the
instructions below for `using the **{% flat_menu %}** tag <#flat_menu-tag>`_.

In a multi-site project, you can choose to define a new set of menus for
each site, or you can define one set of menus for your default site and
reuse them for your other sites, or use a combination of both approaches
for different menus (see the **fall_back_to_default_site_menus**
option in `**Using the **{% flat_menu %} tag** <#flat_menu-tag>`_ to
find out more). However you choose to do things, a 'copy' feature makes
it easy to copy existing flat menus from one site to another via
Wagtail's admin interface.

3. Offers a solution to the issue of key page links becoming 'toggles' in multi-level drop-down menus
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extend the :code:`wagtailmenus.models.MenuPage` model instead of the usual
:code:`wagtail.wagtailcore.models.Page` to create your custom page types,
and gain a couple of extra fields that will allow you to configure
certain pages to appear again alongside their children in multi-level
menus. Use the menu tags provided, and that behaviour will remain
consistent in all menus throughout your site.

No more adding additional pages into the tree. No more hard-coding
additional links into templates, or resorting to javascript hacks.

4. Gives you a set of powerful template tags to render your menus consistently
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each tag comes with a default template that's designed to be fully
accessible and compatible with Bootstrap 3. Limiting any project to a
set of pre-defined templates would be silly though, which is why every
template tag allows you to render menus using a template of your
choosing. You can also override the templates in the same way as any
other Django project... by putting templates of the same name into a
preferred location.

Installation instructions
-------------------------

#. Install the package using pip:

   .. code:: bash

    $ pip install wagtailmenus

#. Add :code:`wagtail.contrib.modeladmin` to :code:`INSTALLED_APPS` in your
   project settings, if it's not there already.
#. Add :code:`wagtailmenus` to `INSTALLED_APPS` in your project settings.
#. Add :code:`wagtailmenus.context_processors.wagtailmenus` to the
   :code:`context_processors` list in your :code:`TEMPLATES` setting. The
   setting should look something like this:

   .. code:: python

    TEMPLATES = [
    {
          'BACKEND': 'django.template.backends.django.DjangoTemplates',
          'DIRS': [ os.path.join(PROJECT_ROOT, 'templates'), ],
          'APP_DIRS': True,
          'OPTIONS': {
              'context\_processors': [
                  'django.contrib.auth.context_processors.auth',
                  'django.template.context_processors.debug',
                  'django.template.context_processors.i18n',
                  'django.template.context_processors.media',
                  'django.template.context_processors.request',
                  'django.template.context_processors.static',
                  'django.template.context_processors.tz',
                  'django.contrib.messages.context_processors.messages',
                  'wagtail.contrib.settings.context_processors.settings',
                  'wagtail.contrib.settings.context_processors.settings',
                  'wagtailmenus.context_processors.wagtailmenus',
              ],
          },
    }, ]

#. Install migrations to set up the initial database tables:

   .. code:: bash

    $ python manage.py migrate wagtailmenus


Additional steps for `MenuPage` usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   It is not necessary to extend :code:`wagtailmenus.models.MenuPage` for all custom page
   types; Just ones you know will be used for pages that may have children,
   and will need the option to repeat themselves in sub-menus when listing
   those children.

#. In your **core** app and other apps (wherever you have defined a
   custom page/content model to use in your project), import
   :code:`wagtailmenus.models.MenuPage` and extend that instead of
   :code:`wagtail.wagtailcore.models.Page`.
#. Run :code:`python manage.py makemigrations` to create migrations for the
   apps you've updated.
#. Run :code:`python manage.py migrate` to add apply those migrations.

How to use wagtailmenus in your project
---------------------------------------

**Skip to a section:**

#. `Defining root-level main menu items in the CMS <#defining-main-menu-items>`_
#. `Using the {% main_menu %} tag <#main_menu-tag>`_
#. `Defining flat menus in the CMS <#defining-flat-menus>`_
#. `Using the {% flat_menu %} tag <#flat_menu-tag>`_
#. `Using the {% section_menu %} tag <#section_menu-tag>`_
#. `Using the {% children_menu %} tag <#children_menu-tag>`_
#. `Using the {% sub_menu %} tag <#sub_menu-tag>`_
#. `Writing your own menu templates <#writing-menu-templates>`_
#. `Optional repetition of selected pages in menus using MenuPage <#using-menupage>`_
#. `Adding additional menu items for specific page types <#modifying-submenu-items>`_
#. `Overriding default behaviour with settings <#app-settings>`_

1. Defining root-level main menu items in the CMS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Log into the Wagtail CMS for your project (as a superuser).
#. Click on **Settings** in the side menu to access the options in
   there, then select **Main menu**.
#. You'll be automatically redirected to the an edit page for the
   current site (or the 'default' site, if the current site cannot be
   identified). For multi-site projects, a 'site switcher' will appear
   in the top right, allowing you to edit main menus for each site.
#. Use the **MENU ITEMS** inline panel to define the root-level items.
   If you wish, you can use the :code:`handle` field to specify an
   If you wish, you can use the :code:`handle` field to specify an
   additional value for each item, which you'll be able to access in a
   custom main menu template.

    .. note::

       Pages need to be published, and
       have the :code:`show_in_menus` checkbox checked in order to appear in
       menus (look under the **Promote** tab when editing pages).

#. Save your changes to apply them to your site.

2. Defining flat menus in the CMS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Log into the Wagtail CMS for your project (as a superuser).
#. Click on **Settings** in the side menu to access the options in
   there, then select **Flat menus** to access the menu list page.
#. Click the button at the top of the page to add a flat menu for your
   site (or one for each of your sites if you are running a multi-site
   setup).
#. Fill out the form, choosing a 'unique for site' **handle** to
   reference in your templates.
#. Use the **MENU ITEMS** inline panel to define the links you want the
   menu to have. If you wish, you can use the `handle` field to
   specify an additional value for each item, which you'll be able to
   access in a custom flat menu template.

   .. note::

      Pages need to be published and have the :code:`show_in_menus` checkbox checked in order to
      appear in menus (look under the **Promote** tab when editing pages).

#. Save your changes to apply them to your site.

All of the flat menus created for a project will appear in the menu list
All of the flat menus created for a project will appear in the menu list
page (from step 2, above) making it easy to find, update, copy or delete
your menus later. As soon as you create menus for more than one site in
a multi-site project, the listing page will give you additional
information and filters to help manage your menus, like so:

3. Using the `{% main_menu %}` tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :code:`{% main_menu %}` tag allows you to display the :code:`MainMenu`
defined for the current site in your Wagtail project, with CSS classes
automatically applied to each item to indicate the current page or
ancestors of the current page. It also does a few sensible things, like
never adding the 'ancestor' class for a homepage link, or outputting
children for it.

#. In whichever template you want your main menu to appear, load
   :code:`menu_tags` using :code:`{% load menu_tags %}`.
#. Add :code:`{% main_menu %}` to your template, where you want the menu to
   appear.

**Optional params for `{% main_menu %}`**

-  **max_levels** (default: `2`): Provide an integer value to
   control how many levels of pages should be rendered. If you only want
   to display the root-level menu items defined as inlines in the CMS
   (whether the selected pages have children or not), add
   :code:`max_levels=1` to the tag in your template. You can display
   additional levels by providing a higher value. You can also override
   the default value by adding a
   :code:`WAGTAILMENUS_DEFAULT_MAIN_MENU_MAX_LEVELS` setting to your
   project's settings module.
-  **show_multiple_levels** (default: :code:`True`): Adding
   :code:`show_multiple_levels=False` to the tag in your template
   essentially overrides :code:`max_levels` to **1**. It's just a little
   more descriptive.
-  **allow_repeating_parents** (default: :code:`True`):
   Repetition-related settings on your pages are respected by default,
   but you can add `allow_repeating_parents=False` to ignore them, and
   not repeat any pages in sub-menus when rendering multiple levels.
-  **apply_active_classes** (default: :code:`True`): The tag will
   attempt to add 'active' and 'ancestor' CSS classes to the menu items
   (where applicable) to indicate the active page and ancestors of that
   page. To disable this behaviour, add `apply_active_classes=False`
   to the tag in your template. You can change the CSS classes used by
   adding :code:`WAGTAILMENUS_ACTIVE_CLASS` and
   :code:`WAGTAILMENUS_ACTIVE_ANCESTOR_CLASS` settings to your project's
   settings module.
-  **template** (default: `'menus/main_menu.html'`): Lets you
   render the menu to a template of your choosing. You can also name an
   alternative template to be used by default, by adding a
   :code:`WAGTAILMENUS_DEFAULT_MAIN_MENU_TEMPLATE` setting to your project's
   settings module.
-  **sub_menu_template** (default: `'menus/sub_menu.html'`): Lets
   you specify a template to be used for rendering sub menus. All
   subsequent calls to :code:`{% sub_menu %}` within the context of the
   section menu will use this template unless overridden by providing a
   `template` value to :code:`{% sub_menu %}` in a menu template. You can
   specify an alternative default template by adding a
   :code:`WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE` setting to your project's
   settings module.
-  **use_specific** (default: :code:`False`): If :code:`True`, specific
   page-type objects will be fetched and used for menu items instead of
   vanilla :code:`Page` objects, using as few database queries as possible.
   The default can be altered by adding
   :code:`WAGTAILMENUS_DEFAULT_SECTION_MENU_USE_SPECIFIC=True` to your
   project's settings module.

4. Using the `{% flat_menu %}` tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. In whichever template you want your menu to appear, load
   :code:`menu_tags` using `{% load menu_tags %}`.
#. Add :code:`{% flat_menu 'menu-handle' %}` to your template, where you
   want the menu to appear (where 'menu-handle' is the unique handle for
   the menu you added).

**Optional params for `{% flat_menu %}`**

-  **show_menu_heading** (default: `True`): Passed through to the
   template used for rendering, where it can be used to conditionally
   display a heading above the menu.
-  **show_multiple_levels** (default: `False`): Flat menus are
   designed for outputting simple, flat lists of links. But, if the need
   arises, you can add `show_multiple_levels=True` to the tag in your
   template to output multiple page levels. If you haven't already, you
   may also need to check the **"Allow sub-menu for this item"** box for
   the menu items you wish to show further levels for.
-  **max_levels** (default: `2`): If `show_multiple_levels=True`
   is being provided to enable multiple levels, you can use this
   parameter to specify how many levels you'd like to display.
-  **apply_active_classes** (default: `False`): Unlike
   `main_menu` and `section_menu`, `flat_menu` will NOT attempt to
   add 'active' and 'ancestor' classes to the menu items by default, as
   this is often not useful. You can override this by adding
   `apply_active_classes=true` to the tag in your template.
-  **template** (default: `'menus/flat_menu.html'`): Lets you
   render the menu to a template of your choosing. You can also name an
   alternative template to be used by default, by adding a
   :code:`WAGTAILMENUS_DEFAULT_FLAT_MENU_TEMPLATE` setting to your project's
   settings module.
-  **sub_menu_template** (default: `'menus/sub_menu.html'`): Lets
   you specify a template to be used for rendering sub menus (if enabled
   using :code:`show_multiple_levels`). All subsequent calls to
   {% sub_menu %} within the context of the flat menu will use this
   template unless overridden by providing a `template` value to
   {% sub_menu %} in a menu template. You can specify an alternative
   default template by adding a
   `WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE` setting to your project's
   settings module.
-  **fall_back_to_default_site_menus** (default: `False`): When
   using the `{% flat_menu %}` tag, wagtailmenus identifies the
   'current site', and attempts to find a menu for that site, matching
   the `handle` provided. By default, if no menu is found for the
   current site, nothing is rendered. However, if
   `fall_back_to_default_site_menus=True` is provided, wagtailmenus
   will search search the 'default' site (In the CMS, this will be the
   site with the '**Is default site**' checkbox ticked) for a menu with
   the same handle, and use that instead before giving up. The default
   behaviour can be altered by adding
   `WAGTAILMENUS_FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS=True` to
   your project's settings module.
-  **use_specific** (default: `False`): If `True`, specific
   page-type objects will be fetched and used for menu items instead of
   vanilla `Page` objects, using as few database queries as possible.
   The default can be altered by adding
   `WAGTAILMENUS_DEFAULT_FLAT_MENU_USE_SPECIFIC=True` to your
   project's settings module.

5. Using the `{% section_menu %}` tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `{% section_menu %}` tag allows you to display a context-aware,
page-driven menu in your project's templates, with CSS classes
automatically applied to each item to indicate the active page or
ancestors of the active page.

#. In whichever template you want the section menu to appear, load
   `menu_tags` using `{% load menu_tags %}`.
#. Add `{% section_menu %}` to your template, where you want the menu
   to appear.

**Optional params for `{% section_menu %}`**

-  **show_section_root** (default: `True`): Passed through to the
   template used for rendering, where it can be used to conditionally
   display the root page of the current section.
-  **max_levels** (default: `2`): Lets you control how many levels
   of pages should be rendered (the section root page does not count as
   a level, just the first set of pages below it). If you only want to
   display the first level of pages below the section root page (whether
   pages linked to have children or not), add `max_levels=1` to the
   tag in your template. You can display additional levels by providing
   a higher value.
-  **show_multiple_levels** (default: `True`): Adding
   `show_multiple_levels=False` to the tag in your template
   essentially overrides `max_levels` to `1`. It's just a little
   more descriptive.
-  **allow_repeating_parents** (default: `True`):
   Repetition-related settings on your pages are respected by default,
   but you can add `allow_repeating_parents=False` to ignore them, and
   not repeat any pages in sub-menus when rendering.
-  **apply_active_classes** (default: `True`): The tag will add
   'active' and 'ancestor' classes to the menu items where applicable,
   to indicate the active page and ancestors of that page. To disable
   this behaviour, add `apply_active_classes=False` to the tag in your
   template.
-  **template** (default: `'menus/section_menu.html'`): Lets you
   render the menu to a template of your choosing. You can also name an
   alternative template to be used by default, by adding a
   `WAGTAILMENUS_DEFAULT_SECTION_MENU_TEMPLATE` setting to your
   project's settings module.
-  **sub_menu_template** (default: :code:`'menus/sub_menu.html'`): Lets
   you specify a template to be used for rendering sub menus. All
   subsequent calls to :code:`{% sub_menu %}` within the context of the
   section menu will use this template unless overridden by providing a
   :code:`template` value to :code:`{% sub_menu %}` in a menu template. You can
   specify an alternative default template by adding a
   :code:`WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE` setting to your project's
   settings module.
-  **use_specific** (default: :code:`False`): If :code:`True`, specific
   page-type objects will be fetched and used for menu items instead of
   vanilla :code:`Page` objects, using as few database queries as possible.
   The default can be altered by adding
   :code:`WAGTAILMENUS_DEFAULT_SECTION_MENU_USE_SPECIFIC=True` to your
   project's settings module.

6. Using the `{% children_menu %}` tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :code:`{% children_menu %}` tag can be used in page templates to display
a menu of children of the current page. You can also use the
:code:`parent_page` argument to show children of a different page.

#. In whichever template you want the menu to appear, load `menu_tags`
   using :code:`{% load menu_tags %}`.
#. Use the :code:`{% children_menu %}` tag where you want the menu to
   appear.

**Optional params for `{% children_menu %}`**

-  **parent_page**: The tag will automatically pick up :code:`self` from
   the context to render the children for the active page, but you
   render a children menu for a different page, if desired. To do so,
   add :code:`parent_page=page_obj` to the tag in your template, where
   :code:`page_obj` is the :code:`Page` instance you wish to display children
   for.
-  **max_levels** (default: `1`): Lets you control how many levels
   of pages should be rendered. For example, if you want to display the
   direct children pages and their children too, add :code:`max_levels=2` to
   the tag in your template.
-  **allow_repeating_parents** (default: :code:`True`):
   Repetition-related settings on your pages are respected by default,
   but you can add :code:`allow_repeating_parents=False` to ignore them, and
   not repeat any pages in sub-menus when rendering.
-  **apply_active_classes** (default: :code:`False`): Unlike
   :code:`main_menu` and :code:`section_menu`, :code:`children_menu` will NOT
   attempt to add 'active' and 'ancestor' classes to the menu items by
   default, as this is often not useful. You can override this by adding
   :code:`apply_active_classes=true` to the tag in your template.
-  **template** (default: :code:`'menus/children_menu.html'`): Lets you
   render the menu to a template of your choosing. You can also name an
   alternative template to be used by default, by adding a
   :code:`WAGTAILMENUS_DEFAULT_CHILDREN_MENU_TEMPLATE` setting to your
   project's settings module.
-  **sub_menu_template** (default: :code:`'menus/sub_menu.html'`): Lets
   you specify a template to be used for rendering sub menus. All
   subsequent calls to :code:`{% sub_menu %}` within the context of the
   section menu will use this template unless overridden by providing a
   :code:`template` value to :code:`{% sub_menu %}` in a menu template. You can
   specify an alternative default template by adding a
   :code:`WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE` setting to your project's
   settings module.
-  **use_specific** (default: :code:`False`): If :code:`True`, specific
   page-type objects will be fetched and used for menu items instead of
   vanilla :code:`Page` objects, using as few database queries as possible.
   The default can be altered by adding
   :code:`WAGTAILMENUS_DEFAULT_CHILDREN_MENU_USE_SPECIFIC=True` to your
   project's settings module.

6. Using the `{% sub_menu %}` tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :code:`{% sub_menu %}` tag is used within menu templates to render
additional levels of pages within a menu. It's designed to pick up on
variables added to the context by the other menu tags, and so can behave
a little unpredictably if called directly, without those context
variables having been set. It requires only one parameter to work, which
is :code:`menuitem_or_page`, which can either be an instance of
:code:`MainMenuItem`, :code:`FlatMenuItem`, or `Page`.

**Optional params for `{% sub_menu %}`**

-  **stop_at_this_level**: By default, the tag will figure out
   whether further levels should be rendered or not, depending on what
   you supplied as :code:`max_levels` to the original menu tag. However, you
   can override that behaviour by adding either
   :code:`stop_at_this_level=True` or :code:`stop_at_this_level=False` to the
   tag in your custom menu template.
-  **allow_repeating_parents**: By default, the tag will inherit
   this behaviour from whatever was specified for the original menu tag.
   However, you can override that behaviour by adding either
   :code:`allow_repeating_parents=True` or :code:`allow_repeating_parents=False`
   to the tag in your custom menu template.
-  **apply_active_classes**: By default, the tag will inherit this
   behaviour from whatever was specified for the original menu tag.
   However, you can override that behaviour by adding either
   :code:`apply_active_classes=True` or :code:`apply_active_classes=False` to
   the tag in your custom menu template.
-  **template** (default: :code:`'menus/sub_menu.html'`): Lets you
   render the menu to a template of your choosing. You can also name an
   alternative template to be used by default, by adding a
   :code:`WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE` setting to your project's
   settings module.
-  **use_specific**: By default, the tag will inherit this behaviour
   from whatever was specified for the original menu tag. However, the
   value can be overridden by adding :code:`use_specific=True` or
   :code:`use_specific=False` to the :code:`{% sub_menu %}` tag in your custom menu
   template.

8. Writing your own menu templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following variables are added to the context by all of the above
tags, which you can make use of in your templates:

-  **menu_items**: A list of :code:`MenuItem` or :code:`Page` objects with
   additional attributes added to help render menu items for the current
   level.
-  **current_level**: The current level being rendered. This starts
   at `1` for the initial template tag call, then increments each time
   :code:`sub_menu` is called recursively in rendering that same menu.
-  **current_template**: The name of the template currently being
   used for rendering. This is most useful when rendering a :code:`sub_menu`
   template that calls :code:`sub_menu` recursively, and you wish to use the
   same template for all recursions.
-  **max_levels**: The maximum number of levels that should be
   rendered, as determined by the original :code:`main_menu`,
   :code:`section_menu`, :code:`flat_menu` or :code:`children_menu` tag call.
-  **allow_repeating_parents**: A boolean indicating whether
   :code:`MenuPage` fields should be respected when rendering further menu
   levels.
-  **apply_active_classes**: A boolean indicating whether
   :code:`sub_menu` tags should attempt to add 'active' and 'ancestor'
   classes to menu items when rendering further menu levels.

**Each item in `menu_items` has the following attributes:**

-  **href**: The URL that the menu item should link to
-  **text**: The text that should be used for the menu item
-  **active_class**: A class name to indicate the 'active' state of
   the menu item. The value will be 'active' if linking to the current
   page, or 'ancestor' if linking to one of it's ancestors.
-  **has_children_in_menu**: A boolean indicating whether the menu
   item has children that should be output as a sub-menu.

9. Optional repetition of selected pages in menus using `MenuPage`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's say you have an **About Us** section on your site. The top-level
page has content that is just as important as that on the pages below it
(e.g. "Meet the team", "Our mission and values", "Staff vacancies").
Because of this, you'd like visitors to be able to access the root page
as easily as those pages. But, your site uses drop-down navigation, and
the **About Us** link no longer takes you to that page when clicked...
it simply acts as a toggle for hiding and showing it's sub-pages:

Presuming the **About Us** page extends
`wagtailmenus.models.MenuPage`:

#. Edit that page in the CMS, and click on the :code:`Settings` tab.
#. Uncollapse the **ADVANCED MENU BEHAVIOUR** panel by clicking the
   downward-pointing arrow next to the panel's label.
#. Tick the **Repeat in sub-navigation** checkbox that appears, and
   publish your changes.

Now, wherever the children of the **About Us** page are output (using
one of the above menu tags), an additional link will appear alongside
them, allowing the that page to be accessed more easily. In the example
above, you'll see *"Section overview"* has been added to the a
**Repeated item link text** field. With this set, the link text for the
repeated item should read *"Section overview"*, instead of just
repeating the page's title, like so:

The menu tags do some extra work to make sure both links are never
assigned the :code:`'active'` class. When on the 'About Us' page, the tags
will treat the repeated item as the 'active' page, and just assign the
:code:`'ancestor'` class to the original, so that the behaviour/styling is
consistent with other page links rendered at that level.

10. Adding additional menu items for specific page types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you find yourself needing further control over the items that appear
in your menus (perhaps you need to add further items for specific pages,
or remove some under certain circumstances), you will likely find the
**modify_submenu_items()** *(added in 1.3)* and **has_submenu_items()** *(added in 1.4)* methods on the
`MenuPage <https://github.com/rkhleics/wagtailmenus/blob/master/wagtailmenus/models.py#L17>`_
model of interest.

For example, if you had a :code:`ContactPage` model extended :code:`MenuPage`,
and in main menus, you wanted to add some additional links below each
:code:`ContactPage` - You could achieve that by overriding the
:code:`modify_submenu_items()` and :code:`has_submenu_items()` methods like so:

.. code:: python

    from wagtailmenus.models import MenuPage

    class ContactPage(MenuPage):
        ...

        def modify_submenu_items(self, menu_items, current_page,
                                 current_ancestor_ids, current_site,
                                 allow_repeating_parents, apply_active_classes,
                                 original_menu_tag):
            # Apply default modifications first of all
            menu_items = super(ContactPage, self).modify_submenu_items(
                menu_items, current_page, current_ancestor_ids, current_site,
                allow_repeating_parents, apply_active_classes, original_menu_tag)
            """
            If rendering a 'main_menu', add some additional menu items to the end
            of the list that link to various anchored sections on the same page
            """
            if original_menu_tag == 'main_menu':
                base_url = self.relative_url(current_site)
                """
                Additional menu items can be objects with the necessary attributes,
                or simple dictionaries. `href` is used for the link URL, and `text`
                is the text displayed for each link. Below, I've also used
                `active_class` to add some additional CSS classes to these items,
                so that I can target them with additional CSS
                """
                menu_items.extend((
                    {
                        'text': 'Get support',
                        'href': base_url + '#support',
                        'active_class': 'support',
                    },
                    {
                        'text': 'Speak to someone',
                        'href': base_url + '#call',
                        'active_class': 'call',
                    },
                    {
                        'text': 'Map & directions',
                        'href': base_url + '#map',
                        'active_class': 'map',
                    },
                ))
            return menu_items

        def has_submenu_items(self, current_page, check_for_children,
                              allow_repeating_parents, original_menu_tag):
            """
            Because `modify_submenu_items` is being used to add additional menu
            items, we need to indicate in menu templates that `ContactPage` objects
            do have submenu items in main menus, even if they don't have children
            pages.
            """
            if original_menu_tag == 'main_menu':
                return True
            return super(ContactPage, self).has_submenu_items(
                current_page, check_for_children, allow_repeating_parents,
                original_menu_tag)

These change would result in the following HTML output when rendering a
:code:`ContactPage` instance in a main menu:

.. code:: html

        <li class=" dropdown">
            <a href="/contact-us/" class="dropdown-toggle" id="ddtoggle_18" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Contact us <span class="caret"></span></a>
            <ul class="dropdown-menu" aria-labelledby="ddtoggle_18">
                <li class="support"><a href="/contact-us/#support">Get support</a></li>
                <li class="call"><a href="/contact-us/#call">Speak to someone</a></li>
                <li class="map"><a href="/contact-us/#map">Map &amp; directions</a></li>
            </ul>
        </li>

You can also modify sub-menu items based on field values for specific
instances, rather than doing the same for every page of the same type.
Here's another example:

.. code:: python


    from django.db import models
    from wagtailmenus.models import MenuPage

    class SectionRootPage(MenuPage):
        add_submenu_item_for_news = models.BooleanField(default=False)

        def modify_submenu_items(
            self, menu_items, current_page, current_ancestor_ids, current_site,
            allow_repeating_parents, apply_active_classes, original_menu_tag=''
        ):
            menu_items = super(SectionRootPage,self).modify_menu_items(
                menu_items, current_page, current_ancestor_ids, current_site,
                allow_repeating_parents, apply_active_classes, original_menu_tag
            )
            if self.add_submenu_item_for_news:
                menu_items.append({
                    'href': '/news/',
                    'text': 'Read the news',
                    'active_class': 'news-link',
                })
            return menu_items

        def has_submenu_items(self, current_page, check_for_children,
                              allow_repeating_parents, original_menu_tag):

            if self.add_submenu_item_for_news:
                return True
            return super(SectionRootPage, self).has_submenu_items(
                current_page, check_for_children, allow_repeating_parents,
                original_menu_tag)

11. Changing the default settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can override some of wagtailmenus' default behaviour by adding one
of more of the following to your project's settings:

-  **WAGTAILMENUS_ACTIVE_CLASS** (default: :code:`'active'`):
   The class added to menu items for the currently active page (when using a menu
   template with :code:`apply_active_classes=True`)
-  **WAGTAILMENUS_ACTIVE_ANCESTOR_CLASS** (default: :code:`'ancestor'`):
   The class added to any menu items for pages that are ancestors of the
   currently active page (when using a menu template with
   :code:`apply_active_classes=True`)
-  **WAGTAILMENUS_MAINMENU_MENU_ICON** (default: :code:`'list-ol'`): Use
   this to change the icon used to represent :code:`MainMenu` in the Wagtail
   admin area.
-  **WAGTAILMENUS_FLATMENU_MENU_ICON** (default: :code:`'list-ol'`): Use
   this to change the icon used to represent :code:`FlatMenu` in the Wagtail
   admin area.
-  **WAGTAILMENUS_SECTION_ROOT_DEPTH** (default: :code:`3`):
   Use this to specify the 'depth' value of a project's 'section root' pages. For
   most Wagtail projects, this should be :code:`3` (Root page = 1, Home page
   = 2), but it may well differ, depending on the needs of the project.
-  **WAGTAILMENUS_GUESS_TREE_POSITION_FROM_PATH** (default: :code:`True`):
   When not using wagtail's routing/serving mechanism to
   serve page objects, wagtailmenus can use the request path to attempt
   to identify a 'current' page, 'section root' page, allowing
   :code:`{% section_menu %}` and active item highlighting to work. If this
   functionality is not required for your project, you can disable it by
   setting this value to :code:`False`.
-  **WAGTAILMENUS_FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS** (default: :code:`False`):
   The default value used for :code:`fall_back_to_default_site_menus` option of the :code:`{% flat_menu %}`
   tag when a parameter value isn't provided.
-  **WAGTAILMENUS_DEFAULT_MAIN_MENU_TEMPLATE** (default: :code:`'menus/main_menu.html'`):
   The name of the template used for
   rendering by the :code:`{% main_menu %}` tag when a :code:`template`
   parameter value isn't provided.
-  **WAGTAILMENUS_DEFAULT_FLAT_MENU_TEMPLATE** (default: :code:`'menus/flat_menu.html'`):
   The name of the template used for
   rendering by the :code:`{% flat_menu %}` tag when a :code:`template`
   parameter value isn't provided.
-  **WAGTAILMENUS_DEFAULT_SECTION_MENU_TEMPLATE** (default: :code:`'menus/section_menu.html'`):
   The name of the template used for
   rendering by the :code:`{% section_menu %}` tag when a :code:`template`
   parameter value isn't provided.
-  **WAGTAILMENUS_DEFAULT_CHILDREN_MENU_TEMPLATE** (default: :code:`'menus/children_menu.html'`):
   The name of the template used for
   rendering by the :code:`{% children_menu %}` tag when a `template`
   parameter value isn't provided.
-  **WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE** (default: :code:`'menus/sub_menu.html'`):
   The name of the template used for
   rendering by the :code:`{% sub_menu %}` tag when a `template` parameter
   value isn't provided.
-  **WAGTAILMENUS_DEFAULT_MAIN_MENU_MAX_LEVELS** (default: :code:`2`):
   The default number of maximum levels rendered by :code:`{% main_menu %}`
   when a :code:`max_levels` parameter value isn't provided.
-  **WAGTAILMENUS_DEFAULT_FLAT_MENU_MAX_LEVELS** (default: :code:`2`):
   The default number of maximum levels rendered by :code:`{% flat_menu %}`
   when :code:`show_multiple_levels=True` and a :code:`max_levels` parameter
   value isn't provided.
-  **WAGTAILMENUS_DEFAULT_SECTION_MENU_MAX_LEVELS** (default: :code:`2`):
   The default number of maximum levels rendered by
   :code:`{% section_menu %}` when a `max_levels` parameter value isn't
   provided.
-  **WAGTAILMENUS_DEFAULT_CHILDREN_MENU_MAX_LEVELS** (default: `1`):
   The default number of maximum levels rendered by
   :code:`{% children_page_menu %}` when a :code:`max_levels` parameter value
   isn't provided.
-  **WAGTAILMENUS_DEFAULT_MAIN_MENU_USE_SPECIFIC** (default: :code:`False`):
   If set to `True`, by default, when rendering a
   :code:`{% main_menu %}`, specific page-type objects will be fetched and
   used for menu items instead of vanilla :code:`Page` objects, using as few
   database queries as possible. The behaviour can be overridden in
   individual cases using the tag's :code:`use_specific` keyword argument.
-  **WAGTAILMENUS_DEFAULT_SECTION_MENU_USE_SPECIFIC** (default: `False`):
   If set to :code:`True`, by default, when rendering a :code:`{% section_menu %}`,
   specific page-type objects will be fetched
   and used for menu items instead of vanilla :code:`Page` objects, using as
   few database queries as possible. The behaviour can be overridden in
   individual cases using the tag's :code:`use_specific` keyword argument.
-  **WAGTAILMENUS_DEFAULT_CHILDREN_USE_SPECIFIC** (default: :code:`False`):
   If set to :code:`True`, by default, when rendering a
   :code:`{% children_menu %}`, specific page-type objects will be fetched
   and used for menu items instead of vanilla :code:`Page` objects, using as
   few database queries as possible. The behaviour can be overridden in
   individual cases using the tag's :code:`use_specific` keyword argument.
-  **WAGTAILMENUS_DEFAULT_FLAT_MENU_USE_SPECIFIC** (default: :code:`False`):
   If set to :code:`True`, by default, when rendering a
   :code:`{% flat_menu %}`, specific page-type objects will be fetched and
   used for menu items instead of vanilla :code:`Page` objects, using as few
   database queries as possible. The behaviour can be overridden in
   individual cases using the tag's :code:`use_specific` keyword argument.

Contributing
------------

If you'd like to become a wagtailmenus contributor, we'd be happy to
have you. You should start by taking a look at our `contributor
guidelines <https://github.com/rkhleics/wagtailmenus/blob/master/CONTRIBUTING.md>`_

.. |Build Status| image:: https://travis-ci.org/rkhleics/wagtailmenus.svg?branch=master
   :target: https://travis-ci.org/rkhleics/wagtailmenus
.. |PyPi Version| image:: https://img.shields.io/pypi/v/wagtailmenus.svg
   :target: https://pypi.python.org/pypi/wagtailmenus
.. |Coverage Status| image:: https://coveralls.io/repos/github/rkhleics/wagtailmenus/badge.svg?branch=master
   :target: https://coveralls.io/github/rkhleics/wagtailmenus?branch=master
