# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-05-03 20:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0019_auto_20190503_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='tipoplan',
            field=models.IntegerField(default=0),
        ),
    ]