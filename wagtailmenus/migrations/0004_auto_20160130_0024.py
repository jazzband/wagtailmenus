# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailmenus', '0003_auto_20160129_2339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainmenuitem',
            name='repeat_in_children_menu',
            field=models.BooleanField(default=False, verbose_name='Include a link to this page in the sub-menu'),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='show_children_menu',
            field=models.BooleanField(default=False, verbose_name='Add a sub-menu for children of this page'),
        ),
    ]
