Changelog
=========


2.X.X (XX.XX.XXXX) IN DEVELOPMENT
----------------------------------

TBA


2.9.0 (04.05.2018)
------------------

* Added `WAGTAILMENUS_MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN` setting to the 'Main menu' menu item and underlying management functionality to be removed from the Wagtail admin area (thanks to Michael van de Waeter).
* Added `WAGTAILMENUS_FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN` setting to the 'Flat menus' menu item and underlying management functionality to be removed from the Wagtail admin area (thanks to Michael van de Waeter).
* Added the 'sub_menu_templates' option to menu tags to allow sub menu templates to be specified for each level.
* Updated 'get_template_names()' and 'get_sub_menu_template_names()' methods for each class to search for template paths including the level currently being rendered, allowing developers to define level-specific templates in their templates directory, and have wagtailmenus find and use them automatically.


2.8.0 (29.03.2018)
------------------

* Added improved active class attribution behaviour for menu items that link to custom URLs (Enabled using the `WAGTAILMENUS_CUSTOM_URL_SMART_ACTIVE_CLASSES` setting).
* Deprecated the existing active class attribution behaviour in favour of the above.
* Backend-specific template instances are now always used for rendering.
* Removed `get_template_engine()` method from `wagtailmenus.models.menus.Menu`
* Removed `panels` attributes from the `AbstractMainMenu` and `AbstractFlatMenu` models
* Removed `main_menu_panels` and `flat_menu_panels` from `wagtailmenus.panels`.
* Various documentation spelling/formatting corrections (thanks to Sergey Fedoseev and Pierre Manceaux).


2.7.1 (07.03.2018)
------------------

* Fixed a bug in MenuTabbedInterfaceMixin preventing `content_panels` and `settings_panels` being picked up in the editing UI when using Wagtail 2.0.
* Remove the 'alpha' notice and title notation from the 2.7.0 release notes.
* Added a badge to README.rst to indicate the documentation build status.
* Added a missing 'migrate' step to the **Developing locally** instructions in the contribution guidelines.
* Updated the code block in the **.po to .mo** conversion step in the packaging guidelines to the `find` command with `execdir`.


2.7.0 (01.03.2018)
------------------

* Added support for Wagtail 2.0 and Django 2.0
* Dropped support for Python 2 and 3.3.
* Dropped support for Wagtail versions 1.8 to 1.9
* Dropped support for Django versions 1.5 to 1.9
* Made numerous 'Python 3 only' optimisations to code.
* The `wagtailmenus.models.menus.MenuFromRootPage` class was removed.
* The `__init__()` method of `wagtailmenus.models.menus.ChildrenMenu` no
  longer accepts a **root_page** keyword argument. The parent page should be
  passed using the **parent_page** keyword instead.
* The *root_page* attribute has been removed from the
  `wagtailmenus.models.menus.ChildrenMenu` class. Use the *parent_page* 
  attribute instead.
* The `sub_menu` template tag no longer accepts a *stop_at_this_level*
  keyword argument.
* The `get_sub_menu_items_for_page()` and `prime_menu_items()` methods
  have been removed from `wagtailmenus.templatetags.menu_tags`.
* The `get_attrs_from_context()` method has been removed from 
  `wagtailmenus.utils.misc`.
* The `get_template_names()` and `get_sub_menu_template_names()` methods
  have been removed from `wagtailmenus.utils.template` and the redundant
  `wagtailmenus.utils.template` module removed.
* Fixed an issue that was preventing translated field label text appearing for
  the `handle` field when using the `FLAT_MENUS_HANDLE_CHOICES` setting
  (Contributed by @jeromelebleu)


2.6.0 (22.12.2017)
------------------ 

* Improve compatibility with alternative template backends such as `jinja2`.
  Implementation by @hongquan.
* Added compatibility with `wagtail-condensedinlinepanel`.
* Updated the menu CMS editing UI to split rendering setting field out into 
  their own tab.
* Updated tests to test compatibility with Wagtail 1.13.


2.5.1 (27.10.2017)
------------------

* Fixed a bug that was causing Django to create new migrations for wagtailmenus
  after changing Django's `LANGUAGE_CODE` setting for a project. Thanks to
  @philippbosch from A Color Bright for the fix.


2.5.0 (14.10.2017)
------------------ 

* Added rendering logic to Menu classes and refactored all existing template
  tags to make use of it (massively reducing code duplication in menu_tags.py).
* Added support for several 'hooks', allowing for easier customisation of base
  querysets and manipulation of menu items during rendering. For more
  information and examples, see the 'Hooks' section of the documentation:
  http://wagtailmenus.readthedocs.io/en/latest/advanced_topics/hooks.html
* Updated the 'sub_menu' tag to raise an error if used in a way that isn't
  supported. 
* Deprecated `get_sub_menu_items_for_page` and `prime_menu_items` methods from
  `wagtailmenus.templatetags.menu_tags` (logic moved to menu classes).
* Deprecated `get_template` and `get_sub_menu_template_names` methods from
  `wagtailmenus.utils.template` (logic moved to menu classes).
* Deprecated `get_attrs_from_context` method from `wagtailmenus.utils.misc`
  (logic moved to menu classes).
* Deprecated the `MenuFromRootPage` class from `wagtailmenus.models.menus` in
  favour of using a new `MenuFromPage` class that fits better with how it's
  used in menu classes.
* Minor tidying / renaming of tests.
* Added a 'add_menu_items_for_pages()' method to the `MenuWithMenuItems` model,
  which adds menu item to a menu object, linking to any pages passed in as a `PageQuerySet`.
* Added the 'autopopulate_main_menus' command, that can be run as part of the 
  installation process to help populate main menus based on the 'home' and 
  'section root' pages for each site.
* Fixed an issue with runtests.py that was causing tox builds in Travis CI
  to report as successful, even when tests were failing. Contributed by
  Oliver Bestwalter (obestwalter).
* Deprecated the `stop_at_this_level` argument for the `sub_menu` tag, which
  hasn't worked for a few versions.
* Added support for Wagtail 1.12.
* Made the logic in menu classes 'page_children_dict' method easier to override
  by moving it out into a separate 'get_page_children_dict()' method, which the
  original (@cached_property decorated) method calls.
* Made the logic in menu classes 'pages_for_display' method easier to override
  by moving it out into a separate 'get_pages_for_display()' method, which the
  original (@cached_property decorated) method calls. 
* Made the logic in menu classes 'top_level_items' method easier to override
  by moving it out into a separate 'get_top_level_items()' method, which the
  original (@cached_property decorated) method calls. 


2.4.0 (04.08.2017)
------------------ 

* Adjusted Meta classes on menu item models so that common behaviour is defined
  once in AbastractMenuItem.Meta.
* Refactored the AbstractMenuItem's `menu_text` property method to improve code
  readability, and better handle instances where neither link_text or link_page
  are set.
* Replaced overly long README.md with brand new documentation and a new 
  README.rst which will render better on PyPi. The documentation is kindly 
  hosted by readthedocs.org and can be found at 
  http://wagtailmenus.readthedocs.io/
* Added Chinese translations, kindly submitted by 汇民 王 (levinewong)
* Added the 'use_absolute_page_urls' argument to all template tags. When a 
  value equating to `True` is provided, the menu will be rendered using the 
  'full URL' for each page (including the protocol/domain derived from the 
  relevant `wagtailcore.models.Site` object), instead the 'relative URL' used
  by default. Developed by Trent Holliday of Morris Technology and Andy Babic.


2.3.2 (21.07.2017)
------------------ 

* Fixed a bug that would result in {% sub_menu %} being called recursively (
  until raising a "maximum recursion depth exceeded" exception) if a 
  'repeated menu item' was added at anything past the 2nd level. Thanks to
  @pyMan for raising/investigating.


2.3.1 (01.07.2017)
------------------ 

* Code example formatting fixes, and better use of headings in README.md.
* Added 'on_delete=models.CASCADE' to all relationship fields on models where
  no 'on_delete' behaviour was previously set (Django 2.0 compatibility).
* Marked a missing string for translation (@einsfr).
* Updated translations for Lithuanian, Portuguese (Brazil), and Russian.
  Many thanks to @mamorim, @matas.dailyda and @einsfr!


2.3.0 (21.06.2017)
------------------

* Added an 'AbstractLinkPage' model to wagtailmenus.models that can be easily
  sub-classed and used in projects to create 'link pages' that act in a similar
  fashion to menu items when appearing in menus, but can be placed in any part
  of the page tree.
* Updated 'modify_submenu_items', 'has_submenu_items' and 
  'get_repeated_menu_item' methods on MenuPageMixin / MenuPage to accept a 
  'request' parameter, which is used to pass in the current `HttpRequest` 
  object the menu is being rendered for.
* Added the `WAGTAILMENUS_SECTION_MENU_CLASS_PATH` setting, which can be used
  to override the `Menu` class used when using the `{% section_menu %}` tag.
* Added the `WAGTAILMENUS_CHILDREN_MENU_CLASS_PATH` setting, which can be used
  to override the `Menu` class used when using the `{% children_menu %}` tag.
* All `Menu` classes are now 'request aware', meaning `self.request` will
  return the current `HttpRequest` object within most methods. 
* Added a `get_base_page_queryset()` method to all `Menu` classes, that can be
  overridden to change the base page QuerySet used when identifying pages to
  be included in a menu when rendering. For example developers could use 
  `self.request.user` to only ever include pages that the current user has
  some permission for.
* Abstracted out most model functionality from `MenuPage` to a `MenuPageMixin`
  model, that can be used with existing page type models.
* Added wagtail 1.10 and django 1.11 test environments to tox.
* Renamed `test_frontend.py` to `test_menu_rendering.py`
* In situations where `request.site` hasn't been set by wagtail's 
  `SiteMiddleware`, the wagtailmenus context processor use the default
  site to generate menus with.
* Updated AbstractMenuItem.clean() to only ever return field-specific
  validation errors, because Wagtail doesn't render non-field errors for
  related models added to the editor interface using `InlinePanel`.
* Added Russian translations (submitted by Alex einsfr).


2.2.3 (21.07.2017)
------------------

* Fixed a bug that would result in {% sub_menu %} being called recursively (
  until raising a "maximum recursion depth exceeded" exception) if a 
  'repeated menu item' was added at anything past the 2nd level. Thanks to
  @pyMan for raising/investigating.


2.2.2 (27.03.2017)
------------------

* Got project set up in Transifex.
* Updated translatable strings throughout the project to use named variable
  substitution, and unmarked a few exception messages.
* Add Lithuanian translations (submitted by Matas Dailyda).
* Better handle situations where `request` isn't available in the context, or
  `request.site` hasn't been set.


2.2.1 (06.03.2017)
------------------

* Updated travis/tox test settings to test against Wagtail 1.9 & Django 1.10.
* Removed a couple of less useful travis/tox environment tests to help with
  test speed.
* Made use of 'extras_require' in setup.py to replace multiple requirements 
  files.
* Optimised the app_settings module so that we can ditch the questionably stuff 
  we're doing with global value manipulation on app load (solution inspired by 
  django-allauth).
* Added new symantic version handling to the project (solution inspired by
  wagtail)


2.2.0 (20.02.2017)
------------------

* Utilise Django's 'django.template.loader.select_template()' method
  to provide a more intuitive way for developers to override templates for
  specific menus without having to explicitly specify alternative templates 
  via settings or via the `template` and `sub_menu_template` options for
  each menu tag. See the updated documentation for each tag for information
  about where wagtailmenus looks for templates.
* Added the `WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS` setting to allow 
  developers to choose to have wagtailmenus look in additional site-specific
  locations for templates to render menus.
* Moved some methods out of `template_tags/menu_tags.py` into a new `utils.py`
  file to make `menu_tags.py` easier to read / maintain in future.
* Brazilian Portuguese language translations added by @MaxKurama.
* Added try/except to `AbstractMenuItem.relative_url()` so that errors aren't
  thrown when `Page.relative_url` returns `None` for some reason.


2.1.4 (21.07.2017)
------------------

* Fixed a bug that would result in {% sub_menu %} being called recursively (
  until raising a "maximum recursion depth exceeded" exception) if a 
  'repeated menu item' was added at anything past the 2nd level. Thanks to
  @pyMan for raising/investigating.


2.1.3 (20.01.2017)
------------------

* Fixed a bug in the `section_menu` tag when attempting to apply the correct
  active class to `section_root` when the `modify_submenu_items()` method has 
  been overridden to return additional items without an `active_class`
  attribute (like in the example code in README).


2.1.2 (07.01.2017)
------------------

* Fixed a bug preventing reordered menu items from retaining their new order 
  after saving. The Meta class on the new abstract models had knocked out the
  `sort_order` ordering from `wagtail.wagtailcore.models.Orderable`.


2.1.1 (02.01.2017)
------------------ 

* Fixed import error on pip install from version 2.1.0 (Adriaan Tijsseling)


2.1.0 (28.12.2016)
------------------

* Added official support for wagtail v1.8.
* Turned `wagtailmenus.app_settings` into a real settings module.
* Added `WAGTAILMENUS_MAIN_MENU_MODEL` and `WAGTAILMENUS_FLAT_MENU_MODEL`
  settings to allow the default main and flat menu models to be swapped out for
  custom models.
* Added `WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME` and 
  `WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME` settings to allow the default
  menu item models to be swapped out for custom models.
* Added the `WAGTAILMENUS_PAGE_FIELD_FOR_MENU_ITEM_TEXT` setting to allow 
  developers to specify a page attribute other than `title` to be used to
  populate the `text` attribute for menu items linking to pages.
* Added german translation by Pierre (@bloodywing).
* Split models.py into 3 logically-named files to make models easier to find.


2.0.3 (08.12.2016)
------------------

Fixed migration related issue raised by @urlsangel.


2.0.2 (08.12.2016)
------------------ 

This release is broken and shouldn't be used. Skip to v2.0.3 instead.


2.0.1 (22.11.2016)
------------------

Bug fix for `main_menu` template tag.


2.0.0 (19.11.2016)
------------------

* The `use_specific` menu tag argument can now be one of 4 integer values,
  allowing for more fine-grained control over the use of `Page.specific` and
  `PageQuerySet.specific()` when rendering menu tags (see README.md for further
  details).
* `MainMenu` and `FlatMenu` models now have a `use_specific` field, to allow
  the default `use_specific` setting when rendering that menu to be changed
  via the admin area.
* `MainMenu` and `FlatMenu` models now have a `max_levels` field, to allow the
  default `max_levels` setting when rendering that menu to be changed via the
  admin area.
* When rendering a multi-level `MainMenu` or `FlatMenu, the model instances for
  those menus pre-fetch all of pages needed to generate the entire menu. 
  The menu tags then request lists of child pages from menu instance as they 
  are needed, reducing the need to hit the database at every single branch.
* The `max_levels`, `use_specific`, `parent_page` and `menuitem_or_page`
  arguments passed to all template tags are now checked to ensure their values
  are valid, and if not, raise a `ValueError` with a helpful message to aid
  debugging.
* Developers not using the `MenuPage` class or overriding any of wagtail `Page`
  methods involved in URL generation can now enjoy better performance by
  choosing not to fetch any specific pages at all during rendering. Simply
  pass `use_specific=USE_SPECIFIC_OFF` or `use_specific=0` to the tag, or
  update the `use_specific` field value on your `MainMenu` or `FlatMenu`
  instances via the Wagtail admin area.
* Dropped support for the `WAGTAILMENUS_DEFAULT_MAIN_MENU_MAX_LEVELS` and 
  `WAGTAILMENUS_DEFAULT_FLAT_MENU_MAX_LEVELS` settings. Default values are now
  set using the `max_levels` field on the menu objects themselves.
* Dropped support for the `WAGTAILMENUS_DEFAULT_MAIN_MENU_USE_SPECIFIC` and 
  `WAGTAILMENUS_DEFAULT_FLAT_MENU_USE_SPECFIC` settings. Default values are now
  set using the `use_specific` field on the menu objects themselves.
* Eliminated a lot of code duplication in template tags by adding the
  `get_sub_menu_items_for_page` method, which is used by `sub_menu`,
  `section_menu` and `children_menu` to do most of their work.
* The default `show_multiple_levels` value for the `flat_menu` tag is now
  `True` instead of `False`. The default `max_levels` field value for
  `FlatMenu` instances is `1`, which has the same effect. Only, the value can
  be changed via the admin area,     and the changes will reflected immediately
  without having to explicitly add `show_multiple_levels=True` to the tag in
  templates.
* The `has_submenu_items()` method on `MenuPage` no longer accepts a 
  `check_for_children` argument.
* The `modify_submenu_items()` and `has_submenu_items()` methods on the
  `MenuPage` model now both accept an optional `menu_instance` value, so that
  menu_instance might be called to access pre-fetched page data without hitting
  the database.
* Added the `WAGTAILMENUS_ADD_EDITOR_OVERRIDE_STYLES` setting to allow override
  styles to be disabled.
* Other minor performance improvements.


1.6.1 (04.11.2016)
------------------

* French translations added by François GUÉRIN (frague59)


1.6.0 (28.10.2016)
------------------

* Improved confirmation messages when saving a menu in the admin area.
* Added a new test to submit the `MainMenu` edit form and check that
  it behaves as expected.
* Added some styles to menu add/edit/copy views to improve the UI.
* Added a new `context_processor` to handle some of the logic that was
  previously being done in template tags. Django's `SimpleLazyObject` class is
  used to reduce the overhead as much as possible, only doing the work when the
  values are accessed by menu tags.
* Added the `WAGTAILMENUS_GUESS_TREE_POSITION_FROM_PATH` setting to allow
  developers to disable the 'guess tree position from path' functionality 
  that comes into play when serving custom views, where the `before_serve_page`
  hook isn't activated, and `wagtailmenu_params_helper()` in `wagtail_hooks.py`
  doesn't get to add it's helpful values to the request/context.
* Updated tox environment settings to run tests against wagtail==1.7, and 
  updated pinned wagtail version in `setup.py` to reflect compatibility.
* Added unicode support for python 2.7 and added missing verbose_names to
  fields so that they can be translated (Alexey Krasnov & Andy Babic).
* Added support for a `WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES` setting that, if
  set, will turn the `CharField` used for FlatMenu.handle in add/edit/copy
  forms into a `ChoiceField`, with that setting as the available choices.


1.5.1 (10.10.2016) 
------------------

* `MenuPage.has_submenu_items()` is now only ever called if 
  `check_for_children` is True in `menu_tags.prime_menu_items()`.
  This way, the `max_levels` value supplied to the original menu tag is always
  respected, with no additional levels ever being rendered. 
  The `check_for_chilren` value passed to `has_submenu_items()` is now always
  True. Since removing would add breaking changes, it will be removed in a 
  later feature release.
* Fixed a migration-related issue that was Django to create new migrations for
  the app.
* Fixed an issue where not all help text was marked for translation.


1.5.0 (05.10.2016)
------------------

* Updated FlatMenu listing in CMS to only show site column and filters if menus
  are defined for more than one site.
* Added the `fall_back_to_default_site_menus` option to the `flat_menu` tag, to
  allow flat menus defined for the default site to be used as fall-backs, in
  cases where the 'current' site doesn't have its own menus set up with the
  specified handle.
* Added a custom ValidationError to FlatMenu's `clean()` method that better
  handles the `unique_together` rule that applied to `site` and `handle`
  fields.
* Added the ability to copy/duplicate existing FlatMenu objects between sites
  (or to the same site with a different handle) via Wagtail's admin area. The
  'Copy' button appears in the listing for anyone with 'add' permission, and
  the view allows the user to make changes before anything is saved. 
* Apply `active` classes to menu items that link to custom URLs (if
  `request.path` and `link_url` are exact matches).
* Added a `handle` to `MenuItem` model to provide a string which can be 
  used to do specific matching of menu items in the template. (Tim Leguijt)


1.4.1 (02.10.2016) 
------------------

* Updated FlatMenu listing in CMS to include a column for `site`, a filter for
  `handle`, and a MenuItem count for each object. Also added default ordering,
  and output the handle value in a <code></code> tag to make it stand out.
* Made it easier to develop and debug wagtailmenus locally, by running it as a
  Django project. See CONTRIBUTING.md for instructions. 
* Added a `get_for_site` class method to the FlatMenu model, to be consistent 
  with the MainMenu model, and renamed the `for_site` method on MainMenu to
  `get_for_site` for consistency. `main_menu` and `flat_menu` tags now make use
  of these.
* Fixed an minor bug in the `prime_menu_items` method, where a `depth`
  value was hard-coded, instead of utilising the `SECTION_ROOT_LEVEL` setting. 


1.4.0 (22.09.2016)
------------------

* Added a `has_submenu_items()` method to `MenuPage` model to compliment
  `modify_submenu_items()` in version 1.3. Allows for far better control and 
  consistency when overriding `modify_submenu_items()` to add additional
  menu items for specific page types.
* Added a `sub_menu_template` option to `main_menu`, `section_menu`,
  `flat_menu` and `children_menu` that will be automatically picked up by the
  `sub_menu` tag and used as the template (if no `template` value is provided).
* Added a `fetch_specific_pages` option to all template tags, that if True,
  will used PageQuerySet's `specific()` method to return instances of the 
  most specific page-type model as menu items, instead of just vanilla `Page`
  objects.
* Added settings to allow default `fetch_specific_pages` value to be
  altered for each individual menu tag.
* If `fetch_specific_pages` is True, `prime_menu_items` will call the 
  `relative_url` method on the specific page to determine a menu item's `href`
  value, meaning overrides to that method will be respected.


1.3.1 (09.08.2016)
------------------

* Configured additional tox test environments for Wagtail>=1.6 with Django=1.9
  and 1.10.
* Extended the 'section matching by path' functionality added in 1.3.0 to
  also identify a 'current page' if the found page matches the exact path.
* Added further tests for path matching.
* Reduced the number of unnecessary calls to `Page.specific` in `menu_tags.py`
  where possible.


1.3.0 (06.08.2016)
------------------

* Added the ability for all menu tags to (attempt to) identify ancestor pages
  and section root page by using components from the request path when serving
  a custom URL (not routed via the page tree / served by `wagtail_serve`)
* Added `modify_submenu_items()` method to `MenuPage` model, which takes
  responsibility for modifying the initial menu_items list in `section_menu`
  and `sub_menu` tags. A DRYer approach, that is easier to extend/override to
  meet custom needs.
  

1.2.3 (25.07.2016)
------------------

* Added PyPi version and coveralls test coverage badges to README
* Altered Travis CI test configuration to use tox, allowing for much better
  control over test environments
* Added tests for Python 3.4 and 3.5 to confirm compatibility
* Added CONTRIBUTORS.rst


1.2.2 (06.07.2016)
------------------

 * Added this changelog :)
 * Added `WAGTAILMENUS_SECTION_ROOT_DEPTH` setting support, for more consistent identification of 'section root' pages


