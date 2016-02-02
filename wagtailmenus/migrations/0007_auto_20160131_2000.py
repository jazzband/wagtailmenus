# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailmenus', '0006_auto_20160131_1347'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flatmenuitem',
            name='url_append',
        ),
        migrations.RemoveField(
            model_name='mainmenuitem',
            name='url_append',
        ),
        migrations.AlterField(
            model_name='flatmenuitem',
            name='link_page',
            field=models.ForeignKey(verbose_name='Link to an internal page', blank=True, to='wagtailcore.Page', null=True),
        ),
        migrations.AlterField(
            model_name='mainmenuitem',
            name='link_page',
            field=models.ForeignKey(verbose_name='Link to an internal page', blank=True, to='wagtailcore.Page', null=True),
        ),
    ]
