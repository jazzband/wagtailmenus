[![Build Status](https://travis-ci.org/rkhleics/wagtailmenus.svg?branch=master)](https://travis-ci.org/rkhleics/wagtailmenus)
[![PyPi Version](https://img.shields.io/pypi/v/wagtailmenus.svg)](https://pypi.python.org/pypi/wagtailmenus)
[![Coverage Status](https://coveralls.io/repos/github/rkhleics/wagtailmenus/badge.svg?branch=master)](https://coveralls.io/github/rkhleics/wagtailmenus?branch=master)

What is wagtailmenus?
=====================

It's an extension for Torchbox's [Wagtail CMS](https://github.com/torchbox/wagtail) to help you manage and render multi-level navigation and simple flat menus in a consistent, flexible way.

The current version is compatible with Wagtail 1.5 to 1.8, and Python 2.7, 3.3, 3.4 and 3.5.

What does it do?
================

1. Gives you independent control over your root-level main menu items
---------------------------------------------------------------------

The `MainMenu` model lets you define the root-level items for your project's main navigation (or one for each site, if it's a multi-site project) using an inline model `MainMenuItem`. These items can link to pages (you can append an optional hash or querystring to the URL, too) or custom URLs. The custom URL field won't force you to enter a valid URL either, so you can add things like *#request-callback* or *#signup* to link to areas on the active page (perhaps as JS modals).

The site's page tree powers everything past the root level, so you don't have to recreate it elsewhere. And as you'd expect, only links to published pages will appear when rendering.


2. Allows you to manage multiple 'flat menus' via the CMS
---------------------------------------------------------

Have you ever hard-coded a menu into a footer at the start of a project, only for those pages never to come into existence? Or maybe the pages were created, but their URLs changed later on, breaking the hard-coded links? How about 'secondary navigation' menus in headers? Flat menus allow you to manage these kind of menus via the CMS, instead of hard-coding them. This means that the page URLs dynamically update to reflect changes, and making updates is possible without having to touch a single line of code.

In a multi-site project, you can choose to define a new set of menus for each site, or you can define one set of menus for your default site and reuse them for your other sites, or use a combination of both approaches for different menus (see the **`fall_back_to_default_site_menus`** option in [using the `{% flat_menu %}` tag](#flat_menu-tag) to find out more). However you choose to do things, a 'copy' feature makes it easy to copy existing menus from one site to another via the Wagtail admin interface.


3. Provides a solution to key page links becoming just 'toggles' in multi-level drop-downs
------------------------------------------------------------------------------------------

Extend the `wagtailmenus.models.MenuPage` model instead of the usual `wagtail.wagtailcore.models.Page` to create your custom page types, and gain a couple of extra fields that will allow you to configure certain pages to appear again alongside their children in multi-level menus. Use the menu tags provided, and that behaviour will remain consistent in all menus throughout your site.

No more adding additional pages into the tree. No more hard-coding additional links into templates, or resorting to javascript hacks.

<img alt="Screenshot showing the repeated nav item in effect" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/repeating-item.png" />


4. Provides templates and template tags to render menus consistently
--------------------------------------------------------------------

Each tag comes with a default template that's designed to be fully accessible and compatible with Bootstrap 3. Limiting any project to a set of pre-defined templates would be silly though, which is why every template tag allows you to render menus using a template of your choosing. You can also override the templates in the same way as any other Django project... by putting templates of the same name into a preferred location.

<img alt="Screenshot from Sublime editor showing menu template code" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/wagtailmenus-menu-templates.png" />


Installing wagtailmenus
=======================

1. Install the package using pip: `pip install wagtailmenus`.
2. Add `wagtail.contrib.modeladmin` to `INSTALLED_APPS` in your project settings, if it's not there already.
3. Add `wagtailmenus` to `INSTALLED_APPS` in your project settings.
4. Add `wagtailmenus.context_processors.wagtailmenus` to the `context_processors` list in your `TEMPLATES` setting. The setting should look something like this:
    
	```python

    TEMPLATES = [
    	{
        	'BACKEND': 'django.template.backends.django.DjangoTemplates',
			'	DIRS': [
				os.path.join(PROJECT_ROOT, 'templates'),
			],
			'APP_DIRS': True,
			'OPTIONS': {
				'context_processors': [
					'django.contrib.auth.context_processors.auth',
					'django.template.context_processors.debug',
					'django.template.context_processors.i18n',
					'django.template.context_processors.media',
					'django.template.context_processors.request',
					'django.template.context_processors.static',
					'django.template.context_processors.tz',
					'django.contrib.messages.context_processors.messages',
					'wagtail.contrib.settings.context_processors.settings',
					'wagtailmenus.context_processors.wagtailmenus',
				],
			},
		},
	]
	
    ```
	
5. Run `python manage.py migrate wagtailmenus` to set up the initial database tables.


Making use of `MenuPage`
------------------------

While wagtailmenus' menu tags will work with your existing page tree and page types, to access some of the app's more powerful features (e.g. item repetition, programmatic manipulation of sub-menu items), you'll likely want to use the `MenuPage` model as a base for some of your page-type models.

1. In any app that defines a new page-type model, open the models file and add `MenuPage` to your imports with: `from wagtailmenus.models import MenuPage` 
2. For any page-types you'd like to become `MenuPage` pages, simply sub-class the `MenuPage` model class instead of the default `wagtail.wagtailcore.models.Page`.
2. Run `python manage.py makemigrations` to create migrations for the apps you've updated.
3. Run `python manage.py migrate` to add apply those migrations.


Using wagtailmenus
==================

1. [Defining your main menu in the CMS](#defining-main-menus)
2. [Using the `{% main_menu %}` tag](#main_menu-tag)
3. [Defining flat menus in the CMS](#defining-flat-menus)
4. [Using the `{% flat_menu %}` tag](#flat_menu-tag)
5. [Using the `{% section_menu %}` tag](#section_menu-tag)
6. [Using the `{% children_menu %}` tag](#children_menu-tag)
7. [Using the `{% sub_menu %}` tag](#sub_menu-tag)
8. [Writing your own menu templates](#writing-menu-templates)
9. [Repetition of selected pages in sub-menus with `MenuPage`](#using-menupage)
10. [Specific page instances and performance](#specific-page-use)
11. [Manipulating sub-menu items for specific page types](#modifying-submenu-items)
12. [Replacing the default models with custom ones](#custom-models)
13. [Settings reference](#app-settings)


<a id="defining-main-menus"></a>1. Defining your main menu in the CMS
---------------------------------------------------------------------

1. Log into the Wagtail CMS for your project (as a superuser).
2. Click on **Settings** in the side menu to access the options in there, then select **Main menu**.
3. You'll be automatically redirected to the an edit page for the current site (or the 'default' site, if the current site cannot be identified). For multi-site projects, a 'site switcher' will appear in the top right, allowing you to edit main menus for each site. <img alt="Screenshot of MainMenu edit page in Wagtail admin" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/wagtailmenus-mainmenu-edit.png" />
4. Use the **MENU ITEMS** inline panel to define the root-level items. If you wish, you can use the `handle` field to specify an additional value for each item, which you'll be able to access in a custom main menu template. **NOTE**: Pages need to be published, and have the `show_in_menus` checkbox checked in order to appear in menus (look under the **Promote** tab when editing pages).
5. At the very bottom of the form, you'll find the **ADVANCED SETTINGS** panel, which is collapsed by default. Click on the arrow icon next to the heading to reveal the **Maximum levels** and **Specific usage** fields, which you can alter to fit the needs of your project. For more information about specific usage, take a look at the [Specific pages instances and performance](#specific-page-use) section below.
6. Save your changes to apply them to your site.


<a id="defining-flat-menus"></a>2. Defining flat menus in the CMS
-----------------------------------------------------------------

1. Log into the Wagtail CMS for your project (as a superuser).
2. Click on `Settings` in the side menu to access the options in there, then select `Flat menus` to access the menu list page.
3. Click the button at the top of the page to add a flat menu for your site (or one for each of your sites if you are running a multi-site setup). <img alt="Screenshot showing the FlatMenu edit interface" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/wagtailmenus-flatmenu-edit.png" />
4. Fill out the form, choosing a 'unique for site' `handle` to reference in your templates. If you know in advance what `handle` values you'd like to use in your project, and would rather select from a set of pre-defined choices when managing flat menus, take a look at the `WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES` setting in the [settings reference](#app-settings) section.
5. Use the **MENU ITEMS** inline panel to define the links you want the menu to have. If you wish, you can use the `handle` field to specify an additional value for each item, which you'll be able to access in a custom flat menu template. **NOTE**: Pages need to be published and have the `show_in_menus` checkbox checked in order to appear in menus (look under the **Promote** tab when editing pages).
6. At the very bottom of the form, you'll find the **ADVANCED SETTINGS** panel, which is collapsed by default. Click on the arrow icon next to the heading to reveal the **Maximum levels** and **Specific usage** fields, which you can alter to fit the needs of your project. For more information about specific usage, take a look at the [Specific pages instances and performance](#specific-page-use) section below.
7. Save your changes to apply them to your site.

All of the flat menus created for a project will appear in the menu list page (from step 2, above) making it easy to find, update, copy or delete your menus later. As soon as you create menus for more than one site in a multi-site project, the listing page will give you additional information and filters to help manage your menus, like so: <img alt="Screenshot showing the FlatMenu listing page for a multi-site setup" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/wagtailmenus-flatmenu-list.png" />


<a id="main_menu-tag"></a>3. Using the `{% main_menu %}` tag
------------------------------------------------------------

The `{% main_menu %}` tag allows you to display the `MainMenu` defined for the current site in your Wagtail project, with CSS classes automatically applied to each item to indicate the current page or ancestors of the current page. It also does a few sensible things, like never adding the 'ancestor' class for a homepage link, or outputting children for it.

1. In whichever template you want your main menu to appear, load `menu_tags` using `{% load menu_tags %}`.
2. Add `{% main_menu %}` to your template, where you want the menu to appear.

**Optional params for `{% main_menu %}`**

- **`show_multiple_levels`** (default: `True`): Adding `show_multiple_levels=False` to the tag in your template is essentially a more descriptive way of adding `max_levels` to `1`.
- **`max_levels`** (default: `None`): Provide an integer value to override the `max_levels` field value defined on your menu. Controls how many levels should be rendered (when `show_multiple_levels` is `True`).
- **`use_specific`** (default: `None`): Provide a value to override the `use_specific` field value defined on your main menu. Allows you to control how wagtailmenus makes use of `PageQuerySet.specific()` and `Page.specific` when rendering the menu. Take a look at the [Specific pages instances and performance](#specific-page-use) section below to find out more.
- **`allow_repeating_parents`** (default: `True`): Repetition-related settings on your pages are respected by default, but you can add `allow_repeating_parents=False` to ignore them, and not repeat any pages in sub-menus when rendering multiple levels.
- **`apply_active_classes`** (default: `True`): The tag will attempt to add 'active' and 'ancestor' CSS classes to the menu items (where applicable) to indicate the active page and ancestors of that page. To disable this behaviour, add `apply_active_classes=False` to the tag in your template. You can change the CSS classes used by adding `WAGTAILMENUS_ACTIVE_CLASS` and `WAGTAILMENUS_ACTIVE_ANCESTOR_CLASS` settings to your project's settings module.
- **`template`** (default: `'menus/main_menu.html'`): Lets you render the menu to a template of your choosing. You can also name an alternative template to be used by default, by adding a `WAGTAILMENUS_DEFAULT_MAIN_MENU_TEMPLATE` setting to your project's settings module.
- **`sub_menu_template`** (default: `'menus/sub_menu.html'`): Lets you specify a template to be used for rendering sub menus. All subsequent calls to `{% sub_menu %}` within the context of the section menu will use this template unless overridden by providing a `template` value to `{% sub_menu %}` in a menu template. You can specify an alternative default template by adding a `WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE` setting to your project's settings module.



<a id="flat_menu-tag"></a>4. Using the `{% flat_menu %}` tag
------------------------------------------------------------

1. In whichever template you want your menu to appear, load `menu_tags` using `{% load menu_tags %}`.
2. Add `{% flat_menu 'menu-handle' %}` to your template, where you want the menu to appear (where 'menu-handle' is the unique handle for the menu you added).

**Optional params for `{% flat_menu %}`**

- **`show_menu_heading`** (default: `True`): Passed through to the template used for rendering, where it can be used to conditionally display a heading above the menu.
- **`show_multiple_levels`** (default: `True`): Flat menus are designed for outputting simple, flat lists of links. But, you can alter the `max_levels` field value on your`FlatMenu` objects in the CMS to enable multi-level output for specific menus. If you want to absolutely never show anything but the `MenuItem` objects defined on the menu, you can override this behaviour by adding `show_multiple_levels=False` to the tag in your template.
- **`max_levels`** (default: `None`): Provide an integer value to override the `max_levels` field value defined on your menu. Controls how many levels should be rendered (when `show_multiple_levels` is `True`).
- **`use_specific`** (default: `None`): Provide a value to override the `use_specific` field value defined on your flat menu. Allows you to control how wagtailmenus makes use of `PageQuerySet.specific()` and `Page.specific` when rendering the menu. Take a look at the [Specific pages instances and performance](#specific-page-use) section below to find out more.
- **`apply_active_classes`** (default: `False`): Unlike `main_menu` and `section_menu`, `flat_menu` will NOT attempt to add 'active' and 'ancestor' classes to the menu items by default, as this is often not useful. You can override this by adding `apply_active_classes=true` to the tag in your template.
- **`allow_repeating_parents`** (default: `True`): Repetition-related settings on your pages are respected by default, but you can add `allow_repeating_parents=False` to ignore them, and not repeat any pages in sub-menus when rendering. Please note that using this option will only have an effect if `use_specific` has a value of `1` or higher.
- **`fall_back_to_default_site_menus`** (default: `False`): When using the `{% flat_menu %}` tag, wagtailmenus identifies the 'current site', and attempts to find a menu for that site, matching the `handle` provided. By default, if no menu is found for the current site, nothing is rendered. However, if `fall_back_to_default_site_menus=True` is provided, wagtailmenus will search search the 'default' site (In the CMS, this will be the site with the '**Is default site**' checkbox ticked) for a menu with the same handle, and use that instead before giving up. The default behaviour can be altered by adding `WAGTAILMENUS_FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS=True` to your project's settings.
- **`template`** (default: `'menus/flat_menu.html'`): Lets you render the menu to a template of your choosing. You can also name an alternative template to be used by default, by adding a `WAGTAILMENUS_DEFAULT_FLAT_MENU_TEMPLATE` setting to your project's settings.
- **`sub_menu_template`** (default: `'menus/sub_menu.html'`): Lets you specify a template to be used for rendering sub menus (if enabled using `show_multiple_levels`). All subsequent calls to `{% sub_menu %}` within the context of the flat menu will use this template unless overridden by providing a `template` value to `{% sub_menu %}` in a menu template. You can specify an alternative default template by adding a `WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE` setting to your project's settings.



<a id="section_menu-tag"></a>5. Using the `{% section_menu %}` tag
------------------------------------------------------------------

The `{% section_menu %}` tag allows you to display a context-aware, page-driven menu in your project's templates, with CSS classes automatically applied to each item to indicate the active page or ancestors of the active page.  

1. In whichever template you want the section menu to appear, load `menu_tags` using `{% load menu_tags %}`.
2. Add `{% section_menu %}` to your template, where you want the menu to appear.

**Optional params for `{% section_menu %}`**

- **`show_section_root`** (default: `True`): Passed through to the template used for rendering, where it can be used to conditionally display the root page of the current section.
- **`max_levels`** (default: `2`): Lets you control how many levels of pages should be rendered (the section root page does not count as a level, just the first set of pages below it). If you only want to display the first level of pages below the section root page (whether pages linked to have children or not), add `max_levels=1` to the tag in your template. You can display additional levels by providing a higher value.
- **`use_specific`** (default: `1`): Allows you to control how wagtailmenus makes use of `PageQuerySet.specific()` and `Page.specific` when rendering the menu, helping you to find the right balance between functionality and performance. Take a look at the [Specific pages instances and performance](#specific-page-use) section below for a description of the option values supported. The default value can be altered by adding a `WAGTAILMENUS_DEFAULT_SECTION_MENU_USE_SPECIFIC` setting to your project's settings.
- **`show_multiple_levels`** (default: `True`): Adding `show_multiple_levels=False` to the tag in your template essentially overrides `max_levels` to `1`. It's just a little more descriptive.  
- **`apply_active_classes`** (default: `True`): The tag will add 'active' and 'ancestor' classes to the menu items where applicable, to indicate the active page and ancestors of that page. To disable this behaviour, add `apply_active_classes=False` to the tag in your template.
- **`allow_repeating_parents`** (default: `True`): Repetition-related settings on your pages are respected by default, but you can add `allow_repeating_parents=False` to ignore them, and not repeat any pages in sub-menus when rendering. Please note that using this option will only have an effect if `use_specific` has a value of `1` or higher.
- **`template`** (default: `'menus/section_menu.html'`): Lets you render the menu to a template of your choosing. You can also name an alternative template to be used by default, by adding a `WAGTAILMENUS_DEFAULT_SECTION_MENU_TEMPLATE` setting to your project's settings.
- **`sub_menu_template`** (default: `'menus/sub_menu.html'`): Lets you specify a template to be used for rendering sub menus. All subsequent calls to `{% sub_menu %}` within the context of the section menu will use this template unless overridden by providing a `template` value to `{% sub_menu %}` in a menu template. You can specify an alternative default template by adding a `WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE` setting to your project's settings.


<a id="children_menu-tag"></a>6. Using the `{% children_menu %}` tag
--------------------------------------------------------------------

The `{% children_menu %}` tag can be used in page templates to display a menu of children of the current page. You can also use the `parent_page` argument to show children of a different page.

1. In whichever template you want the menu to appear, load `menu_tags` using `{% load menu_tags %}`.
2. Use the `{% children_menu %}` tag where you want the menu to appear.

**Optional params for `{% children_menu %}`**

- **`parent_page`**: The tag will automatically pick up `self` from the context to render the children for the active page, but you render a children menu for a different page, if desired. To do so, add `parent_page=page_obj` to the tag in your template, where `page_obj` is the `Page` instance you wish to display children for.
- **`max_levels`** (default: `1`): Lets you control how many levels of pages should be rendered. For example, if you want to display the direct children pages and their children too, add `max_levels=2` to the tag in your template.
- **`use_specific`** (default: `1`): Allows you to control how wagtailmenus makes use of `PageQuerySet.specific()` and `Page.specific` when rendering the menu. Take a look at the [Specific pages instances and performance](#specific-page-use) section below for a description of the option values supported. The default value can be altered by adding a `WAGTAILMENUS_DEFAULT_CHILDREN_MENU_USE_SPECIFIC` setting to your project's settings.
- **`apply_active_classes`** (default: `False`): Unlike `main_menu` and `section_menu`, `children_menu` will NOT attempt to add 'active' and 'ancestor' classes to the menu items by default, as this is often not useful. You can override this by adding `apply_active_classes=true` to the tag in your template.
- **`allow_repeating_parents`** (default: `True`): Repetition-related settings on your pages are respected by default, but you can add `allow_repeating_parents=False` to ignore them, and not repeat any pages in sub-menus when rendering. Please note that using this option will only have an effect if `use_specific` has a value of `1` or higher.
- **`template`** (default: `'menus/children_menu.html'`): Lets you render the menu to a template of your choosing. You can also name an alternative template to be used by default, by adding a `WAGTAILMENUS_DEFAULT_CHILDREN_MENU_TEMPLATE` setting to your project's settings.
- **`sub_menu_template`** (default: `'menus/sub_menu.html'`): Lets you specify a template to be used for rendering sub menus. All subsequent calls to `{% sub_menu %}` within the context of the section menu will use this template unless overridden by providing a `template` value to `{% sub_menu %}` in a menu template. You can specify an alternative default template by adding a `WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE` setting to your project's settings.


<a id="sub_menu-tag"></a>7. Using the `{% sub_menu %}` tag
----------------------------------------------------------

The `{% sub_menu %}` tag is used within menu templates to render additional levels of pages within a menu. It's designed to pick up on variables added to the context by the other menu tags, and so can behave a little unpredictably if called directly, without those context variables having been set. It requires only one parameter to work, which is `menuitem_or_page`, which can either be an instance of `MainMenuItem`, `FlatMenuItem`, or `Page`.

**Optional params for `{% sub_menu %}`**

- **`stop_at_this_level`**: By default, the tag will figure out whether further levels should be rendered or not, depending on what you supplied as `max_levels` to the original menu tag. However, you can override that behaviour by adding either `stop_at_this_level=True` or `stop_at_this_level=False` to the tag in your custom menu template.
- **`apply_active_classes`**: By default, the tag will inherit this behaviour from whatever was specified for the original menu tag. However, you can override that behaviour by adding either `apply_active_classes=True` or `apply_active_classes=False` to the tag in your custom menu template.
- **`allow_repeating_parents`**: By default, the tag will inherit this behaviour from whatever was specified for the original menu tag. However, you can override that behaviour by adding either `allow_repeating_parents=True` or `allow_repeating_parents=False` to the tag in your custom menu template.
- **`template`** (default: `'menus/sub_menu.html'`): Lets you render the menu to a template of your choosing. You can also name an alternative template to be used by default, by adding a `WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE` setting to your project's settings.
- **`use_specific`**: By default, the tag will inherit this behaviour from whatever was specified for the original menu tag. However, the value can be overridden by passing this option to the {% sub_menu %} tag in your custom menu template. Take a look at the [Specific pages instances and performance](#specific-page-use) section below for a description of the option values supported.


<a id="writing-menu-templates"></a>8. Writing your own menu templates
---------------------------------------------------------------------

The following variables are added to the context by all of the above tags, which you can make use of in your templates:

- **`menu_items`**: A list of `MenuItem` or `Page` objects with additional attributes added to help render menu items for the current level.
- **`current_level`**: The current level being rendered. This starts at `1` for the initial template tag call, then increments each time `sub_menu` is called recursively in rendering that same menu.
- **`current_template`**: The name of the template currently being used for rendering. This is most useful when rendering a `sub_menu` template that calls `sub_menu` recursively, and you wish to use the same template for all recursions.
- **`max_levels`**: The maximum number of levels that should be rendered, as determined by the original `main_menu`, `section_menu`, `flat_menu` or `children_menu` tag call.
- **`allow_repeating_parents`**: A boolean indicating whether `MenuPage` fields should be respected when rendering further menu levels.
- **`apply_active_classes`**: A boolean indicating whether `sub_menu` tags should attempt to add  'active' and 'ancestor' classes to menu items when rendering further menu levels.

**Each item in `menu_items` has the following attributes:**

- **`href`**: The URL that the menu item should link to.
- **`text`**: The text that should be used for the menu item.
- **`active_class`**: A class name to indicate the 'active' state of the menu item. The value will be 'active' if linking to the current page, or 'ancestor' if linking to one of it's ancestors.
- **`has_children_in_menu`**: A boolean indicating whether the menu item has children that should be output as a sub-menu.


<a id="using-menupage"></a>9. Optional repetition of selected pages in menus using `MenuPage`
---------------------------------------------------------------------------------------------

Let's say you have an **About Us** section on your site. The top-level page has content that is just as important as that on the pages below it (e.g. "Meet the team", "Our mission and values", "Staff vacancies"). Because of this, you'd like visitors to be able to access the root page as easily as those pages. But, your site uses drop-down navigation, and the **About Us** link no longer takes you to that page when clicked... it simply acts as a toggle for hiding and showing its sub-pages:

<img alt="Screenshot showing an example navigation" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/no-repeating-item.png" />

Presuming the **About Us** page extends `wagtailmenus.models.MenuPage`:

1. Edit that page in the CMS, and click on the `Settings` tab.
2. Uncollapse the **ADVANCED MENU BEHAVIOUR** panel by clicking the downward-pointing arrow next to the panel's label. <img alt="Screenshot showing the collapsed 'advanced menu behaviour' panel" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/wagtailmenus-menupage-settings-collapsed.png" />
4. Tick the **Repeat in sub-navigation** checkbox that appears, and publish your changes. <img alt="Screenshot show the expanded 'advanced menu behaviour' panel" src="https://github.com/rkhleics/wagtailmenus/blob/master/screenshots/wagtailmenus-menupage-settings-visible.png" />

Now, wherever the children of the **About Us** page are output (using one of the above menu tags), an additional link will appear alongside them, allowing the that page to be accessed more easily. In the example above, you'll see *"Section overview"* has been added to the a **Repeated item link text** field. With this set, the link text for the repeated item should read *"Section overview"*, instead of just repeating the page's title, like so:

<img alt="Screenshot showing the repeated nav item in effect" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/repeating-item.png" />

The menu tags do some extra work to make sure both links are never assigned the `'active'` class. When on the 'About Us' page, the tags will treat the repeated item as the 'active' page, and just assign the `'ancestor'` class to the original, so that the behaviour/styling is consistent with other page links rendered at that level.


<a id="specific-page-use"></a>10. Specific pages instances and performance
--------------------------------------------------------------------------

Wagtail makes use of a something known in Django as 'multi-table inheritance'. In simple terms, this means that when you create an instance of a custom page type model, the data is saved in two different database tables. All of the standard fields from Wagtail's `Page` model are stored in one table, and any additional fields from your custom model are saved in another one. It also means that, in order for Django to return 'specific' page type instances (e.g. an `EventPage`), it needs to fetch and join data from multiple tables; which has a negative effect on performance.

Menu generation is particularly resource intensive, because a menu needs to know a lot of data about a lot of pages. Add a need for 'specific' page instances to that mix (perhaps you need to access multlingual field values, or other custom fields for CSS class names or images), and that intensity is understandably greater, as the data will likely be spread over many tables (depending on how many custom page types you are using), needing lots of database joins to put everything together.

Because every project has different needs, wagtailmenus give you some fine grained control over how 'specific' pages should be used in your menus. When defining a `MainMenu` or `FlatMenu` in the CMS, the <b>Specific page use</b> field allows you to choose one of the following options:

- **Off** (value: `0`): Use only standard `Page` model data and methods, and make the minimum number of database methods when rendering. If you aren't using wagtailmenu's `MenuPage` model in your project, don't need to access any custom page model fields in you menu templates, and aren't overriding `get_url_parts()` or other `Page` methods concerned with URL generation, you should use this option for optimal performance.
- **Auto** (value: `1`): Only use specific pages when needed for `MenuPage` operations (e.g. for 'repeating menu item' behaviour, and manipulation of sub-menu items via `has_submenu_items()` and `modify_submenu_items()` methods).
- **Top level** (value: `2`): Fetch and return specific page instances for only the top-level menu items (The pages selected as actual menu items for main or flat menus). Only works for `{{ main_menu }}` and `{{ flat_menu }}` tags. The `{{ section_menu }}`, `{{ children_menu}}` and `{{ sub_menu }}` tags will treat this the same as **Auto** (`1`).
- **Always** (value: `3`): Fetch and return specific page instances for all pages using as few database queries as possible, so that custom page-type data and methods can be accessed in your menu template. You'll likely need to use this for multilingual sites (multilingual field values won't be accessible from vanilla `Page` objects, you need the page instances to access those), or if you have models that override `get_url_parts()` or other `Page` methods concerned with generating page URLs.

All menu tags accept a `use_specific` argument, allowing you to override any default settings, or the settings applied via the CMS to individual `MainMenu` and `FlatMenu` objects. As a value, you can pass in the integer value of any of the above options, e.g. `{% main_menu use_specific=2 %}`, or the following variables should be available in the context for you to use instead: 


- `USE_SPECIFIC_OFF` (value: `0`) e.g. `{% main_menu use_specific=USE_SPECIFIC_OFF %}`
- `USE_SPECIFIC_AUTO` (value `1`) e.g. `{% main_menu use_specific=USE_SPECIFIC_AUTO %}`
- `USE_SPECIFIC_TOP_LEVEL` (value `2`) e.g. `{% main_menu use_specific=USE_SPECIFIC_TOP_LEVEL %}`
- `USE_SPECIFIC_ALWAYS` (value `3`) e.g. `{% main_menu use_specific=USE_SPECIFIC_ALWAYS %}`


<a id="modifying-submenu-items"></a>11. Manipulating sub-menu items for specific page types
-------------------------------------------------------------------------------------------

If you find yourself needing further control over the items that appear in your menus (perhaps you need to add further items for specific pages, or remove some under certain circumstances), you will likely find the **`modify_submenu_items()`** _(added in 1.3)_ and **`has_submenu_items()`** _(added in 1.4)_ methods on the [`MenuPage`](https://github.com/rkhleics/wagtailmenus/blob/master/wagtailmenus/models.py#L17) model of interest. 

For example, if you had a `ContactPage` model extended `MenuPage`, and in main menus, you wanted to add some additional links below each `ContactPage` - You could achieve that by overriding the `modify_submenu_items()` and `has_submenu_items()` methods like so:

```python

from wagtailmenus.models import MenuPage


class ContactPage(MenuPage):
    ...

    def modify_submenu_items(
        self, menu_items, current_page, current_ancestor_ids, current_site,
        allow_repeating_parents, apply_active_classes, original_menu_tag,
        menu_instance=None
    ):
        # Apply default modifications first of all
        menu_items = super(ContactPage, self).modify_submenu_items(
            menu_items, current_page, current_ancestor_ids, current_site,
            allow_repeating_parents, apply_active_classes, original_menu_tag,
            menu_instance)
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

    def has_submenu_items(self, current_page, allow_repeating_parents,
    		          original_menu_tag, menu_instance=None):
        """
        Because `modify_submenu_items` is being used to add additional menu
        items, we need to indicate in menu templates that `ContactPage` objects
        do have submenu items in main menus, even if they don't have children
        pages.
        """
        if original_menu_tag == 'main_menu':
            return True
        return super(ContactPage, self).has_submenu_items(
            current_page, allow_repeating_parents, original_menu_tag,
            menu_instance)
```

These change would result in the following HTML output when rendering a `ContactPage` instance in a main menu:

```html
	<li class=" dropdown">
        <a href="/contact-us/" class="dropdown-toggle" id="ddtoggle_18" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Contact us <span class="caret"></span></a>
        <ul class="dropdown-menu" aria-labelledby="ddtoggle_18">
            <li class="support"><a href="/contact-us/#support">Get support</a></li>
            <li class="call"><a href="/contact-us/#call">Speak to someone</a></li>
            <li class="map"><a href="/contact-us/#map">Map &amp; directions</a></li>
        </ul>
    </li>
```

You can also modify sub-menu items based on field values for specific instances, rather than doing the same for every page of the same type. Here's another example:

```python

from django.db import models
from wagtailmenus.models import MenuPage

class SectionRootPage(MenuPage):
    add_submenu_item_for_news = models.BooleanField(default=False)

    def modify_submenu_items(
        self, menu_items, current_page, current_ancestor_ids, current_site,
        allow_repeating_parents, apply_active_classes, original_menu_tag='',
        menu_instance=None
    ):
        menu_items = super(SectionRootPage,self).modify_menu_items(
            menu_items, current_page, current_ancestor_ids, current_site,
            allow_repeating_parents, apply_active_classes, original_menu_tag,
            menu_insance)
	    
        if self.add_submenu_item_for_news:
            menu_items.append({
                'href': '/news/',
                'text': 'Read the news',
                'active_class': 'news-link',
            })
        return menu_items

    def has_submenu_items(self, current_page, allow_repeating_parents,
                          original_menu_tag, menu_instance=None):
        
        if self.add_submenu_item_for_news:
            return True
        return super(SectionRootPage, self).has_submenu_items(
            current_page, allow_repeating_parents, original_menu_tag,
            menu_instance)
```


<a id="custom-models"></a>12. Overriding the default wagtailmenus models
------------------------------------------------------------------------

There are a couple of ways in which you can customise the menu and menu item models used by wagtailmenus. 

**Overriding just the menu item models**

If you only wish to change the menu item models (e.g. to add images, extra fields for translated text), but are happy for the 'main menu' and 'flat menu' models themselves to remain unchanged, you can utilise the `WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME` and `WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME` settings.

1.	Create your custom menu item model(s) by subclassing wagtailmenus' abstract model classes. e.g:
	
	```python

	from django.db import models
	from django.utils.translation import ugettext_lazy as _
	from modelcluster.fields import ParentalKey
	from wagtail.wagtailimages import get_image_model_string
	from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
	from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel
	from wagtailmenus.models import AbstractMainMenuItem, AbstractFlatMenuItem


	class CustomMainMenuItem(AbstractMainMenuItem):
		"""A custom menu item model to be used by ``wagtailmenus.MainMenu``"""

		menu = ParentalKey(
			'wagtailmenus.MainMenu',
			related_name="custom_menu_items" # important for step 3!
		)
		image = models.ForeignKey(
			get_image_model_string(),
			blank=True,
			null=True,
			on_delete=models.SET_NULL,
		)
		hover_description = models.CharField(
			max_length=250,
			blank=True
		)

		# Also override the panels attribute, so that the new fields appear
		# in the admin interface
		panels = (
	        PageChooserPanel('link_page'),
	        ImageChooserPanel('image'),
	        FieldPanel('link_url'),
	        FieldPanel('url_append'),
	        FieldPanel('link_text'),
	        FieldPanel('hover_description'),
	        FieldPanel('allow_subnav'),
	    )

	class CustomFlatMenuItem(AbstractFlatMenuItem):
		"""A custom menu item model to be used by ``wagtailmenus.FlatMenu``"""
		
		menu = ParentalKey(
			'wagtailmenus.FlatMenu',
			related_name="custom_menu_items" # important for step 3!
		)

		...
	```

2.	Run `python manage.py makemigrations appname` (where appname is the name of the app where you created your new models, e.g. 'core') to create migrations for your new models. Then run `python manage.py migrate appname` to create the necessary database tables.

3.	Add the following settings to your project to tell wagtailmenus to use your custom menu item models instead of the default ones. e.g:

	```python

	# Set this to the 'related_name' attribute used on the ParentalKey field
	WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME = "custom_menu_items"

	# Set this to the 'related_name' attribute used on the ParentalKey field
	WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME = "custom_menu_items"

	```

4.	**That's it!** The custom models will now be used instead of the default ones. The default models and their data will remain intact, even if you can no longer see them via the admin area. If you need to, you can easily write a data migration to populate your new models from existing data.


**Overriding the menu AND menu item models**

If it's the main and flat menu models themselves that you wish to override, that's possible too. But, because the default menu item models are tied to the default menu models, you'll also need to create custom menu item models (whether you wish to change their behaviour or not).

1.	Create your custom models by subclassing wagtailmenus' abstract model classes. e.g:

	```python
	from django.db import models
	from django.utils import translation
	from django.utils.translation import ugettext_lazy as _
	from modelcluster.fields import ParentalKey
	from wagtail.wagtailadmin.edit_handlers import (
    	FieldPanel, MultiFieldPanel, PageChooserPanel
    )
    from wagtailmenus import app_settings
    from wagtailmenus.models import (
		AbstractMainMenu, AbstractMainMenuItem, 
		AbstractFlatMenu, AbstractFlatMenuItem,
	)

	
	class TranslatedField(object):
	    def __init__(self, en_field, de_field, fr_field):
	        self.en_field = en_field
	        self.de_field = de_field
	        self.fr_field = fr_field

	    def __get__(self, instance, owner):
	    	active_language = translation.get_language()
	        if active_language == 'de':
	            return getattr(instance, self.de_field)
	        elif active_language == 'fr':
	            return getattr(instance, self.fr_field)
	        return getattr(instance, self.en_field)

	
	class TranslatedMainMenu(AbstractMainMenu):
    	pass


    class TranslatedMainMenuItem(AbstractMainMenuItem):
		"""A custom menu item model to be used by ``TranslatedMainMenu``"""
	
		menu = ParentalKey(
			TranslatedMainMenu, # we can directly reference the model above
			related_name=app_settings.MAIN_MENU_ITEMS_RELATED_NAME
		)
		link_text_de = models.CharField(
	        verbose_name=_("link text (german)"),
	        max_length=255,
	        blank=True,
	    )
	    link_text_fr = models.CharField(
	        verbose_name=_("link text (french)"),
	        max_length=255,
	        blank=True,
	    )
	    translated_link_text = TranslatedField(
        	'link_text', 'link_text_de', 'link_text_fr'
    	)

    	@property
    	def menu_text(self):
    		"""Use `translated_link_text` instead of just `link_text`"""
	        return self.translated_link_text or getattr(
	            self.link_page,
	            app_settings.PAGE_FIELD_FOR_MENU_ITEM_TEXT,
	            self.link_page.title
	        )

	    # Also override the panels attribute, so that the new fields appear
		# in the admin interface
	    panels = (
	        PageChooserPanel("link_page"),
	        FieldPanel("link_url"),
	        FieldPanel("url_append"),
	        FieldPanel("link_text"),
	        FieldPanel("link_text_de"),
	        FieldPanel("link_text_fr"),
	        FieldPanel("handle"),
	        FieldPanel("allow_subnav"),
	    )


    class TranslatedFlatMenu(AbstractFlatMenu):
	    heading_de = models.CharField(
	        verbose_name=_("heading (german)"),
	        max_length=255,
	        blank=True,
	    )
	    heading_fr = models.CharField(
	        verbose_name=_("heading (french)"),
	        max_length=255,
	        blank=True,
	    )
	    translated_heading = TranslatedField(
        	'heading', 'heading_de', 'heading_fr'
    	)

		panels = (
	        MultiFieldPanel(
	            heading=_("Settings"),
	            children=(
	                FieldPanel("title"),
	                FieldPanel("site"),
	                FieldPanel("handle"),
	            )
	        ),
	        MultiFieldPanel(
	            heading=_("Heading"),
	            children=(
	                FieldPanel("heading"),
	                FieldPanel("heading_de"),
	                FieldPanel("heading_fr"),
	            ),
	            classname='collapsible'
	        ),
	        AbstractFlatMenu.panels[1],
	        AbstractFlatMenu.panels[2],
	    )


	class TranslatedFlatMenuItem(AbstractFlatMenuItem):
		"""A custom menu item model to be used by ``TranslatedFlatMenu``"""
	
		menu = ParentalKey(
			TranslatedFlatMenu, # we can use the model from above
			related_name=app_settings.FLAT_MENU_ITEMS_RELATED_NAME
		)
		link_text_de = models.CharField(
	        verbose_name=_("link text (german)"),
	        max_length=255,
	        blank=True,
	    )
	    link_text_fr = models.CharField(
	        verbose_name=_("link text (french)"),
	        max_length=255,
	        blank=True,
	    )
	    translated_link_text = TranslatedField(
        	'link_text', 'link_text_de', 'link_text_fr'
    	)

    	@property
    	def menu_text(self):
    		"""Use `translated_link_text` instead of just `link_text`"""
	        return self.translated_link_text or getattr(
	            self.link_page,
	            app_settings.PAGE_FIELD_FOR_MENU_ITEM_TEXT,
	            self.link_page.title
	        )

	    # Also override the panels attribute, so that the new fields appear
		# in the admin interface
	    panels = (
	        PageChooserPanel("link_page"),
	        FieldPanel("link_url"),
	        FieldPanel("url_append"),
	        FieldPanel("link_text"),
	        FieldPanel("link_text_de"),
	        FieldPanel("link_text_fr"),
	        FieldPanel("handle"),
	        FieldPanel("allow_subnav"),
	    )

	```

2.	Run `python manage.py makemigrations appname` (replace 'appname' with the name of the app where your new menu models are defined, e.g. 'core') to create migrations for your new models. Then run `python manage.py migrate appname` to create the necessary database tables.

3.	Add the following settings to your project to tell wagtailmenus to use your custom menu models instead of the default ones (replace 'appname' with the name of the app where your new menu models are defined, e.g. 'core'). e.g:

	```python

	WAGTAILMENUS_MAIN_MENU_MODEL = "appname.TranslatedMainMenu"
	WAGTAILMENUS_FLAT_MENU_MODEL = "appname.TranslatedFlatMenu"

	```

4.	**That's it!** The custom models will now be used instead of the default ones. The default models and their data will remain intact, even if you can no longer see them via the admin area. If you need to, you can easily write a data migration to populate your new models from existing data.


<a id="app-settings"></a>13. Settings reference
-----------------------------------------------

You can override some of wagtailmenus' default behaviour by adding one of more of the following to your project's settings:

- **`WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES`** (default: `None`): Can be set to a tuple of choices in the [standard Django choices format](https://docs.djangoproject.com/en/1.10/ref/models/fields/#field-choices) to change the `FlatMenu.handle` text field into a select field with fixed choices when adding, editing or copying a `FlatMenu` in Wagtail's admin area.
- **`WAGTAILMENUS_ADD_EDITOR_OVERRIDE_STYLES`** (default: `True`): By default, wagtailmenus adds some additional styles to improve the readability of the forms on the menu management pages in the Wagtail admin area. If for some reason you don't want to override any styles, you can disable this behaviour by setting to `False`.
- **`WAGTAILMENUS_ACTIVE_CLASS`** (default: `'active'`): The class added to menu items for the currently active page (when using a menu template with `apply_active_classes=True`)
- **`WAGTAILMENUS_ACTIVE_ANCESTOR_CLASS`** (default: `'ancestor'`): The class added to any menu items for pages that are ancestors of the currently active page (when using a menu template with `apply_active_classes=True`)
- **`WAGTAILMENUS_MAINMENU_MENU_ICON`** (default: `'list-ol'`): Use this to change the icon used to represent `MainMenu` in the Wagtail admin area.
- **`WAGTAILMENUS_FLATMENU_MENU_ICON`** (default: `'list-ol'`): Use this to change the icon used to represent `FlatMenu` in the Wagtail admin area.
- **`WAGTAILMENUS_SECTION_ROOT_DEPTH`** (default: `3`): Use this to specify the 'depth' value of a project's 'section root' pages. For most Wagtail projects, this should be `3` (Root page = 1, Home page = 2), but it may well differ, depending on the needs of the project.
- **`WAGTAILMENUS_GUESS_TREE_POSITION_FROM_PATH`** (default: `True`): When not using wagtail's routing/serving mechanism to serve page objects, wagtailmenus can use the request path to attempt to identify a 'current' page, 'section root' page, allowing `{% section_menu %}` and active item highlighting to work. If this functionality is not required for your project, you can disable it by setting this value to `False`.
- **`WAGTAILMENUS_FLAT_MENUS_FALL_BACK_TO_DEFAULT_SITE_MENUS`** (default: `False`): The default value used for `fall_back_to_default_site_menus` option of the `{% flat_menu %}` tag when a parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_MAIN_MENU_TEMPLATE`** (default: `'menus/main_menu.html'`): The name of the template used for rendering by the `{% main_menu %}` tag when a `template` parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_FLAT_MENU_TEMPLATE`** (default: `'menus/flat_menu.html'`): The name of the template used for rendering by the `{% flat_menu %}` tag when a `template` parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_SECTION_MENU_TEMPLATE`** (default: `'menus/section_menu.html'`): The name of the template used for rendering by the `{% section_menu %}` tag when a `template` parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_CHILDREN_MENU_TEMPLATE`** (default: `'menus/children_menu.html'`): The name of the template used for rendering by the `{% children_menu %}` tag when a `template` parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE`** (default: `'menus/sub_menu.html'`): The name of the template used for rendering by the `{% sub_menu %}` tag when a `template` parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_SECTION_MENU_MAX_LEVELS`** (default: `2`): The maximum number of levels rendered by the `{% section_menu %}` tag when a `max_levels` parameter value isn't specified.
- **`WAGTAILMENUS_DEFAULT_CHILDREN_MENU_MAX_LEVELS`** (default: `1`): The maximum number of levels rendered by the `{% children_menu %}` tag when a `max_levels` parameter value isn't specified.
- **`WAGTAILMENUS_DEFAULT_SECTION_MENU_USE_SPECIFIC`** (default: `USE_SPECIFIC_AUTO`): Controls how 'specific' pages objects are fetched and used during rendering of the `{% section_menu %}` tag when the `use_specific` parameter value isn't supplied. 
- **`WAGTAILMENUS_DEFAULT_CHILDREN_USE_SPECIFIC`** (default: `USE_SPECIFIC_AUTO`): Controls how 'specific' pages objects are fetched and used during rendering of the `{% children_menu %}` tag when the `use_specific` parameter value isn't supplied. 
- **`WAGTAILMENUS_PAGE_FIELD_FOR_MENU_ITEM_TEXT`** (default: `'title'`): When preparing menu items for rendering, wagtailmenus looks for a field, attribute or property method with this name on each page object to populate a `text` attribute on the menu item. NOTE: wagtailmenus will only be able to access custom page attributes if specific pages are being used (See [Specific pages instances and performance](#specific-page-use) for more details). The page's `title` attribute will be used as a fallback if no attribute can found matching specified name.
- **`WAGTAILMENUS_MAIN_MENU_MODEL`** (default: `'wagtailmenus.MainMenu'`): Use this to specify a custom model to use for main menus instead of the default. The model should be a subclass of `wagtailmenus.AbstractMainMenu`. See [Overriding the default wagtailmenus models](#custom-models) for more details.
- **`WAGTAILMENUS_FLAT_MENU_MODEL`** (default: `'wagtailmenus.FlatMenu'`): Use this to specify a custom model to use for flat menus instead of the default. The model should be a subclass of `wagtailmenus.AbstractFlatMenu`. See [Overriding the default wagtailmenus models](#custom-models) for more details.
- **`WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME`** (default: `'menu_items'`): Use this to specify the 'related name' that should be used to access menu items from main menu instances. Used to replace the default `MainMenuItem` model with a custom one. See [Overriding the default wagtailmenus models](#custom-models) for more details.
- **`WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME`** (default: `'menu_items'`): Use this to specify the 'related name' that should be used to access menu items from flat menu instances. Used to replace the default `FlatMenuItem` model with a custom one. See [Overriding the default wagtailmenus models](#custom-models) for more details.


Contributing
============

Want to contribute to wagtailmenus? We'd be happy to have you! You should start by taking a look at our [contributor guidelines](https://github.com/rkhleics/wagtailmenus/blob/master/CONTRIBUTING.md)
