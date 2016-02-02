# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailmenus', '0009_auto_20160201_0859'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mainmenuitem',
            old_name='add_subnav',
            new_name='allow_subnav',
        ),
    ]
