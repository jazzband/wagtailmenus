Changelog
=========

1.3.0 (xx.xx.xx) IN DEVELOPMENT
---------------------------------

* Added `modify_submenu_items()` method to `MenuPage` model, which takes
  responsibility for modifying the initial menu_items list in `section_menu`
  and `sub_menu` tags. A DRYer approach, that is easily extend/override to
  meet custom needs.
  

1.2.3 (25.07.2016)
---------------------------------

* Added PyPi version and coveralls test coverage badges to README
* Altered travis CI test configuration to use tox, allowing for much better
  control over test environments
* Added tests for Python 3.4 and 3.5 to confirm compatibility
* Added CONTRIBUTORS.rst


1.2.2 (06.07.2016)
------------------

 * Added this changelog :)
 * Added `WAGTAILMENUS_SECTION_ROOT_DEPTH` setting support, for more consistent identification of 'section root' pages


