# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import datetime

# Create your models here.

class MovimientoManager(models.Manager):
   def create_from_json(self, data, current_user):
      tipo_mov = TipoMovimiento.objects.get(id=data['tipo_movimiento'])
      user = current_user
      mov = self.create(tipo_movimiento = tipo_mov,total = data['total'], description = data['descripcion'],  fecha = datetime.datetime.today(), user = user);
      totalCompra = 0
      totalVenta = 0
      for item in data['items']:
         item['movimiento'] = mov.id
         producto = Producto.objects.filter(barcode=item['barcode'])[0]

         print 'MovimientoManager', tipo_mov
         
         if tipo_mov.codigo == 'VTA':
            producto.existencia = producto.existencia + (item['cantidad'] * tipo_mov.factor)
            producto.save()

         if tipo_mov.codigo != 'VTA':
           producto.precioVenta = item['precioVenta']
           producto.precioCompra = item['precioCompra']
           producto.ubicacion = item['ubicacion']
           producto.description = item['description']
           producto.existencia = producto.existencia + (item['cantidad'] * tipo_mov.factor)
           print "Existencia actual ", producto.existencia
           producto.save()
           print "Guardo el producto"
            

         item['__tipo_movimiento'] = tipo_mov.codigo
         DetalleMovimiento.objects.create_from_json(item)
         
      return mov;

	  
class DetalleMovimientoManager(models.Manager):
   def create_from_json(self, data):
      print "detalle movimiento save"
      print data
      movimiento = Movimiento.objects.get(id=data['movimiento'])
      tipo_movimiento = data['__tipo_movimiento']
      precioVenta = data['cantidad'] * data['precioVenta']
      precioCompra = data['cantidad'] * data['precioCompra']
      det = self.create(movimiento = movimiento, barcode = data['barcode'], description = data['description'], cantidad = data['cantidad'], precioCompra = precioCompra, precioVenta = precioVenta)
      return det



class Compania(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=5, default='')
    description = models.CharField(max_length=255)
    imagen = models.CharField(max_length=50)
    comision = models.IntegerField(default=0)

class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=5, default='')
    description = models.CharField(max_length=255)
    parent = models.ForeignKey('self',models.SET_NULL, blank=True, null=True)

class Producto (models.Model):
   id = models.AutoField(primary_key=True)
   barcode = models.CharField(max_length =30, unique=True)
   codigoproveedor = models.CharField(max_length = 40,default='')
   description = models.CharField(max_length=255)
   existencia = models.IntegerField(default=0)
   minimoexist = models.IntegerField(default=0)
   maximoexist = models.IntegerField(default=0)
   precioCompra = models.DecimalField(max_digits=5, decimal_places=2)
   precioVenta =models.DecimalField(max_digits=5, decimal_places=2)
   ubicacion = models.CharField(max_length=255)
   categoria = models.ForeignKey(Categoria,models.SET_NULL, blank=True, null=True)
   falta =  models.DateTimeField(blank=False, null=False)
   fmodificacion =  models.DateTimeField(blank=True, null=True)

   @staticmethod 
   def findByBarcode(codigo):
     return Producto.objects.filter(barcode = codigo)[0]

   def __str__(self):
    return 'barcode: %s, descricion: %s, existencia :  %d, precioCompra : %f, precioVenta: %f, minimoexist: %d, maximoexist: %d, codigoprov: %s, ubicacion: %s \n' % (self.barcode, self.description, self.existencia, self.precioCompra, self.precioVenta, self.minimoexist, self.maximoexist, self.codigoproveedor, self.ubicacion)
   
   def as_dict(self):
      return {
	     'barcode': self.barcode,
		 'description':self.description,
		 'existencia':self.existencia,
                 'ubicacion': self.ubicacion,
		 'precioCompra':float(self.precioCompra),
		 'precioVenta':float(self.precioVenta)
	  
	  }


class Plan(models.Model):
   id = models.AutoField(primary_key=True)
   plan = models.CharField(max_length=20, default='')
   description = models.CharField(max_length=255)
   monto = models.IntegerField(default=0)
   tipoplan = models.IntegerField(default=0)
   compania = models.ForeignKey(Compania,models.SET_NULL,blank=True, null=True)
   producto = models.ForeignKey(Producto,models.SET_NULL,blank=True, null=True) 

class Recarga(models.Model):
    id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(Plan, models.SET_NULL,blank=True, null=True)
    celular =  models.CharField(max_length=20, default='', blank=True, null=True)
    monto = models.IntegerField(default=0)
    falta = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    estatus = models.CharField(max_length=20, default='EN PROCESO')
    error = models.CharField(max_length=1024, default='')
    codigoautorizacion = models.CharField(max_length=30, default='')
 

class TipoMovimiento (models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length =30, unique=True)
    description = models.CharField(max_length=255)
    factor = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    factor_conta = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    prioridad = models.DecimalField(default=0, max_digits=2, decimal_places=0)
    def __str__(self):
	 return 'Codigo : %s, Descripcion : %s, factor: %f \n' % (self.codigo, self.description, self.factor)

class Movimiento (models.Model):
    id = models.AutoField(primary_key=True)
    tipo_movimiento = models.ForeignKey(TipoMovimiento)
    description = models.CharField(max_length=255)
    total = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    fecha =  models.DateTimeField(blank=False, null=False)
    user =  models.ForeignKey(User,on_delete=models.SET_NULL, null=True) 
    objects = MovimientoManager()

    def __str__(self):
      items = list(DetalleMovimiento.objects.filter(movimiento = self.id))
      detalle = ''
      for item in items:
         detalle = detalle + str(item) 
      
      return 'id : %d, username: %s , Tipo Mov: %s , total : %f, descripcion: %s fecha: %s \n Detalle: \n %s' % (self.id, self.user.username, self.tipo_movimiento.description, self.total, self.description, self.fecha, detalle)
	  
class DetalleMovimiento (models.Model):
   id = models.AutoField(primary_key=True)
   movimiento = models.ForeignKey(Movimiento, on_delete=models.CASCADE)
   barcode = models.CharField(max_length =30)
   description = models.CharField(max_length=255)
   cantidad = models.IntegerField(default=0)
   precioCompra = models.DecimalField(default=0, max_digits=5, decimal_places=2)
   precioVenta =models.DecimalField(default=0, max_digits=5, decimal_places=2)
   objects = DetalleMovimientoManager()

   def __str__(self):
     return '   barcode : %s , description : %s, cantidad : %f, precioCompra : %f, precioVenta : %f \n ' % (self.barcode, self.description, self.cantidad, self.precioCompra, self.precioVenta)
   
   def as_dict(self):
      return {
	     'barcode': self.barcode,
		 'description':self.description,
		 'cantidad':self.cantidad,
		 'precioCompra':float(self.precioCompra),
		 'precioVenta':float(self.precioVenta)
	  
	  }	  
