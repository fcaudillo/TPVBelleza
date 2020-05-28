# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-06-12 17:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0023_auto_20190523_1852'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='categoria',
            table='precios_categoria',
        ),
        migrations.AlterModelTable(
            name='compania',
            table='precios_compania',
        ),
        migrations.AlterModelTable(
            name='configuracion',
            table='precios_configuracion',
        ),
        migrations.AlterModelTable(
            name='detallemovimiento',
            table='precios_detallemovimiento',
        ),
        migrations.AlterModelTable(
            name='movimiento',
            table='precios_movimiento',
        ),
        migrations.AlterModelTable(
            name='plan',
            table='precios_plan',
        ),
        migrations.AlterModelTable(
            name='producto',
            table='precios_producto',
        ),
        migrations.AlterModelTable(
            name='recarga',
            table='precios_recarga',
        ),
        migrations.AlterModelTable(
            name='tipomovimiento',
            table='precios_tipomovimiento',
        ),
    ]