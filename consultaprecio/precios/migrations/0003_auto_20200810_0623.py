# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2020-08-10 06:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0002_auto_20200617_0726'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoriaPrecioProveedor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fechaLista', models.DateField()),
                ('codigoProveedor', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=200)),
                ('precioCompra', models.DecimalField(decimal_places=2, max_digits=6)),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='precios.Persona')),
            ],
        ),
        migrations.CreateModel(
            name='ProductoProveedor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('codigoProveedor', models.CharField(max_length=50)),
                ('descActualProveedor', models.CharField(max_length=200)),
                ('descAnteriorProveedor', models.CharField(max_length=200)),
                ('unidadCompra', models.CharField(max_length=30)),
                ('precioCompra', models.DecimalField(decimal_places=2, max_digits=6)),
                ('cantPorUnidadCompra', models.DecimalField(decimal_places=2, max_digits=5)),
                ('cantMinimaCompra', models.DecimalField(decimal_places=2, default=1, max_digits=6)),
                ('puntuacionCambio', models.IntegerField(default=0)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='precios.Producto')),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='precios.Persona')),
            ],
        ),
        migrations.AddIndex(
            model_name='productoproveedor',
            index=models.Index(fields=['proveedor', 'codigoProveedor'], name='precios_pro_proveed_409698_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='productoproveedor',
            unique_together=set([('proveedor', 'codigoProveedor')]),
        ),
        migrations.AddIndex(
            model_name='historiaprecioproveedor',
            index=models.Index(fields=['fechaLista', 'proveedor', 'codigoProveedor'], name='precios_his_fechaLi_b4c3d3_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='historiaprecioproveedor',
            unique_together=set([('fechaLista', 'proveedor', 'codigoProveedor')]),
        ),
    ]
