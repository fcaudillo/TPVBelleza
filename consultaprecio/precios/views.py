# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
import json
from django.views.generic import TemplateView
from django.views.generic import View
from precios.models import Producto
from django.core.serializers import serialize
import xlrd
import json
from precios.models import TipoMovimiento, Movimiento

# Create your views here.

def find_consulta(request,barcode):
   print 'saludos 3'
   productos = list(Producto.objects.filter(barcode=barcode))
   if len(productos) == 0:
      return HttpResponse(status=204)
   pr = productos[0]
   return HttpResponse(json.dumps(pr.as_dict()), content_type='application/json')  

def find_all(request): 
   productos = list(Producto.objects.all())
   result = [ obj.as_dict() for obj in productos ]
   return HttpResponse(json.dumps(result), content_type='application/json')   


def guarda_ticket(request):
   print "Guardar Tickets"
   if request.method=='POST':
     received_json_data=json.loads(request.body)
     print received_json_data
     print "saludos"
     Movimiento.objects.create_from_json(received_json_data)
     return HttpResponse(json.dumps({'result':'success'}), content_type='application/json')
   
class LoadDataView(View):   
   def obtener_lista_prod_excel(self, filename, pos_codigo_barras = 1, pos_producto = 2, pos_precio_compra = 3, pos_precio_venta = 5, pos_impresiones = 0, pos_inicio = -1, pos_final = -1):
       data = []
       workbook = xlrd.open_workbook(filename)
       worksheet = workbook.sheet_by_name('Sheet1')
       pos_inicio = 3 if pos_inicio == -1 else pos_inicio - 1
       pos_final = worksheet.nrows if pos_final == -1 else pos_final
       for rx in range(pos_inicio,pos_final): 
         codigo_barras = worksheet.cell(rx,pos_codigo_barras).value;
         if type(worksheet.cell(rx,pos_codigo_barras).value) is float:
           codigo_barras = '%13.0f' % worksheet.cell(rx,pos_codigo_barras).value
         if type(codigo_barras) is unicode:
            if codigo_barras == u'':
               codigo_barras = None
         producto = worksheet.cell(rx,pos_producto).value
         precioCompra = None
         if type(worksheet.cell(rx,pos_precio_compra).value) is float:
            precioCompra = worksheet.cell(rx,pos_precio_compra).value
         precioVenta = None
         if type(worksheet.cell(rx,pos_precio_venta).value) is float:
            precioVenta = worksheet.cell(rx,pos_precio_venta).value	
         impresiones = 1
         if type(worksheet.cell(rx,pos_impresiones).value) is float:
            impresiones = int(worksheet.cell(rx,pos_impresiones).value)
         data.append({'producto': producto, 'codigo': codigo_barras, 'precioCompra': precioCompra,'precioVenta':precioVenta, 'cantidad': impresiones})
       return data
	   
   def get(self, request, *args, **kwargs):
       Producto.objects.all().delete()	
       productos = self.obtener_lista_prod_excel('/vagrant/consultaprecio/ListaDePrecios23enero.xlsx',1, 4,5, 6, 4, 3,-1)
       for producto in productos:
          print producto  
          Producto.objects.create(barcode=producto['codigo'],description=producto['producto'], existencia=producto['cantidad'],precioCompra=producto['precioCompra'],precioVenta=producto['precioVenta'])		  
       return HttpResponse('LISTO', content_type='text/plain')       	
   
   
class FindView(View):
   def get(self, request, *args, **kwargs):
      print kwargs['barcode']
      productos = request.productos
      print productos
      producto = {'producto':'Lapiz dddd', 'precio':20}
      return HttpResponse(json.dumps(producto), content_type='application/json')
	  
   def consulta(self, request, codebar, *args, **kwargs):
      print codebar
      producto = {'producto':'Lapiz dddd', 'precio':20}
      return HttpResponse(json.dumps(producto), content_type='application/json')        
   

class FindProductView(TemplateView):
   template_name = 'precios/home.html'
   def get_context_data(self, **kwargs):
      context = super(TemplateView, self).get_context_data(**kwargs)
      vta = TipoMovimiento.objects.filter(codigo='VTA')[0]
      print vta
      print vta.codigo, vta.description
      context['tipo_movimiento'] = vta
      return context


class ChangeProductView(TemplateView):
   template_name = 'precios/cambioprecio.html'
   def get_context_data(self, **kwargs):
      context = super(TemplateView, self).get_context_data(**kwargs)
      vta = TipoMovimiento.objects.filter(codigo='VTA')[0]
      print vta
      print vta.codigo, vta.description
      context['tipo_movimiento'] = vta
      return context
