# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-31 23:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0010_auto_20190109_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movimiento',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
