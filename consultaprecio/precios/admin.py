# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from precios.models import Categoria, TipoMovimiento

# Register your models here.
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
   list_display = ['description']

@admin.register(TipoMovimiento)
class TipoMovimientoAdmin(admin.ModelAdmin):
   list_display = ('codigo','description','factor')
