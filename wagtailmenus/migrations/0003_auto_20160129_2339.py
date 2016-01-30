# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailmenus', '0002_auto_20160129_0901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flatmenu',
            name='handle',
            field=models.SlugField(help_text='Used to reference this menu in templates etc. Must be unique for the selected site.', max_length=100),
        ),
        migrations.AlterField(
            model_name='flatmenu',
            name='heading',
            field=models.CharField(help_text='If supplied, appears above the menu when rendered.', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='flatmenuitem',
            name='link_text',
            field=models.CharField(help_text='If left blank, the page title will be used. Must be set if you wish to link to a custom URL.', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='flatmenuitem',
            name='link_url',
            field=models.CharField(max_length=255, null=True, verbose_name='Link to a custom URL', blank=True),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='children_menu_link_text',
            field=models.CharField(help_text='e.g. Overview. If left blank, the page title will be used.', max_length=255, verbose_name='Link text for sub-menu item', blank=True),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='link_text',
            field=models.CharField(help_text='If left blank, the page title will be used. Must be set if you wish to link to a custom URL.', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='link_url',
            field=models.CharField(max_length=255, null=True, verbose_name='Link to a custom URL', blank=True),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='repeat_in_children_menu',
            field=models.BooleanField(default=True, verbose_name='Include a link to this page in the sub-menu'),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='show_children_menu',
            field=models.BooleanField(default=True, verbose_name='Add a sub-menu for children of this page'),
        ),
    ]
