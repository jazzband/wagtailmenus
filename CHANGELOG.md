Changelog
=========

1.4.1 (XX.XX.XXXX) IN DEVELOPMENT
---------------------------------

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
---------------------------------

* Configured additional tox test environments for Wagtail>=1.6 with Django=1.9
  and 1.10.
* Extended the 'section matching by path' functionality added in 1.3.0 to
  also identify a 'current page' if the found page matches the exact path.
* Added further tests for path matching.
* Reduced the number of unnecessary calls to `Page.specific` in `menu_tags.py`
  where possible.

1.3.0 (06.08.2016)
---------------------------------

* Added the ability for all menu tags to (attempt to) identify ancestor pages
  and section root page by using components from the request path when serving
  a custom URL (not routed via the page tree / served by `wagtail_serve`)
* Added `modify_submenu_items()` method to `MenuPage` model, which takes
  responsibility for modifying the initial menu_items list in `section_menu`
  and `sub_menu` tags. A DRYer approach, that is easier to extend/override to
  meet custom needs.
  

1.2.3 (25.07.2016)
---------------------------------

* Added PyPi version and coveralls test coverage badges to README
* Altered Travis CI test configuration to use tox, allowing for much better
  control over test environments
* Added tests for Python 3.4 and 3.5 to confirm compatibility
* Added CONTRIBUTORS.rst


1.2.2 (06.07.2016)
------------------

 * Added this changelog :)
 * Added `WAGTAILMENUS_SECTION_ROOT_DEPTH` setting support, for more consistent identification of 'section root' pages


