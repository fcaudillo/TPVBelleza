# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-07 21:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0003_auto_20180306_2237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movimiento',
            name='usuario',
        ),
        migrations.AlterField(
            model_name='movimiento',
            name='fecha',
            field=models.DateTimeField(),
        ),
    ]
