Changelog
=========

1.5.2 (XX.XX.XXX) IN DEVELOPMENT
---------------------------------

* Wait and see!


1.5.1 (10.10.2016) 
---------------------------------

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


