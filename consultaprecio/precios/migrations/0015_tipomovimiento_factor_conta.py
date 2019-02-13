# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-12 23:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0014_tipomovimiento_prioridad'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipomovimiento',
            name='factor_conta',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]