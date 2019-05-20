# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class PreciosConfig(AppConfig):
    name = 'precios'
    def ready(self):
      self.configuracion = None
      self.refreshConfiguracion()

    def getConfiguracion(self):
      return self.configuracion

    def refreshConfiguracion(self):
      from precios.models import Configuracion
      lista = list(Configuracion.objects.all())
      self.configuracion = dict((a.clave,a.valor) for a in lista)
      print ("Cargando configuracion")
