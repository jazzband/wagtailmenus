# What is wagtailmenus?

It's an extension for torchbox's [Wagtail CMS](https://github.com/torchbox/wagtail) to help you handle multi-level navigation more consistently in your wagtail project. 

## Want to use this in your project?

The project is still in development. Code hasn’t yet been optimised for use outside of the RKH project workflow, and we are unable to offer any support at this time. If you wish to use `wagtailmenus` in your project, you do so at your own risk, and will have to overcome any issues yourself.

## Why does the project exist?

We’re forever coming across the same problems on sites we put together using Wagtail, and wanted a nice, consistent, but flexible way overcome them.

### 1) Page trees on their own are often insufficient for creating complex menus 

If all pages in your tree contain important content, and need to be accessible from the main navigation, a page tree alone can make that difficult in multi-level navigation. In dropdown or hover menus, menu items for pages with children commonly become just a 'toggle' for getting to it's children pages, making that page difficult  to access.

In the past we've always hacked around this issue by adding additional pages into the tree, or repeating the page automatically alongside it's children in menu templates, or adding extra items with javascript, etc etc. Lots of different approaches, changing from project to project, depending on who was solving the problem.

### 2) We sometimes want a menu item to link to a certain part of a page, or to an external URL

That's very difficult to do with just a page tree, and often resorts in certain menus being fixed, or partly fixed; which is difficult to manage over a long project life cycle, and bound to trip you up at least once. 

### 3) Giving the client free reign over the main menu isn't always appropriate

The main navigation on a site is often the result of some intense thought and conversation. Add to that the design implications of horizontal navs, and styling them to work responsively, and there's certainly an argument for detaching the main navigation from the page tree to a degree. 

### 4) We often find ourselves wanting other 'flat' menus to output links elsewhere in project templates

Sets of links in the footer, or an extra 'info' nav in the header, or some other menu only relevant in a certain section. 

## How does this project help with all that?

### It gives you independent control over your main menu

Create a `MainMenu` instance for your site (or one for each site, if it's a multi-site project), and use it's inline 'MainMenuItem's to control your root level items. They can be pages or custom URLS. You can also add a hash or querystring to the page URL (to get to a specific tab or section), and control which pages you want to allow children/sub menus for.

Past the root level, your existing `Page` structure is used to drive sub-navigations, so you don't have to repeat yourself.

### A simple approach to let you access any page in a dropdown/hover menu, without adding additional pages

Extend the `MenuPage` (an abstract sub-class Wagtail's `Page` model) to create your custom page types, and get a couple of fields that allow you to control advanced menu behaviour for each page (find them in the 'Settings' tab). With the behaviour defined on the page, you can access the preferred behaviour wherever that page is output in any menu, and handle things consistently.

**Using custom `edit_panels` for your Pages?** Check out `panels.py`… there should be something there that can help

### Create and manage various 'flat menus' for use throughout your project

Create `FlatMenu` instances to help you manage lists of links throughout your project. Each `FlatMenu` will have a handle, which you can easily use within templates to output them using a standard template.

**Got a multi-site project?** Create separate versions of your `FlatMenu` for each site, using the same handle for each site. The `flat_menu` templatetag will automatically grab the correct one when rendering to a template.

### A set of powerful templatetags and templates included

With output designed to be fully accessible and compatible with Bootstrap3. Templates can be overridden easily for each project if you need to do something different.

## How to install

1. Install the package using pip: `pip install git+https://github.com/rkhleics/wagtailmenus.git`
2. Add `wagtailmenus` to `INSTALLED_APPS` in your project settings (after `wagtailmodeladmin` and before your `core` app)
3. Run `python manage.py migrate wagtailmenus` to set up the initial database tables
4. In your `core` app and other apps (wherever you have defined a custom page/content model to use in your project), import `MenuPage` from `wagtailmenus.models`, and extend that instead of `Page` from `wagtail.wagtailcore.models`
5. Run `python manage.py makemigrations` to create migrations for the apps you've updated
6. Run `python manage.py migrate` to add apply those migrations

### Creating and using `MainMenu`

1. Log into the Wagtail CMS for your project (as a superuser)
2. Click on `Settings` in the side menu to access the options in there, then select `Main menu`
3. Click the button at the top of the page to add a main menu for your site (or one for each of your sites if you are running a multi-site setup), using the `MENU ITEMS` InlinePanel to define the root level items.
4. Save any menus you create
5. In whichever template you want to output your main menu in, load `menu_tags` using `{% load menu_tags %}`
6. Use the `{% main_menu %}` tag where you want the menu to appear

**Optional params for `main_menu`**

The `main_menu` templatetag accepts an optional parameter `show_multiple_levels` to let you control whether multiple levels should be displayed, which defaults to `True` if not provided. If you only want top-level items to display, you can do that with `{% main_menu show_multiple_levels=False %}`

### Creating and using 'FlatMenu'

1. Log into the Wagtail CMS for your project (as a superuser)
2. Click on `Settings` in the side menu to access the options in there, then select `Flat menus`
3. Click the button at the top of the page to add a flat menu for your site (or one for each of your sites if you are running a multi-site setup), choosing a 'unique for site' `handle` to reference in your templates, and using the `MENU ITEMS` InlinePanel to define the the links you want to appear in it.
4. Save your new menu
5. In whichever template you want to output your flat menu, load `menu_tags` using `{% load menu_tags %}`
6. Use the `{% flat_menu 'menu-handle' %}` tag where you want the menu to appear, where 'menu-handle' is the unique handle for the menu you want to use

**Optional params for `flat_menu`**

The `flat_menu` templatetag accepts an optional parameter `show_menu_heading` to let you control whether a heading should be displayed if one has been added to the menu you're using. It is simply passed through to the `flat_menu.html` template, to allow you to conditionally display it in the template. It defaults to `True` if not provided. If you definitely don't want the headings to be displayed where you're outputting them, you can do that with `{% flat_menu 'menu-handle' show_menu_heading=False %}`

### Using the `section_menu` tag

1. In whichever template you wish to add a context-specific, page-driven 'section menu' to (in a sidebar, for example), load `menu_tags` using `{% load menu_tags %}`
2. Use the `{% section_menu %}` tag where you want the menu to appear

**Optional params for `section_menu`**

The `section_menu` templatetag accepts two optional parameters:

- `show_section_root`: This value is passed through to the `section_menu.html` template, where it is used to conditionally display the root page element. Defaults to `True` if not provided.
- `show_multiple_levels`: let you control whether multiple levels should be displayed. Defaults to `True` if not provided.

So, if you wanted your section menu to show second-level pages only, you could do that with `{% section_menu show_section_root=False show_multiple_levels=False %}`

### Controlling 'repeating' behaviour for specific

Let's say you have an 'About Us' section on your site. The top-level 'About Us' page has a decent amount of important content on it, and it also has important children pages that have more specific content (e.g. 'Meet the team', 'Our mission and values', 'Staff vacancies'). You want people to be able to access the top-level 'About Us' page from your navigation as easily as the other pages, but you're using a drop-down menu, and the 'About Us' page link has simply become a toggle for hiding and showing it's children pages.

Presuming the 'About Us' page uses a model that extends the `wagtailmenus.models.MenuPage`:

1. Log into the Wagtail CMS for your project
2. Find the 'About Us' page and click to get to it's 'edit' page
3. Click on the `Settings` tab
4. Uncollapse the `ADVANCED MENU BEHAVIOUR` panel by clicking the read arrow.
5. Tick the checkbox that appears, and optionally provide some custom link text to use for the repeated nav item
6. Save your changes.

In a multi-level main menu or section menu, an additional link will now appear alongside the children of 'About Us', allowing it to be accessed more easily. The page title will be repeated by default, but it's often desirable to use different text for the repeated nav item (commonly 'Overview' or 'Section home'). You can do that by altering the value of **Link text for sub-navigation item**.
