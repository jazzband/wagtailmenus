# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailmenus', '0007_auto_20160131_2000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mainmenuitem',
            name='children_menu_link_text',
        ),
        migrations.RemoveField(
            model_name='mainmenuitem',
            name='repeat_in_children_menu',
        ),
        migrations.RemoveField(
            model_name='mainmenuitem',
            name='show_children_menu',
        ),
        migrations.AddField(
            model_name='flatmenuitem',
            name='url_append',
            field=models.CharField(max_length=255, verbose_name='Hash or querystring to append to URL', blank=True),
        ),
        migrations.AddField(
            model_name='mainmenuitem',
            name='add_subnav',
            field=models.BooleanField(default=True, verbose_name='Add sub-navigation for this page to allow access to children pages'),
        ),
        migrations.AddField(
            model_name='mainmenuitem',
            name='url_append',
            field=models.CharField(max_length=255, verbose_name='Hash or querystring to append to URL', blank=True),
        ),
        migrations.AlterField(
            model_name='flatmenuitem',
            name='link_text',
            field=models.CharField(help_text='Must be set if you wish to link to a custom URL.', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='link_text',
            field=models.CharField(help_text='Must be set if you wish to link to a custom URL.', max_length=255, blank=True),
        ),
    ]
