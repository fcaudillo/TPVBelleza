# -*- coding: utf-8 -*- #from __future__ import unicode_literals from __future__ import absolute_import, unicode_literals

import json
from precios.models import Producto
import xlrd
import json
import os
import datetime
from precios.models import HistoriaPrecioProveedor, Persona
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import sys

class LoadListaProdProv:
   def __init__(self, pathfile):
       self.pathfile = pathfile
   
   def obtener_lista_desde_excel(self, filename ):
       data = []
       workbook = xlrd.open_workbook(filename)
       worksheet = workbook.sheet_by_name('Configuracion')
       proveedor = worksheet.cell(2,1).value
       print "1. proveedor ->", proveedor
       cell_type = worksheet.cell_type(3,1)
       cell_value = worksheet.cell_value(3,1)
       fecha_lista = None
       if cell_type == xlrd.XL_CELL_DATE:
          dt_tuple = xlrd.xldate_as_tuple(cell_value, workbook.datemode)
          fecha_lista = datetime.date(dt_tuple[0], dt_tuple[1], dt_tuple[2])
       if fecha_lista is None:
          raise ValueError('La fecha de la lista no es del tipo adecuado')
       pos_codigo_proveedor = ord(worksheet.cell(4,1).value) - ord('A') 
       pos_descripcion = ord(worksheet.cell(5,1).value) - ord('A') 
       print "cell(6,1) = ", worksheet.cell(5,1).value
       pos_caja = ord(worksheet.cell(6,1).value) - ord('A') 
       pos_unidad = ord(worksheet.cell(7,1).value) - ord('A') 
       pos_codigobarras = ord(worksheet.cell(8,1).value) - ord('A') 
       pos_alta_rotacion = ord(worksheet.cell(9,1).value) - ord('A') 
       pos_precioCompra = ord(worksheet.cell(10,1).value) - ord('A') 
       pos_precioMayoreo = ord(worksheet.cell(11,1).value) - ord('A') 
       pos_precioPublico = ord(worksheet.cell(12,1).value) - ord('A') 
       pos_inicio = int(worksheet.cell(13,1).value) 
       pos_final = int(worksheet.cell(14,1).value)
       print "Inicio ", pos_inicio
       print "final ", pos_final
       worksheet = workbook.sheet_by_name('ListaProductos')
       print "proveedor", proveedor
       print "fecha lista", fecha_lista
       print "pos_unidad ", pos_unidad
       print "pos_codigobarras", pos_codigobarras


       persona = Persona.objects.filter(codigo=proveedor)[0]
       for rx in range(pos_inicio,pos_final): 
         codigo_proveedor = worksheet.cell(rx,pos_codigo_proveedor).value;
         if type(worksheet.cell(rx,pos_codigo_proveedor).value) is float:
           codigo_proveedor = '%13.0f' % worksheet.cell(rx,pos_codigo_proveedor).value
         codigo_proveedor = codigo_proveedor.strip()          
         desc = worksheet.cell(rx,pos_descripcion).value
         descripcion = desc.encode("utf-8")
         try:
           caja = worksheet.cell(rx,pos_caja).value
         except:
           caja = 1;
         try:
           unidad = worksheet.cell(rx,pos_unidad).value
         except:
           unidad = '';
         try:
           codigobarras = worksheet.cell(rx,pos_codigobarras).value
         except:
           codigobarras = '';

         try:
           alta_rotacion = worksheet.cell(rx,pos_alta_rotacion).value
         except:
           alta_rotacion = 0;

         try:
           precioCompra = worksheet.cell(rx,pos_precioCompra).value
         except:
           precioCompra = 0;

         try:
           precioMayoreo = worksheet.cell(rx,pos_precioMayoreo).value
         except:
           precioMayoreo = 0;

         try:
           precioPublico = worksheet.cell(rx,pos_precioPublico).value
         except:
           precioPublico = 0;
      
         print codigo_proveedor, ' -> ', descripcion
         data.append({'fechaLista': fecha_lista,'codigoProveedor':codigo_proveedor,'descripcion':descripcion,'caja':caja,'unidad':unidad,'codigobarras':codigobarras,'alta_rotacion':alta_rotacion,'precioCompra': precioCompra,'precioMayoreo':precioMayoreo,'precioPublico':precioPublico,'proveedor':persona})
       return data
	   
   def carga_catalogo(self):
       productos = self.obtener_lista_desde_excel(self.pathfile)
       for producto in productos:
          print producto  
          try:
            HistoriaPrecioProveedor.objects.create(fechaLista=producto['fechaLista'],proveedor=producto['proveedor'],codigobarras=producto['codigobarras'],  codigoProveedor=producto['codigoProveedor'],descripcion=producto['descripcion'],caja=producto['caja'],unidad=producto['unidad'],alta_rotacion=producto['alta_rotacion'],precioCompra=producto['precioCompra'], precioMayoreo=producto['precioMayoreo'],precioPublico=producto['precioPublico'])
          except:
            print "Oops!", sys.exc_info()[0], "occurred. insertar historia precio"
       return 1       	
   
def prueba_carga():
    path_file = '/app/app/TPVBelleza/CatalogoTrupper.xlsx'
    load = LoadListaProdProv(path_file)
    load.carga_catalogo()
    return HttpResponse(json.dumps({'result':'success'}), content_type='application/json')

#if __name__ == '__main__':
  # prueba_carga()   
#path_file = '/app/app/TPVBelleza/CatalogoTrupper.xlsx'
#load = LoadListaProdProv(path_file)
#load.carga_catalogo()
