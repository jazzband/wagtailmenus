# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailmenus', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainmenuitem',
            name='children_menu_link_text',
            field=models.CharField(help_text='If left blank, the same link text will be used.', max_length=255, verbose_name='Link text for children menu link', blank=True),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='repeat_in_children_menu',
            field=models.BooleanField(help_text="A menu item with children automatically becomes a toggle for accessing the pages below it. Repeating the link in it's children menu allows the page to remain accessible via the main navigation.", verbose_name='Repeat this page in the children menu?'),
        ),
    ]
