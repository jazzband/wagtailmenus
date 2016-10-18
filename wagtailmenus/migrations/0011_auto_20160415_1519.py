# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailmenus', '0010_auto_20160201_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flatmenuitem',
            name='url_append',
            field=models.CharField(help_text="Use this to optionally append a #hash or querystring to the above page's URL.", max_length=255, verbose_name='Append to URL', blank=True),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='url_append',
            field=models.CharField(help_text="Use this to optionally append a #hash or querystring to the above page's URL.", max_length=255, verbose_name='Append to URL', blank=True),
        ),
    ]
