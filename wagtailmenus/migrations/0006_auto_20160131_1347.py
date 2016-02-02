# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailmenus', '0005_auto_20160130_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flatmenuitem',
            name='url_append',
            field=models.CharField(help_text="e.g. '#about-section', '#tab-contact' or '?abc=xyz'", max_length=255, verbose_name='hash or querystring to append to URL', blank=True),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='children_menu_link_text',
            field=models.CharField(help_text="e.g. 'Section home' or 'Overview'. If left blank, the page title will be used.", max_length=255, verbose_name='Link text for sub-menu item', blank=True),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='url_append',
            field=models.CharField(help_text="e.g. '#about-section', '#tab-contact' or '?abc=xyz'", max_length=255, verbose_name='hash or querystring to append to URL', blank=True),
        ),
    ]
