# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import datetime

# Create your models here.

class MovimientoManager(models.Manager):
   def create_from_json(self, data):
      tipo_mov = TipoMovimiento.objects.get(id=data['tipo_movimiento'])
      user = User.objects.all()[0]
      mov = self.create(tipo_movimiento = tipo_mov,total = data['total'], fecha = datetime.date.today(), user = user);
      totalCompra = 0
      totalVenta = 0
      for item in data['items']:
         item['movimiento'] = mov.id
         producto = Producto.objects.filter(barcode=item['barcode'])[0]
         item['__tipo_movimiento'] = tipo_mov.codigo
         item['__precioVenta'] = producto.precioVenta
         item['__precioCompra'] = producto.precioCompra
         DetalleMovimiento.objects.create_from_json(item)
         precioCompra = producto.precioCompra
         precioVenta = producto.precioVenta
         if tipo_mov.codigo == 'VTA':
            precioVenta = item['precioVenta']
         totalCompra = totalCompra + (item['cantidad'] * precioCompra)
         totalVenta = totalVenta + (item['cantidad'] * precioVenta)
         if tipo_mov.factor != 0:
            
            producto.existencia = producto.existencia + (item['cantidad'] * tipo_mov.factor)
            producto.save()
      mov.totalCompra = totalCompra
      mov.totalVenta = totalVenta
      mov.save()
      return mov;

	  
class DetalleMovimientoManager(models.Manager):
   def create_from_json(self, data):
      movimiento = Movimiento.objects.get(id=data['movimiento'])
      tipo_movimiento = data['__tipo_movimiento']
      precioVenta = data['__precioVenta']
      precioCompra = data['__precioCompra']
      if tipo_movimiento == 'VTA':
         precioVenta = data['precioVenta']
	     
      print "movimiento "
      print movimiento
      det = self.create(movimiento = movimiento, barcode = data['barcode'], description = data['description'], cantidad = data['cantidad'], precioCompra = precioCompra, precioVenta = precioVenta)
      return det
	  
	  
class Producto (models.Model):
   id = models.AutoField(primary_key=True)
   barcode = models.CharField(max_length =30, unique=True)
   description = models.CharField(max_length=255)
   existencia = models.IntegerField(default=0)
   precioCompra = models.DecimalField(max_digits=5, decimal_places=2)
   precioVenta =models.DecimalField(max_digits=5, decimal_places=2)
   
   def as_dict(self):
      return {
	     'barcode': self.barcode,
		 'description':self.description,
		 'existencia':self.existencia,
		 'precioCompra':float(self.precioCompra),
		 'precioVenta':float(self.precioVenta)
	  
	  }

class TipoMovimiento (models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length =30, unique=True)
    description = models.CharField(max_length=255)
    factor = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    def __str__(self):
	 return self.description

class Movimiento (models.Model):
    id = models.AutoField(primary_key=True)
    tipo_movimiento = models.ForeignKey(TipoMovimiento)
    total = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    fecha =  models.DateTimeField(blank=False, null=False)
    user =  models.ForeignKey(User,null=True) 
    objects = MovimientoManager()
	  
class DetalleMovimiento (models.Model):
   id = models.AutoField(primary_key=True)
   movimiento = models.ForeignKey(Movimiento, on_delete=models.CASCADE)
   barcode = models.CharField(max_length =30)
   description = models.CharField(max_length=255)
   cantidad = models.IntegerField(default=0)
   precioCompra = models.DecimalField(default=0, max_digits=5, decimal_places=2)
   precioVenta =models.DecimalField(default=0, max_digits=5, decimal_places=2)
   objects = DetalleMovimientoManager()
   
   def as_dict(self):
      return {
	     'barcode': self.barcode,
		 'description':self.description,
		 'cantidad':self.cantidad,
		 'precioCompra':float(self.precioCompra),
		 'precioVenta':float(self.precioVenta)
	  
	  }	  