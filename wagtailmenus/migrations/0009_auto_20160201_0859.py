# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailmenus', '0008_auto_20160131_2327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainmenuitem',
            name='add_subnav',
            field=models.BooleanField(default=True, verbose_name='Allow sub-navigation for this page'),
        ),
    ]
