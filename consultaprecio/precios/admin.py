# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from precios.models import Categoria, TipoMovimiento, Compania, Plan, Configuracion,Persona 

# Register your models here.
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
   list_display = ['description']

@admin.register(Compania)
class CompaniaAdmin(admin.ModelAdmin):
  list_display = ('codigo','description','imagen','comision')


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
  list_display = ('codigo','description')

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
  list_display = ('plan','description','monto','compania','producto')

@admin.register(TipoMovimiento)
class TipoMovimientoAdmin(admin.ModelAdmin):
   list_display = ('codigo','description','factor','factor_conta','prioridad')

@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
   list_display = ('clave','valor')
