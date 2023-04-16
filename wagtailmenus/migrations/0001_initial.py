# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0023_alter_page_revision_on_delete_behaviour'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlatMenu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='For internal reference only.', max_length=255)),
                ('handle', models.SlugField(help_text='Used in to reference this menu in templates etc. Must be unique for the selected site.', max_length=100)),
                ('heading', models.CharField(help_text='If supplied, appears above the menu when displayed on the on the front-end of the site.', max_length=255, blank=True)),
                ('site', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='flat_menus', to='wagtailcore.Site', verbose_name='site')),
            ],
            options={
                'verbose_name': 'flat menu',
                'verbose_name_plural': 'flat menus',
            },
        ),
        migrations.CreateModel(
            name='FlatMenuItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('link_text', models.CharField(help_text="If left blank, the page name will be used. Must be set if you're linking to a custom URL.", max_length=255, blank=True)),
                ('link_url', models.URLField(null=True, verbose_name='Link to a custom URL', blank=True)),
                ('link_page', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='+', verbose_name='Link to an internal page', blank=True, to='wagtailcore.Page', null=True)),
                ('menu', modelcluster.fields.ParentalKey(on_delete=models.deletion.CASCADE, related_name='menu_items', to='wagtailmenus.FlatMenu')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MainMenu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='main_menu', to='wagtailcore.Site')),
            ],
            options={
                'verbose_name': 'main menu',
                'verbose_name_plural': 'main menu',
            },
        ),
        migrations.CreateModel(
            name='MainMenuItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('link_text', models.CharField(help_text="If left blank, the page name will be used. Must be set if you're linking to a custom URL.", max_length=255, blank=True)),
                ('link_url', models.URLField(null=True, verbose_name='Link to a custom URL', blank=True)),
                ('show_children_menu', models.BooleanField(default=True, help_text='The children menu will only appear if this menu item links to a page, and that page has children that are set to appear in menus.', verbose_name='Show a children menu for this item?')),
                ('repeat_in_children_menu', models.BooleanField(help_text="A menu item with children automatically becomes a toggle for accessing the pages below it. Repeating the link in it's children menu allows the page to remain accessible via the main navigation.", verbose_name='Repeat a link to this page in the children menu?')),
                ('children_menu_link_text', models.CharField(help_text='If left blank, the menu item text will be repeated.', max_length=255, verbose_name='Link text for children menu link', blank=True)),
                ('link_page', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='+', verbose_name='Link to an internal page', blank=True, to='wagtailcore.Page', null=True)),
                ('menu', modelcluster.fields.ParentalKey(on_delete=models.deletion.CASCADE, related_name='menu_items', to='wagtailmenus.MainMenu')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='flatmenu',
            unique_together=set([('site', 'handle')]),
        ),
    ]
