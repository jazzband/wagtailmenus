[![Build Status](https://travis-ci.org/rkhleics/wagtailmenus.svg?branch=master)](https://travis-ci.org/rkhleics/wagtailmenus)
[![PyPi Version](https://img.shields.io/pypi/v/wagtailmenus.svg)](https://pypi.python.org/pypi/wagtailmenus)
[![Coverage Status](https://coveralls.io/repos/github/rkhleics/wagtailmenus/badge.svg?branch=master)](https://coveralls.io/github/rkhleics/wagtailmenus?branch=master)

# What is wagtailmenus?

It's an extension for Torchbox's [Wagtail CMS](https://github.com/torchbox/wagtail) to help you manage and render multi-level navigation and simple flat menus in a consistent, flexible way.

The current version is compatible with Wagtail >= 1.5, and Python 2.7, 3.3, 3.4 and 3.5.

## What does wagtailmenus do?

### 1. Gives you independent control over your root-level main menu items

The `MainMenu` model lets you define the root-level items for your projects's main navigation (or one for each site, if it's a multi-site project) using an inline model `MainMenuItem`. These items can link to pages (you can append an optional hash or querystring to the URL, too) or custom URLs. The custom URL field won't force you to enter a valid URL either, so you can add things like "#request-callback" or "#signup" to link to areas on the active page (perhaps as JS modals).

<img alt="Screenshot of MainMenu edit page in Wagtail admin" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/wagtailmenus-mainmenu-edit.png" />

The site's page tree powers everything past the root level, so you don't have to recreate it elsewhere. And as you'd expect, only links to published pages will appear when rendering.

Pages still need to have `show_in_menus` checked to appear in menus (if you really needed to hide a page for some reason, it would be frustrating if they didn't), but your project's main navigation (likely displayed in a way that is sensitive to change) will be protected from accidental additions.

### 2. Allows you to manage multiple 'flat menus' via the CMS

Have you ever hard-coded a menu into a footer at the start of a project, only for those pages never to come into existence? Or maybe the pages were created, but their URLs changed later on, breaking the hard-coded links? How about 'secondary navigation' menus in headers? Flat menus allow you to manage these kind of menus via the CMS, instead of hard-coding them. This means that the page URLs dynamically update to reflect changes, and making updates is possible without having to touch a single line of code.

<img alt="Screenshot of FlatMenu list page in Wagtail admin" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/wagtailmenus-flatmenu-list.png" />

As you'd expect, only links to published pages will appear when rendering, and just like main menu items, pages must have `show_in_menus` checked in order to appear in flat menus.

Flat menus are designed for outputting simple, flat lists of links, but they CAN be made to display multiple levels of pages too. See the instructions below for [using the `{% flat_menu %}` tag](#flat_menu-tag).

### 3. Offers a solution to the issue of key page links becoming 'toggles' in multi-level drop-down menus

Extend the `wagtailmenus.models.MenuPage` model instead of the usual `wagtail.wagtailcore.models.Page` to create your custom page types, and gain a couple of extra fields that will allow you to configure certain pages to appear again alongside their children in multi-level menus. Use the menu tags provided, and that behaviour will remain consistent in all menus throughout your site.

<img alt="Screenshot showing the repeated nav item in effect" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/repeating-item.png" />

No more adding additional pages into the tree. No more hard-coding additional links into templates, or resorting to javascript hacks.

### 4. Gives you a set of powerful template tags to render your menus consistently

Each tag comes with a default template that's designed to be fully accessible and compatible with Bootstrap 3. Limiting any project to a set of pre-defined templates would be silly though, which is why every template tag allows you to render menus using a template of your choosing. You can also override the templates in the same way as any other Django project... by putting templates of the same name into a preferred location.

<img alt="Screenshot from Sublime editor showing menu template code" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/wagtailmenus-menu-templates.png" />

## Installation instructions

### For wagtail `1.5` and up

1. Install the package using pip: `pip install wagtailmenus`.
2. Add `wagtail.contrib.modeladmin` to `INSTALLED_APPS` in your project settings, if it's not there already.
3. Add `wagtailmenus` to `INSTALLED_APPS` in your project settings.
4. Run `python manage.py migrate wagtailmenus` to set up the initial database tables.

### For wagtail `1.4.5` and below

Since version `1.2`, watailmenus has depended on the `wagtail.contrib.modeladmin` package that was added to wagtail in `1.5`. However, earlier versions of wagtailmenus can be used with earlier versions of wagtail with the help of another third-party package, [wagtailmodeladmin](https://github.com/rkhleics/wagtailmodeladmin).

1. Install `wagtailmodeladmin` by following these instructions: https://github.com/rkhleics/wagtailmodeladmin.
2. Install this package using pip: `pip install wagtailmenus>=1.1.1,<1.2.0`.
3. Add `wagtailmenus` to `INSTALLED_APPS` in your project settings (after `wagtailmodeladmin` and before your `core` app).
4. Run `python manage.py migrate wagtailmenus` to set up the initial database tables.

### Additional steps for `MenuPage` usage

**NOTE:** It is not necessary to extend `MenuPage` for all custom page types; Just ones you know will be used for pages that may have children, and will need the option to repeat themselves in sub-menus when listing those children.

1. In your `core` app and other apps (wherever you have defined a custom page/content model to use in your project), import `wagtailmenus.models.MenuPage` and extend that instead of `wagtail.wagtailcore.models.Page`.
2. Run `python manage.py makemigrations` to create migrations for the apps you've updated.
3. Run `python manage.py migrate` to add apply those migrations.

## Usage instructions

**Skip to a section:**

1. [Defining root-level main menu items in the CMS](#defining-main-menu-items)
2. [Using the `{% main_menu %}` tag](#main_menu-tag)
3. [Defining flat menus in the CMS](#defining-flat-menus)
4. [Using the `{% flat_menu %}` tag](#flat_menu-tag)
5. [Using the `{% section_menu %}` tag](#section_menu-tag)
6. [Using the `{% children_menu %}` tag](#children_menu-tag)
7. [Using the `{% sub_menu %}` tag](#sub_menu-tag)
8. [Writing your own menu templates](#writing-menu-templates)
9. [Optional repetition of selected pages in menus using `MenuPage`](#using-menupage)
10. [Overriding default behaviour with settings](#app-settings)

### <a id="defining-main-menu-items"></a>1. Defining root-level main menu items in the CMS

1. Log into the Wagtail CMS for your project (as a superuser).
2. Click on `Settings` in the side menu to access the options in there, then select `Main menu`.
3. You'll be automatically redirected to the `Main menu` edit page for the current site (or the 'default' site, if the current site cannot be identified). For multi-site projects, a 'site switcher' will appear in the top right, allowing you to edit main menus for each site.
4. Use the **MENU ITEMS** inline panel to define the root-level items, and save your changes when finished.

### <a id="defining-flat-menus"></a>2. Defining flat menus in the CMS

1. Log into the Wagtail CMS for your project (as a superuser).
2. Click on `Settings` in the side menu to access the options in there, then select `Flat menus`.
3. Click the button at the top of the page to add a flat menu for your site (or one for each of your sites if you are running a multi-site setup). <img alt="Screenshot indicating the location of the add button on the FlatMenu list page" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/wagtailmenus-flatmenu-add.png" />
4. Fill out the form, choosing a 'unique for site' `handle` to reference in your templates, and using the **MENU ITEMS** inline panel to define the links you want the menu to have. Save your changes when finished. <img alt="Screenshot showing the FlatMenu edit interface" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/wagtailmenus-flatmenu-edit.png" />

### <a id="main_menu-tag"></a>3. Using the `{% main_menu %}` tag

The `{% main_menu %}` tag allows you to display the `MainMenu` defined for the current site in your Wagtail project, with CSS classes automatically applied to each item to indicate the current page or ancestors of the current page. It also does a few sensible things, like never adding the 'ancestor' class for a homepage link, or outputting children for it.

1. In whichever template you want your main menu to appear, load `menu_tags` using `{% load menu_tags %}`.
2. Add `{% main_menu %}` to your template, where you want the menu to appear.

**Optional params for `{% main_menu %}`**

- **`max_levels`** (default: `2`): Provide an integer value to control how many levels of pages should be rendered. If you only want to display the root-level menu items defined as inlines in the CMS (whether the selected pages have children or not), add `max_levels=1` to the tag in your template. You can display additional levels by providing a higher value. You can also override the default value by adding a `WAGTAILMENUS_DEFAULT_MAIN_MENU_MAX_LEVELS` setting to your project's settings module.
- **`show_multiple_levels`** (default: `True`): Adding `show_multiple_levels=False` to the tag in your template essentially overrides `max_levels` to `1`. It's just a little more descriptive.  
- **`allow_repeating_parents`** (default: `True`): Repetition-related settings on your pages are respected by default, but you can add `allow_repeating_parents=False` to ignore them, and not repeat any pages in sub-menus when rendering multiple levels.
- **`apply_active_classes`** (default: `True`): The tag will attempt to add 'active' and 'ancestor' CSS classes to the menu items (where applicable) to indicate the active page and ancestors of that page. To disable this behaviour, add `apply_active_classes=False` to the tag in your template. You can change the CSS classes used by adding `WAGTAILMENUS_ACTIVE_CLASS` and `WAGTAILMENUS_ACTIVE_ANCESTOR_CLASS` settings to your project's settings module.
- **`template`** (default: `'menus/main_menu.html'`): Lets you render the menu to a template of your choosing. You can also name an alternative template to be used by default, by adding a `WAGTAILMENUS_DEFAULT_MAIN_MENU_TEMPLATE` setting to your project's settings module.

### <a id="flat_menu-tag"></a>4. Using the `{% flat_menu %}` tag

1. In whichever template you want your menu to appear, load `menu_tags` using `{% load menu_tags %}`.
2. Add `{% flat_menu 'menu-handle' %}` to your template, where you want the menu to appear (where 'menu-handle' is the unique handle for the menu you added).

**Optional params for `{% flat_menu %}`**

- **`show_menu_heading`** (default: `True`): Passed through to the template used for rendering, where it can be used to conditionally display a heading above the menu.
- **`show_multiple_levels`** (default: `False`): Flat menus are designed for outputting simple, flat lists of links. But, if the need arises, you can add `show_multiple_levels=True` to the tag in your template to output multiple page levels. If you haven't already, you may also need to check the **"Allow sub-menu for this item"** box for the menu items you wish to show further levels for.
- **`max_levels`** (default: `2`): If `show_multiple_levels=True` is being provided to enable multiple levels, you can use this parameter to specify how many levels you'd like to display.
- **`apply_active_classes`** (default: `False`): Unlike `main_menu` and `section_menu`, `flat_menu` will NOT attempt to add 'active' and 'ancestor' classes to the menu items by default, as this is often not useful. You can override this by adding `apply_active_classes=true` to the tag in your template.
- **`template`** (default: `'menus/flat_menu.html'`): Lets you render the menu to a template of your choosing. You can also name an alternative template to be used by default, by adding a `WAGTAILMENUS_DEFAULT_FLAT_MENU_TEMPLATE` setting to your project's settings module.

### <a id="section_menu-tag"></a>5. Using the `{% section_menu %}` tag

The `{% section_menu %}` tag allows you to display a context-aware, page-driven menu in your project's templates, with CSS classes automatically applied to each item to indicate the active page or ancestors of the active page.  

1. In whichever template you want the section menu to appear, load `menu_tags` using `{% load menu_tags %}`.
2. Add `{% section_menu %}` to your template, where you want the menu to appear.

**Optional params for `{% section_menu %}`**

- **`show_section_root`** (default: `True`): Passed through to the template used for rendering, where it can be used to conditionally display the root page of the current section.
- **`max_levels`** (default: `2`): Lets you control how many levels of pages should be rendered (the section root page does not count as a level, just the first set of pages below it). If you only want to display the first level of pages below the section root page (whether pages linked to have children or not), add `max_levels=1` to the tag in your template. You can display additional levels by providing a higher value.
- **`show_multiple_levels`** (default: `True`): Adding `show_multiple_levels=False` to the tag in your template essentially overrides `max_levels` to `1`. It's just a little more descriptive.  
- **`allow_repeating_parents`** (default: `True`): Repetition-related settings on your pages are respected by default, but you can add `allow_repeating_parents=False` to ignore them, and not repeat any pages in sub-menus when rendering.
- **`apply_active_classes`** (default: `True`): The tag will add 'active' and 'ancestor' classes to the menu items where applicable, to indicate the active page and ancestors of that page. To disable this behaviour, add `apply_active_classes=False` to the tag in your template.
- **`template`** (default: `'menus/section_menu.html'`): Lets you render the menu to a template of your choosing. You can also name an alternative template to be used by default, by adding a `WAGTAILMENUS_DEFAULT_SECTION_MENU_TEMPLATE` setting to your project's settings module.

### <a id="children_menu-tag"></a>6. Using the `{% children_menu %}` tag

The `{% children_menu %}` tag can be used in page templates to display a menu of children of the current page. You can also use the `parent_page` argument to show children of a different page.

1. In whichever template you want the menu to appear, load `menu_tags` using `{% load menu_tags %}`.
2. Use the `{% children_menu %}` tag where you want the menu to appear.

**Optional params for `{% children_menu %}`**

- **`parent_page`**: The tag will automatically pick up `self` from the context to render the children for the active page, but you render a children menu for a different page, if desired. To do so, add `parent_page=page_obj` to the tag in your template, where `page_obj` is the `Page` instance you wish to display children for.
- **`max_levels`** (default: `1`): Lets you control how many levels of pages should be rendered. For example, if you want to display the direct children pages and their children too, add `max_levels=2` to the tag in your template.
- **`allow_repeating_parents`** (default: `True`): Repetition-related settings on your pages are respected by default, but you can add `allow_repeating_parents=False` to ignore them, and not repeat any pages in sub-menus when rendering.
- **`apply_active_classes`** (default: `False`): Unlike `main_menu` and `section_menu`, `children_menu` will NOT attempt to add 'active' and 'ancestor' classes to the menu items by default, as this is often not useful. You can override this by adding `apply_active_classes=true` to the tag in your template.
- **`template`** (default: `'menus/children_menu.html'`): Lets you render the menu to a template of your choosing. You can also name an alternative template to be used by default, by adding a `WAGTAILMENUS_DEFAULT_CHILDREN_MENU_TEMPLATE` setting to your project's settings module.


### <a id="sub_menu-tag"></a>6. Using the `{% sub_menu %}` tag

The `{% sub_menu %}` tag is used within menu templates to render additional levels of pages within a menu. It's designed to pick up on variables added to the context by the other menu tags, and so can behave a little unpredictably if called directly, without those context variables having been set. It requires only one parameter to work, which is `menuitem_or_page`, which can either be an instance of `MainMenuItem`, `FlatMenuItem`, or `Page`.

**Optional params for `{% sub_menu %}`**

- **`stop_at_this_level`**: By default, the tag will figure out whether further levels should be rendered or not, depending on what you supplied as `max_levels` to the original menu tag. However, you can override that behaviour by adding either `stop_at_this_level=True` or `stop_at_this_level=False` to the tag in your custom menu template.
- **`allow_repeating_parents`**: By default, the tag will inherit this behaviour from whatever was specified for the original menu tag. However, you can override that behaviour by adding either `allow_repeating_parents=True` or `allow_repeating_parents=False` to the tag in your custom menu template.
- **`apply_active_classes`**: By default, the tag will inherit this behaviour from whatever was specified for the original menu tag. However, you can override that behaviour by adding either `apply_active_classes=True` or `apply_active_classes=False` to the tag in your custom menu template.
- **`template`** (default: `'menus/sub_menu.html'`): Lets you render the menu to a template of your choosing. You can also name an alternative template to be used by default, by adding a `WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE` setting to your project's settings module.

### <a id="writing-menu-templates"></a>8. Writing your own menu templates

The following variables are added to the context by all of the above tags, which you can make use of in your templates:

- **`menu_items`**: A list of `MenuItem` or `Page` objects with additional attributes added to help render menu items for the current level.
- **`current_level`**: The current level being rendered. This starts at `1` for the initial template tag call, then increments each time `sub_menu` is called recursively in rendering that same menu.
- **`current_template`**: The name of the template currently being used for rendering. This is most useful when rendering a `sub_menu` template that calls `sub_menu` recursively, and you wish to use the same template for all recursions.
- **`max_levels`**: The maximum number of levels that should be rendered, as determined by the original `main_menu`, `section_menu`, `flat_menu` or `children_menu` tag call.
- **`allow_repeating_parents`**: A boolean indicating whether `MenuPage` fields should be respected when rendering further menu levels.
- **`apply_active_classes`**: A boolean indicating whether `sub_menu` tags should attempt to add  'active' and 'ancestor' classes to menu items when rendering further menu levels.

**Each item in `menu_items` has the following attributes:**

- **`href`**: The URL that the menu item should link to
- **`text`**: The text that should be used for the menu item
- **`active_class`**: A class name to indicate the 'active' state of the menu item. The value will be 'active' if linking to the current page, or 'ancestor' if linking to one of it's ancestors.
- **`has_children_in_menu`**: A boolean indicating whether the menu item has children that should be output as a sub-menu.

### <a id="using-menupage"></a>9. Optional repetition of selected pages in menus using `MenuPage`

Let's say you have an 'About Us' section on your site. The top-level 'About Us' page has content that is just as important as that on the more specific pages below it (e.g. 'Meet the team', 'Our mission and values', 'Staff vacancies'). Because of this, you'd like visitors to be able to access the 'About Us' page from your navigation as easily as those pages. But, your site uses drop-down navigation, and the 'About Us' link no longer takes you to that page when clicked... it simply acts as a toggle for hiding and showing the pages below it:

<img alt="Screenshot showing an example navigation" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/no-repeating-item.png" />

Presuming the 'About Us' page extends `wagtailmenus.models.MenuPage`:

1. Edit the 'About Us' page in the CMS, and click on the `Settings` tab.
2. Uncollapse the `ADVANCED MENU BEHAVIOUR` panel by clicking the downward-pointing arrow next to the panel's label. <img alt="Screenshot showing the collapsed 'advanced menu behaviour' panel" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/wagtailmenus-menupage-settings-collapsed.png" />
4. Tick the **Repeat in sub-navigation** checkbox that appears, and publish your changes. <img alt="Screenshot show the expanded 'advanced menu behaviour' panel" src="https://github.com/rkhleics/wagtailmenus/blob/master/screenshots/wagtailmenus-menupage-settings-visible.png" />

Now, wherever the children of the `About Us` page are output (using one of the above menu tags), an additional link to the `About Us` page will appear alongside them, allowing the page to be accessed more easily. In the example above, you'll see I've added the text **Section overview** into the `Repeated item link text` field. With this set, the repeated item text should be 'Section overview', instead of just repeating the page's title, like so:

<img alt="Screenshot showing the repeated nav item in effect" src="https://raw.githubusercontent.com/rkhleics/wagtailmenus/master/screenshots/repeating-item.png" />

The menu tags do some extra work to make sure both links are never assigned the 'active' class. When on the 'About Us' page, the tags will treat the repeated item as the 'active' page, and just assign the 'ancestor' class to the original, so that the behaviour/styling is consistent with other page links rendered at that level.

#### NEW IN 1.3! Adding further sub-menu items for a page

`MenuPage` objects have a `modify_submenu_items()` method, which is responsible for adding the 'repeated' menu item (mentioned above) when the appropriate fields have been set. If for any reason you want to dynamically add more links to a page's sub-menu, it's possible to override `modify_submenu_items()` on your page model and add them there. For example:

```python

from django.db import models
from wagtailmenus.models import MenuPage

class MyPageModel(MenuPage):
	add_submenu_item_for_news = models.BooleanField(default=False)

	def modify_submenu_items(
		self, menu_items, current_page, current_ancestor_ids, current_site,
        allow_repeating_parents, apply_active_classes, original_menu_tag=''
    ):
        menu_items = super(MyPageModel,self).modify_menu_items(
        	menu_items, current_page, current_ancestor_ids, current_site,
            allow_repeating_parents, apply_active_classes, original_menu_tag=''
        )
        if self.add_submenu_item_for_news:
        	menu_items.append({
        		'href': '/news/',
        		'text': 'Read the news',
        		'active_class': 'news-link',
        	})
		return menu_items
```

Even if your page model doesn't extend `MenuPage`, you can add a new method to
your model with the same name, and taking the same arguments, and it will be
used whenever generating sub-menus for pages of that type. Just make sure to
always return `menu_items`, whether you made any changes to it's contents or
not.

### <a id="app-settings"></a>10. Changing the default settings

You can override some of wagtailmenus' default behaviour by adding one of more of the following to your project's settings:

- **`WAGTAILMENUS_ACTIVE_CLASS`** (default: `'active'`): The class added to menu items for the currently active page (when using a menu template with `apply_active_classes=True`)
- **`WAGTAILMENUS_ACTIVE_ANCESTOR_CLASS`** (default: `'ancestor'`): The class added to any menu items for pages that are ancestors of the currently active page (when using a menu template with `apply_active_classes=True`)
- **`WAGTAILMENUS_MAINMENU_MENU_ICON`** (default: `'list-ol'`): Use this to change the icon used to represent `MainMenu` in the Wagtail admin area.
- **`WAGTAILMENUS_FLATMENU_MENU_ICON`** (default: `'list-ol'`): Use this to change the icon used to represent `FlatMenu` in the Wagtail admin area.
- **`WAGTAILMENUS_SECTION_ROOT_DEPTH`** (default: `3`): Use this to specify the 'depth' value of a project's 'section root' pages. For most Wagtail projects, this should be `3` (Root page = 1, Home page = 2), but it may well differ, depending on the needs of the project.
- **`WAGTAILMENUS_DEFAULT_MAIN_MENU_TEMPLATE`** (default: `'menus/main_menu.html'`): The name of the template used for rendering by the `{% main_menu %}` tag when a `template` parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_FLAT_MENU_TEMPLATE`** (default: `'menus/flat_menu.html'`): The name of the template used for rendering by the `{% flat_menu %}` tag when a `template` parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_SECTION_MENU_TEMPLATE`** (default: `'menus/section_menu.html'`): The name of the template used for rendering by the `{% section_menu %}` tag when a `template` parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_CHILDREN_MENU_TEMPLATE`** (default: `'menus/children_menu.html'`): The name of the template used for rendering by the `{% children_menu %}` tag when a `template` parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE`** (default: `'menus/sub_menu.html'`): The name of the template used for rendering by the `{% sub_menu %}` tag when a `template` parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_MAIN_MENU_MAX_LEVELS`** (default: `2`): The default number of maximum levels rendered by `{% main_menu %}` when a `max_levels` parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_FLAT_MENU_MAX_LEVELS`** (default: `2`): The default number of maximum levels rendered by `{% flat_menu %}` when `show_multiple_levels=True` and a `max_levels` parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_SECTION_MENU_MAX_LEVELS`** (default: `2`): The default number of maximum levels rendered by `{% section_menu %}` when a `max_levels` parameter value isn't provided.
- **`WAGTAILMENUS_DEFAULT_CHILDREN_MENU_MAX_LEVELS`** (default: `1`): The default number of maximum levels rendered by `{% children_page_menu %}` when a `max_levels` parameter value isn't provided.

## Contributing

If you'd like to become a wagtailmenus contributor, we'd be happy to have you. You should start by taking a look at our [contributor guidelines](https://github.com/rkhleics/wagtailmenus/blob/master/CONTRIBUTING.md)
