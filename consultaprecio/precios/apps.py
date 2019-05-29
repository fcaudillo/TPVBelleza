# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connection

from django.apps import AppConfig


class PreciosConfig(AppConfig):
    name = 'precios'
    def ready(self):
      self.configuracion = dict()
      all_tables = connection.introspection.table_names()
      if 'precios_configuracion' in all_tables:
        print ("Existe precios_configuracion in alltables")
        self.refreshConfiguracion()

    def getConfiguracion(self):
      return self.configuracion

    def refreshConfiguracion(self):
      from precios.models import Configuracion
      lista = list(Configuracion.objects.all())
      self.configuracion = dict((a.clave,a.valor) for a in lista)
      print ("Cargando configuracion")
