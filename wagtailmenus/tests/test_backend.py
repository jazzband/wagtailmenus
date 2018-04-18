from importlib import reload

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.test import (
    TestCase, TransactionTestCase, modify_settings, override_settings
)
from mock import call, patch

from django_webtest import WebTest
from wagtail import VERSION as WAGTAIL_VERSION
from wagtailmenus import (
    get_flat_menu_model, get_main_menu_model, wagtail_hooks
)
from wagtailmenus.panels import (
    FlatMenuItemsInlinePanel, MainMenuItemsInlinePanel
)
from wagtailmenus.tests.models import LinkPage

if WAGTAIL_VERSION >= (2, 0):
    from wagtail.admin.edit_handlers import ObjectList, InlinePanel
    from wagtail.core.models import Page, Site
else:
    from wagtail.wagtailadmin.edit_handlers import ObjectList, InlinePanel
    from wagtail.wagtailcore.models import Page, Site

FlatMenu = get_flat_menu_model()


class CMSUsecaseTests(WebTest):

    # optional: we want some initial data to be able to login
    fixtures = ['test.json']
    base_flatmenu_admin_url = '/admin/wagtailmenus/flatmenu/'
    base_mainmenu_admin_url = '/admin/wagtailmenus/mainmenu/'

    def setUp(self):
        get_user_model().objects._create_user(
            username='test1', email='test1@email.com', password='password',
            is_staff=True, is_superuser=True)

    def test_copy_footer_menu(self):
        # First check that there are 3 menus
        response = self.app.get(self.base_flatmenu_admin_url, user='test1')
        assert len(response.context['object_list']) == 3

        site_one = Site.objects.get(id=1)
        site_two = Site.objects.get(id=2)

        # Start by getting the footer menu for site one
        site_one_footer_menu = FlatMenu.get_for_site('footer', site_one)
        copy_view = self.app.get(
            '%scopy/%s/' % (self.base_flatmenu_admin_url, site_one_footer_menu.pk),
            user='test1')

        form = copy_view.forms[1]
        form['site'] = site_two.pk
        response = form.submit().follow()

        assert len(response.context['object_list']) == 4
        assert '<div class="changelist-filter col3">' in response

        # Let's just compare the two menu with the old one
        site_two_footer_menu = FlatMenu.get_for_site('footer', site_two)

        assert site_one_footer_menu.pk != site_two_footer_menu.pk
        assert site_one_footer_menu.heading == site_two_footer_menu.heading
        assert site_one_footer_menu.get_menu_items_manager().count() == site_two_footer_menu.get_menu_items_manager().count()

    def test_cannot_copy_footer_menu(self):
        site_one = Site.objects.get(id=1)
        site_two = Site.objects.get(id=2)
        # Start by getting the footer menu for site one
        site_one_footer_menu = FlatMenu.get_for_site('footer', site_one)
        # Create a new menu from the above one, for site two
        site_two_footer_menu = site_one_footer_menu
        site_two_footer_menu.id = None
        site_two_footer_menu.site = site_two
        site_two_footer_menu.save()

        # Refetche menu one
        site_one_footer_menu = FlatMenu.get_for_site('footer', site_one)

        copy_view = self.app.get(
            '%scopy/%s/' % (self.base_flatmenu_admin_url, site_one_footer_menu.pk),
            user='test1')
        form = copy_view.forms[1]
        form['site'] = site_two.pk
        response = form.submit()

        assert 'The flat menu could not be saved due to errors' in response
        assert 'Site and handle must create a unique combination.' in response

    def test_main_menu_save_success(self):
        edit_view = self.app.get(
            '%sedit/1/' % self.base_mainmenu_admin_url, user='test1')
        form = edit_view.forms[2]
        response = form.submit().follow()

        assert 'Main menu updated successfully.' in response


class LinkPageCMSTest(WebTest):

    # optional: we want some initial data to be able to login
    fixtures = ['test.json']
    csrf_checks = False
    parent_page_id = 5
    link_page_id = None

    def setUp(self):
        user = get_user_model().objects._create_user(
            username='test1', email='test1@email.com', password='password',
            is_staff=True, is_superuser=True)
        parent_page = Page.objects.get(id__exact=self.parent_page_id)
        link_page = LinkPage(
            content_type=ContentType.objects.get_for_model(LinkPage),
            owner=user,
            title='RKH Website',
            link_url='https://www.rkh.co.uk',
            url_append='#testing'
        )
        parent_page.add_child(instance=link_page)
        self.link_page_id = link_page.id

    def test_add_linkpage(self):
        response = self.app.get(
            '/admin/pages/add/tests/linkpage/%s/' % self.parent_page_id,
            user='test1')
        self.assertEqual(response.status_code, 200)

    def test_edit_linkpage(self):
        response = self.app.get(
            '/admin/pages/%s/edit/' % self.link_page_id,
            user='test1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="RKH Website"')

    def test_view_draft_linkpage(self):
        response = self.app.get(
            '/admin/pages/%s/view_draft/' % self.link_page_id,
            user='test1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This page redirects to: https://www.rkh.co.uk#testing')

    def test_view_draft_linkpage_to_page(self):
        # First, lets update the example LinkPage to link to a page instead of
        # a custom URL
        link_page = LinkPage.objects.get(id=self.link_page_id)
        link_page.link_url = ''
        link_page.link_page_id = self.parent_page_id
        link_page.save()
        response = self.app.get(
            '/admin/pages/%s/view_draft/' % self.link_page_id,
            user='test1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This page redirects to: http://www.wagtailmenus.co.uk:8000/#testing')


class TestSuperUser(TransactionTestCase):
    fixtures = ['test.json']

    def setUp(self):
        get_user_model().objects._create_user(
            username='test1', email='test1@email.com', password='password',
            is_staff=True, is_superuser=True)
        self.client.login(username='test1', password='password')

    def test_menupage_create(self):
        response = self.client.get('/admin/pages/add/tests/toplevelpage/5/')
        self.assertEqual(response.status_code, 200)

    def test_menupage_edit(self):
        response = self.client.get('/admin/pages/6/edit/')
        self.assertEqual(response.status_code, 200)

    def test_mainmenu_list(self):
        response = self.client.get('/admin/wagtailmenus/mainmenu/')
        self.assertRedirects(response, '/admin/wagtailmenus/mainmenu/edit/1/')

    @override_settings(WAGTAILMENUS_ADD_EDITOR_OVERRIDE_STYLES=False,)
    def test_mainmenu_edit(self):
        response = self.client.get('/admin/wagtailmenus/mainmenu/edit/1/')
        # Test 'get_error_message' method on view for additional coverage
        view = response.context['view']
        self.assertTrue(view.get_error_message())

        menu_model = get_main_menu_model()

        # Set 'panels' attribute on menu model to increase coverage for
        # MenuTabbedInterfaceMixin.get_edit_handler_class()
        menu_model.panels = menu_model.content_panels
        response = self.client.get('/admin/wagtailmenus/mainmenu/edit/1/')

        # Set 'edit_handler' attribute on menu model to increase coverage for
        # MenuTabbedInterfaceMixin.get_edit_handler_class()
        menu_model.edit_handler = ObjectList(menu_model.content_panels)
        response = self.client.get('/admin/wagtailmenus/mainmenu/edit/1/')

    def test_mainmenu_edit_multisite(self):
        Site.objects.create(
            id=3, hostname='test3.com', port=80, root_page_id=2,
            is_default_site=0, site_name="Test site 3")

        response = self.client.get(
            '/admin/wagtailmenus/mainmenu/edit/1/')
        self.assertEqual(response.status_code, 200)

        # If the site id in the URL and the site GET value are the same,
        # we shouldn't be redirect, because we're already where we need to be
        response = self.client.get(
            '/admin/wagtailmenus/mainmenu/edit/2/', {'site': 2})
        self.assertEqual(response.status_code, 200)

        # If the site id in the URL and the site GET value are different,
        # we should be redirected to the edit page for the site in GET
        response = self.client.get(
            '/admin/wagtailmenus/mainmenu/edit/2/', {'site': 3})
        self.assertRedirects(response, '/admin/wagtailmenus/mainmenu/edit/3/')

    def test_flatmenu_list(self):
        response = self.client.get('/admin/wagtailmenus/flatmenu/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<th scope="col"  class="sortable column-site">')
        self.assertNotContains(response, '<div class="changelist-filter col3">')

    def test_flatmenu_list_multisite(self):
        site_one = Site.objects.get(id=1)
        site_two = Site.objects.get(id=2)

        # Start by getting the footer menu for site one
        site_one_footer_menu = FlatMenu.get_for_site('footer', site_one)

        # Use menu one to create another for site two
        site_two_footer_menu = site_one_footer_menu
        site_two_footer_menu.site = site_two
        site_two_footer_menu.id = None
        site_two_footer_menu.save()

        # Redefine menu one, so that we definitely have two menus
        site_one_footer_menu = FlatMenu.get_for_site('footer', site_one)

        # Check the menus aren't the same
        self.assertNotEqual(site_one_footer_menu, site_two_footer_menu)

        # Check that the listing has changed to include the site column and
        # filters
        response = self.client.get('/admin/wagtailmenus/flatmenu/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<th scope="col"  class="sortable column-site">')
        self.assertContains(response, '<div class="changelist-filter col3">')

    @override_settings(WAGTAILMENUS_ADD_EDITOR_OVERRIDE_STYLES=False,)
    def test_flatmenu_edit(self):
        response = self.client.get(
            '/admin/wagtailmenus/flatmenu/edit/1/')
        self.assertEqual(response.status_code, 200)

    def test_flatmenu_copy(self):
        response = self.client.get(
            '/admin/wagtailmenus/flatmenu/copy/1/')
        self.assertEqual(response.status_code, 200)

    def test_panels_are_not_condensedinlinepanels(self):
        self.assertTrue(isinstance(FlatMenuItemsInlinePanel(), InlinePanel))
        self.assertTrue(isinstance(MainMenuItemsInlinePanel(), InlinePanel))

    """
    TODO: Uncomment once wagtail-condensedinlinepanel releases a Wagtail 2.0
    compatible version

    @modify_settings(INSTALLED_APPS={'append': 'condensedinlinepanel'})
    def test_panels_are_condensedinlinepanels(self):
        from condensedinlinepanel.edit_handlers import CondensedInlinePanel
        self.assertTrue(isinstance(FlatMenuItemsInlinePanel(), CondensedInlinePanel))
        self.assertTrue(isinstance(MainMenuItemsInlinePanel(), CondensedInlinePanel))
    """


class TestNonSuperUser(TransactionTestCase):
    fixtures = ['perms.json', 'test.json']

    def setUp(self):
        user = get_user_model().objects._create_user(
            username='test2', email='test2@email.com', password='password',
            is_staff=True, is_superuser=False)
        for group in Group.objects.all():
            if group.name == 'Testers':
                user.groups.add(group)
        # Login
        self.client.login(username='test2', password='password')

    def test_mainmenu_edit_denied(self):
        response = self.client.get('/admin/wagtailmenus/mainmenu/edit/1/')
        self.assertEqual(response.status_code, 403)


class TestDisablingMenusInWagtailCMS(TestCase):
    """
    Tests if modeladmin is registered based on settings.
    """
    @override_settings(
        WAGTAILMENUS_MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN=True,
        WAGTAILMENUS_FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN=True,
    )
    @patch('wagtail.contrib.modeladmin.options.modeladmin_register')
    def test_enabled_both_menus(self, mock_modeladmin_register):
        """
        Enabling both wagtailmenus should register both modeladmins.
        """
        reload(wagtail_hooks)
        self.assertIn(
            call(wagtail_hooks.MainMenuAdmin),
            mock_modeladmin_register.mock_calls)
        self.assertIn(
            call(wagtail_hooks.FlatMenuAdmin),
            mock_modeladmin_register.mock_calls)

    @override_settings(
        WAGTAILMENUS_MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN=False,
    )
    @patch('wagtail.contrib.modeladmin.options.modeladmin_register')
    def test_disable_main_menus(self, mock_modeladmin_register):
        """
        Disabling the 'Main menu' via setting should prevent registering the
        MainMenuAdmin.
        """
        reload(wagtail_hooks)
        self.assertNotIn(
            call(wagtail_hooks.MainMenuAdmin),
            mock_modeladmin_register.mock_calls)
        mock_modeladmin_register.assert_called_once_with(
            wagtail_hooks.FlatMenuAdmin)

    @override_settings(
        WAGTAILMENUS_FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN=False,
    )
    @patch('wagtail.contrib.modeladmin.options.modeladmin_register')
    def test_disable_flat_menus(self, mock_modeladmin_register):
        """
        Disabling the 'Flat menu' via setting should prevent registering the
        FlatMenuAdmin.
        """
        reload(wagtail_hooks)
        self.assertNotIn(
            call(wagtail_hooks.FlatMenuAdmin),
            mock_modeladmin_register.mock_calls)
        mock_modeladmin_register.assert_called_once_with(
            wagtail_hooks.MainMenuAdmin)
