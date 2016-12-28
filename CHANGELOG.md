Changelog
=========

2.X.X (XX.XX.XXX) IN DEVELOPMENT
-------------------------------- 


2.1.0 (28.12.2016)
-------------------------------- 

* Added official support for wagtail v1.8
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
-------------------------------- 

Fixed migration related issue raised by @urlsangel.


2.0.2 (08.12.2016)
-------------------------------- 

This release is broken and shouldn't be used. Skip to v2.0.3 instead.


2.0.1 (22.11.2016)
-------------------------------- 

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


