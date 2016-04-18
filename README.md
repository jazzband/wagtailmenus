# What is wagtailmenus?

It's an extension for torchbox's [Wagtail CMS](https://github.com/torchbox/wagtail) to help you manage complex multi-level navigation and flat menus in a consistent, flexible way.

## What does it provide?

### 1. Independent control over your root-level main menu items

The `MainMenu` model and it's orderable inline `MainMenuItem`s let you define the root-level items for your site's main navigation (or one for each site, if it's a multi-site project). Your menu items can link to pages or custom URLs, and you can append an optional hash or querystring to the URL if required. You can still hide pages from menus by unchecking `show_in_menus` on the page, but your site's root-level menu items (likely displayed in a manner that is 'sensitive' to change) will be protected from accidental additions.

Your existing `Page` structure powers everything past the root level, so you don't have to recreate your whole page tree elsewhere.

### 2. Specify pages that should repeat in dropdown/hover menus, to improve visibility/acessibility

Extend the `MenuPage` class (an abstract sub-class of Wagtail's `Page` model) to create your custom page types, and gain a couple of extra fields that allow you to control advanced menu behaviour on a page-to-page basis.

### 3. Manage multiple 'flat' menus via the Wagtail CMS

Create `FlatMenu`s to help you manage lists of links throughout your project. Each `FlatMenu` will have a unique `handle`, allowing you to reference it in `{% flat_menu %}` tags throughout your project's templates.

### 4. A set of powerful templatetags and accessible menu templates

Output from the included templates is designed to be fully accessible and compatible with Bootstrap 3. You can easily use your own templates by passing a `template` variable to any of the tags, or you can override the included templates by putting customised versions in a system-preferred location.

## How to install

1. Install the package using pip: `pip install wagtailmenus`.
2. Add `wagtailmenus` to `INSTALLED_APPS` in your project settings (after `wagtailmodeladmin` and before your `core` app).
3. Run `python manage.py migrate wagtailmenus` to set up the initial database tables.

**Optional steps, if you wish to use `MenuPage`**

**NOTE:** It is not necessary to extend `MenuPage` for all custom page types; Just ones you know will be used for pages that may have children, and will need the option to repeat themselves in sub-menus when listing those children.

1. In your `core` app and other apps (wherever you have defined a custom page/content model to use in your project), import `wagtailmenus.models.MenuPage` and extend that instead of `wagtail.wagtailcore.models.Page`.
2. Run `python manage.py makemigrations` to create migrations for the apps you've updated.
3. Run `python manage.py migrate` to add apply those migrations.

## How to use

**Skip to:**

1. [The `MainMenu` model and `{% main_menu %}` tag](#using-main-menus)
2. [The `FlatMenu` model and `{% flat_menu %}` tag](#using-flat-menus)
3. [The `{% section_menu %}` tag](#using-section-menus)
4. [Optional repetition of selected pages in menus using `MenuPage`](#using-menupage)

### <a id="using-main-menus"></a>1. The `MainMenu` model and `{% main_menu %}` tag

1. Log into the Wagtail CMS for your project (as a superuser).
2. Click on `Settings` in the side menu to access the options in there, then select `Main menu`.
3. Click the button at the top of the page to add a main menu for your site (or one for each of your sites if you are running a multi-site setup), using the `MENU ITEMS` InlinePanel to define the root level items.
4. In whichever template you want to output your main menu in, load `menu_tags` using `{% load menu_tags %}`.
5. Use the `{% main_menu %}` tag where you want the menu to appear.

**Optional params for `{% main_menu %}`**

- **`show_multiple_levels`**: Default: `True`. Lets you control whether subsequent levels should be rendered.
- **`allow_repeating_parents`**: Default: `True`. If set to False, will ignore any repetition-related settings for individual pages, and not repeat any pages when rendering.
- **`template`**: Default: `menus/main_menu.html`. Lets you render the menu to a template of your choosing.
- **`apply_active_classes`**: Default: `True`. wagtailmenus will attempt to add 'active' and 'ancestor' classes to the menu items, based on the current page (`self` in the context). To disable this behaviour, add `apply_active_classes=False`.

### <a id="using-flat-menus"></a>2. The `FlatMenu` model and `{% flat_menu %}` tag

1. Log into the Wagtail CMS for your project (as a superuser).
2. Click on `Settings` in the side menu to access the options in there, then select `Flat menus`.
3. Click the button at the top of the page to add a flat menu for your site (or one for each of your sites if you are running a multi-site setup), choosing a 'unique for site' `handle` to reference in your templates, and using the `MENU ITEMS` InlinePanel to define the the links you want to appear in it.
4. Save your new menu.
5. In whichever template you want to output your flat menu, load `menu_tags` using `{% load menu_tags %}`.
6. Use the `{% flat_menu 'menu-handle' %}` tag where you want the menu to appear, where 'menu-handle' is the unique handle for the menu you added.

**Optional params for `{% flat_menu %}`**

- **`show_menu_heading`**: Default: `True`. Passed through to the template used for rendering, where it can be used to conditionally display a heading above the menu.
- **`template`**: Default: `menus/flat_menu.html`. Lets you render the menu to a template of your choosing.
- **`apply_active_classes`**: Default: `False`. If you wish for wagtailmenus to attempt to add 'active' and 'ancestor' classes to the menu items, based on the current page (`self` in the context), add `apply_active_classes=True`.

### <a id="using-section-menus"></a>3. The `{% section_menu %}` tag

1. In whichever template you wish to add a context-specific, page-driven 'section menu' to your template (in a sidebar, for example), load `menu_tags` using `{% load menu_tags %}`.
2. Use the `{% section_menu %}` tag where you want the menu to appear.

**Optional params for `{% section_menu %}`**

- **`show_section_root`**: Default: `True`. Passed through to the template used for rendering, where it can be used to conditionally display the root page of the current section.
- **`show_multiple_levels`**: Default: `True`. Lets you control whether subsequent levels should be rendered.
- **`allow_repeating_parents`**: Default: `True`. If set to False, will ignore any repetition-related settings for individual pages, and not repeat any pages when rendering.
- **`template`**: Default: `menus/section_menu.html`. Lets you render the menu to a template of your choosing.
- **`apply_active_classes`**: Default: `True`. wagtailmenus will attempt to add 'active' and 'ancestor' classes to the menu items, based on the current page (`self` in the context). To disable this behaviour, add `apply_active_classes=False`.

### <a id="using-menupage"></a>4. Optional repetition of selected pages in menus using `MenuPage`

Let's say you have an 'About Us' section on your site. The top-level 'About Us' page has a decent amount of important content on it, and it also has important children pages that have more specific content (e.g. 'Meet the team', 'Our mission and values', 'Staff vacancies'). You want people to be able to access the top-level 'About Us' page from your navigation as easily as the other pages, but you're using a drop-down menu, and the 'About Us' page link has simply become a toggle for hiding and showing its children pages.

Presuming the 'About Us' page uses a model that extends `wagtailmenus.models.MenuPage`:

1. Edit the 'About Us' page in the CMS, and click on the `Settings` tab.
2. Uncollapse the `ADVANCED MENU BEHAVIOUR` panel by clicking the downward-pointing arrow next to the panel's label. ![advanced menu behaviour panel collapsed](http://i.imgur.com/XwbZjwL.png)
4. Tick the **Repeat in sub-navigation** checkbox that appears, and publish your changes. ![advanced menu behaviour panel open](http://i.imgur.com/EzBKZyB.png)

**NOTE:** If you're using a custom `TabbedInterface` for your page model, you won't see the `ADVANCED MENU BEHAVIOUR` panel by default. Take a look at `wagtailmenus.panels.py`. There should be something in there that you can import and use in your custom `TabbedInteface`, or at least something you can copy to get the panel to show.

In a multi-level main menu or section menu (as long as the template tags aren't called with `allow_repeating_parents=False`), an additional link to the 'About Us' page should now appear alongside the links to it's children pages, allowing that page to be accessed more easily. The page's title will be used as the menu text for the repeated item by default. But, it's often desirable to use different text for the repeated nav item (e.g. 'Overview' or 'Section home'). You can do this by altering the value of **Link text for sub-navigation item** (also in the `ADVANCED MENU BEHAVIOUR` panel).
