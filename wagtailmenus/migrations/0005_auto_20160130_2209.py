# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailmenus', '0004_auto_20160130_0024'),
    ]

    operations = [
        migrations.AddField(
            model_name='flatmenuitem',
            name='url_append',
            field=models.CharField(help_text="e.g. '?abc=xyz' or '#tab-contact'", max_length=255, verbose_name='hash or querystring to append to URL', blank=True),
        ),
        migrations.AddField(
            model_name='mainmenuitem',
            name='url_append',
            field=models.CharField(help_text="e.g. '?abc=xyz' or '#tab-contact'", max_length=255, verbose_name='hash or querystring to append to URL', blank=True),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='children_menu_link_text',
            field=models.CharField(help_text="e.g. 'Overview' or 'Section home'. If left blank, the page title will be used.", max_length=255, verbose_name='Link text for sub-menu item', blank=True),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='show_children_menu',
            field=models.BooleanField(default=True, verbose_name='Add a sub-menu for children of this page'),
        ),
    ]
