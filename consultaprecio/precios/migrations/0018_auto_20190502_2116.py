# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-05-02 21:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0017_recarga'),
    ]

    operations = [
        migrations.AddField(
            model_name='recarga',
            name='celular',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='recarga',
            name='estatus',
            field=models.CharField(default='EN PROCESO', max_length=20),
        ),
    ]