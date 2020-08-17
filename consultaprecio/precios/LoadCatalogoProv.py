# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
from __future__ import absolute_import, unicode_literals

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


def prueba_carga():
    path_file = '/app/app/TPVBelleza/Precios_disfert_01012019.xlsx'
    load = LoadListaProdProv(path_file)
    load.carga_catalogo()
    return HttpResponse(json.dumps({'result':'success'}), content_type='application/json')

class LoadListaProdProv:
   def __init__(self, pathfile):
       self.pathfile = pathfile
   
   def obtener_lista_desde_excel(self, filename ):
       data = []
       workbook = xlrd.open_workbook(filename)
       worksheet = workbook.sheet_by_name('Configuracion')
       proveedor = worksheet.cell(2,2).value
       print "1. proveedor ->", proveedor
       cell_type = worksheet.cell_type(3,2)
       cell_value = worksheet.cell_value(3,2)
       fecha_lista = None
       if cell_type == xlrd.XL_CELL_DATE:
          dt_tuple = xlrd.xldate_as_tuple(cell_value, workbook.datemode)
          fecha_lista = datetime.date(dt_tuple[0], dt_tuple[1], dt_tuple[2])
       if fecha_lista is None:
          raise ValueError('La fecha de la lista no es del tipo adecuado')
       pos_codigo_proveedor = ord(worksheet.cell(4,2).value) - ord('A') 
       pos_descripcion = ord(worksheet.cell(5,2).value) - ord('A') 
       pos_precio_compra = ord(worksheet.cell(6,2).value) - ord('A') 
       pos_inicio = int(worksheet.cell(7,2).value) 
       pos_final = int(worksheet.cell(8,2).value)
       print "Inicio ", pos_inicio
       print "final ", pos_final
       worksheet = workbook.sheet_by_name('ListaProductos')
       print "proveedor", proveedor
       print "fecha lista", fecha_lista

       persona = Persona.objects.filter(codigo=proveedor)[0]
       for rx in range(pos_inicio,pos_final): 
         codigo_proveedor = worksheet.cell(rx,pos_codigo_proveedor).value;
         if type(worksheet.cell(rx,pos_codigo_proveedor).value) is float:
           codigo_proveedor = '%13.0f' % worksheet.cell(rx,pos_codigo_barras).value
          
         desc = worksheet.cell(rx,pos_descripcion).value
         descripcion = desc.encode("utf-8")
         precio_compra = worksheet.cell(rx,pos_precio_compra).value
         print codigo_proveedor, ' -> ', descripcion
         data.append({'fechaLista': fecha_lista,'codigoProveedor':codigo_proveedor,'descripcion':descripcion,'precioCompra': precio_compra,'proveedor':persona})
       return data
	   
   def carga_catalogo(self):
       productos = self.obtener_lista_desde_excel(self.pathfile)
       for producto in productos:
          print producto  
          try:
            HistoriaPrecioProveedor.objects.create(fechaLista=producto['fechaLista'],proveedor=producto['proveedor'],codigoProveedor=producto['codigoProveedor'],descripcion=producto['descripcion'], precioCompra=producto['precioCompra'])
          except:
            print "Oops!", sys.exc_info()[0], "occurred. insertar historia precio"
       return 1       	
   
if __name__ == '__main__':
    prueba_carga()   

