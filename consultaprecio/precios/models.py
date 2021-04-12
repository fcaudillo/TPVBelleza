# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import datetime
from django.db.models.signals import post_save, post_init
from django.apps import apps
from decimal import Decimal

miapp = apps.get_app_config('precios')

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
         producto = Producto.objects.filter(codigoInterno=item['codigointerno'])[0]

         print 'MovimientoManager', tipo_mov
         
         if tipo_mov.codigo == 'VTA':
            producto.existencia = producto.existencia + (Decimal(item['cantidad']) * tipo_mov.factor)
            producto.save()

         if tipo_mov.codigo != 'VTA':
           producto.precioVenta = item['precioVenta']
           producto.precioCompra = item['precioCompra']
           producto.ubicacion = item['ubicacion']
           producto.description = item['description']
           producto.existencia = producto.existencia + (Decimal(item['cantidad']) * tipo_mov.factor)
           if tipo_mov.codigo == 'MOD':
             producto.existencia = item['cantidad']
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
      precioVenta = data['precioVenta']
      precioCompra = data['precioCompra']
      det = self.create(movimiento = movimiento, barcode = data['codigointerno'], description = data['description'], cantidad = data['cantidad'], precioCompra = precioCompra, precioVenta = precioVenta)
      return det

class Configuracion(models.Model):
    id = models.AutoField(primary_key=True)
    clave = models.CharField(max_length=30, blank=False, null=False,  default='')
    valor = models.CharField(max_length=300, default='')
    previous_valor = None

    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if instance.previous_valor != instance.valor or created:
           miapp.refreshConfiguracion()
           print ("Hubo un cambio en la configuracion") 

    @staticmethod
    def remember_valor(sender, **kwargs):
        instance = kwargs.get('instance')
        instance.previous_valor = instance.valor

    def __str__(self):
       return '%s : %s' % (self.clave,self.valor) 

    class Meta:
       managed = False
       db_table = 'precios_configuracion' 

post_save.connect(Configuracion.post_save,sender=Configuracion)
post_init.connect(Configuracion.remember_valor,sender=Configuracion)

class Compania(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=5, default='')
    description = models.CharField(max_length=255)
    imagen = models.CharField(max_length=50)
    comision = models.IntegerField(default=0)
    def __str__(self):
      return 'codigo : %s, descripcion: %s, imagen  : %s \n ' % (self.codigo,self.description, self.imagen)

    class Meta:
       managed = False
       db_table = 'precios_compania' 


class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=5, default='')
    description = models.CharField(max_length=255)
    parent = models.ForeignKey('self',models.SET_NULL, blank=True, null=True)
    def __str__(self):
      return 'codigo: %s, descripcion: %s \n ' % (self.codigo, self.description)

    class Meta:
       managed = False
       db_table = 'precios_categoria' 


class Persona(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=8, default='')
    description = models.CharField(max_length=255)
    es_persona_moral = models.BooleanField(default=False);
    es_proveedor = models.BooleanField(default=False)
    es_cliente = models.BooleanField(default=False) 
    def __str__(self):
      return 'codigo: %s, descripcion: %s \n ' % (self.codigo, self.description)

    class Meta:
       managed = False
       db_table = 'precios_persona' 


class Producto (models.Model):
   id = models.AutoField(primary_key=True)
   codigoInterno = models.CharField(max_length=20, unique=True)
   codigoProveedor = models.CharField(max_length=50)
   barcode = models.CharField(max_length =30, unique=False)
   persona = models.ForeignKey(Persona, models.SET_NULL, blank=True, null=True)
   description = models.CharField(max_length=255)
   descriptionCorta = models.CharField(max_length=255)
   existencia = models.IntegerField(default=0)
   minimoexist = models.IntegerField(default=0)
   maximoexist = models.IntegerField(default=0)
   precioCompra = models.DecimalField(max_digits=5, decimal_places=2)
   precioVenta =models.DecimalField(max_digits=5, decimal_places=2)
   ubicacion = models.CharField(max_length=255, default='')
   categoria = models.ForeignKey(Categoria,models.SET_NULL, blank=True, null=True)
   unidadVenta = models.CharField(max_length=30)
   falta =  models.DateTimeField(blank=False, null=False)
   fmodificacion =  models.DateTimeField(blank=True, null=True)
   puede_venderse = models.BooleanField(default=True)

   @staticmethod 
   def findByBarcode(codigo):
     return Producto.objects.filter(barcode = codigo)[0]

   @staticmethod
   def findByCodigoInterno(codigo):
     return Producto.objects.filter(codigoInterno = codigo)[0]

   def __str__(self):
    return 'barcode: %s, descricion: %s, existencia :  %d, precioCompra : %f, precioVenta: %f, minimoexist: %d, maximoexist: %d, codigoprov: %s, ubicacion: %s \n' % (self.barcode, self.description, self.existencia, self.precioCompra, self.precioVenta, self.minimoexist, self.maximoexist, self.codigoproveedor, self.ubicacion)
   
   def as_dict(self):
      return {
             'codigointerno': self.codigoInterno,
	     'barcode': self.barcode,
             'codigoProveedor': self.codigoProveedor,
             'proveedor': self.persona.codigo,
		 'description':self.description,
		 'existencia':self.existencia,
                 'ubicacion': self.ubicacion,
		 'precioCompra':float(self.precioCompra),
		 'precioVenta':float(self.precioVenta)
	  
	  }

   class Meta:
       managed = False
       db_table = 'precios_producto' 



class ProductoProveedor(models.Model):
   id = models.AutoField(primary_key=True)
   proveedor = models.ForeignKey(Persona, null=False) 
   producto = models.ForeignKey(Producto, null=False)
   codigoProveedor = models.CharField(max_length=50, null=False)
   descActualProveedor = models.CharField(max_length=200)
   descAnteriorProveedor = models.CharField(max_length=200)
   unidadCompra = models.CharField(max_length=30)
   precioCompra = models.DecimalField(max_digits=6, decimal_places=2)
   cantPorUnidadCompra =  models.DecimalField(max_digits=5, decimal_places=2)
   cantMinimaCompra = models.DecimalField(max_digits=6, decimal_places=2,default=1)
   puntuacionCambio = models.IntegerField(default=0)
   
   class Meta:
      unique_together = (('proveedor','codigoProveedor')),
      indexes = [
          models.Index(fields=['proveedor','codigoProveedor']),
      ]


class HistoriaPrecioProveedor(models.Model):
   id = models.AutoField(primary_key=True)
   fechaLista = models.DateField(blank=False, null=False)
   proveedor = models.ForeignKey(Persona, null=False) 
   codigoProveedor = models.CharField(max_length=50,null=False)
   descripcion = models.CharField(max_length=200,null=False)
   caja = models.DecimalField(max_digits=6, decimal_places=2, null = True)
   unidad = models.CharField(max_length=30, null=True)
   alta_rotacion = models.DecimalField(max_digits=2, decimal_places=0, null = True)
   codigobarras = models.CharField(max_length=30, null=True)
   precioCompra = models.DecimalField(max_digits=6, decimal_places=2, default=0)
   precioMayoreo = models.DecimalField(max_digits=6, decimal_places=2, default=0)
   precioPublico = models.DecimalField(max_digits=6, decimal_places=2, default=0)
   
   class Meta:
      unique_together = (('fechaLista','proveedor','codigoProveedor')),
      indexes = [
          models.Index(fields=['fechaLista','proveedor','codigoProveedor']),
      ]


class Plan(models.Model):
   id = models.AutoField(primary_key=True)
   plan = models.CharField(max_length=20, default='')
   description = models.CharField(max_length=255)
   monto = models.IntegerField(default=0)
   tipoplan = models.IntegerField(default=0)
   compania = models.ForeignKey(Compania,models.SET_NULL,blank=True, null=True)
   producto = models.ForeignKey(Producto,models.SET_NULL,blank=True, null=True) 

   def __str__(self):
    return 'plan: %s, descripcion: %s, monto :  %d, tipoplan : %d, compania: %s \n' % (self.plan, self.description, self.monto, self.tipoplan, self.compania.codigo)

   class Meta:
       managed = False
       db_table = 'precios_plan' 

class Recarga(models.Model):
    id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(Plan, models.SET_NULL,blank=True, null=True)
    celular =  models.CharField(max_length=20, default='', blank=True, null=True)
    monto = models.IntegerField(default=0)
    falta = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    estatus = models.CharField(max_length=20, default='EN PROCESO')
    error = models.CharField(max_length=1024, default='')
    codigoautorizacion = models.CharField(max_length=30, default='')

    def __str__(self):
      return 'plan: %s, celular: %s, monto: %d, estatus: %s, error: %s, codigoautorizacion: %s \n' % (self.plan.description, self.celular, self.monto, self.estatus,self.error, self.codigoautorizacion)
 
    class Meta:
       managed = False
       db_table = 'precios_recarga' 

class TipoMovimiento (models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length =30, unique=True)
    description = models.CharField(max_length=255)
    factor = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    factor_conta = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    prioridad = models.DecimalField(default=0, max_digits=2, decimal_places=0)
    def __str__(self):
	 return 'Codigo : %s, Descripcion : %s, factor: %f, factor_conta:  %f, prioridad : %d \n' % (self.codigo, self.description, self.factor, self.factor_conta, self.prioridad)

    class Meta:
       managed = False
       db_table = 'precios_tipomovimiento' 

class Movimiento (models.Model):
    id = models.AutoField(primary_key=True)
    tipo_movimiento = models.ForeignKey(TipoMovimiento)
    description = models.CharField(max_length=255)
    total = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    fecha =  models.DateTimeField(blank=False, null=False)
    user =  models.ForeignKey(User,on_delete=models.SET_NULL, null=True) 
    objects = MovimientoManager()

    def __str__(self):
      items = list(DetalleMovimiento.objects.filter(movimiento = self.id))
      detalle = ''
      for item in items:
         detalle = detalle + str(item) 
      
      return 'id : %d, username: %s , Tipo Mov: %s , total : %f, descripcion: %s fecha: %s \n Detalle: \n %s' % (self.id, self.user.username, self.tipo_movimiento.description, self.total, self.description, self.fecha, detalle)

    def as_dict_tpv(self):
       mov = {
                'tipo_movimiento': self.tipo_movimiento.codigo,
                'descripcion' : self.description,
                'total' : float(self.total),
                'fecha' : self.fecha.strftime('%d/%m/%Y %H:%M:%S'),
                'usuario': self.user.username,
                'detalle': []
             }
       items = list(DetalleMovimiento.objects.filter(movimiento = self.id))
       detalle = mov['detalle']
       for item in items:
         detalle.append(item.as_dict_tpv()) 
       return mov

    class Meta:
       managed = False
       db_table = 'precios_movimiento' 

	  
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

   class Meta:
       managed = False
       db_table = 'precios_detallemovimiento' 

   def as_dict_tpv(self):
      return {
		 'description':self.description,
		 'cantidad':float(self.cantidad),
		 'precioVenta':float(self.precioVenta)
	     }	  


