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
import os
import datetime
from precios.models import TipoMovimiento, Movimiento, Categoria
from precios.etiqueta_chica import generar_etiquetas, obtener_lista_productos
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Create your views here.
@login_required
def logout_view(request):
  logout(request)
  return redirect('login')

def login_view(request):
   #import pdb; pdb.set_trace()
   if request.method == 'POST': 
      username = request.POST['username']
      password = request.POST['password']
      print username, ':', password
      user = authenticate(request, username=username, password=password)
      if user is not None:
        login(request, user)
        return redirect('consulta')
      else:
        return render(request,'precios/login.html',{'error':'Invalid username o password'}) 
   return render(request, 'precios/login.html')


@login_required
def find_consulta(request,barcode):
   print 'saludos 3'
   productos = list(Producto.objects.filter(barcode=barcode))
   if len(productos) == 0:
      return HttpResponse(status=204)
   pr = productos[0]
   return HttpResponse(json.dumps(pr.as_dict()), content_type='application/json')  


@login_required
def find_all(request): 
   productos = list(Producto.objects.all())
   result = [ obj.as_dict() for obj in productos ]
   return HttpResponse(json.dumps(result), content_type='application/json') 


@login_required
def download(request):
    print os.getcwd() 
    #file_path = '/app/TPV/TPVBelleza/consultaprecio/salida_dj.pdf'
    print "Modificando ruta descarga" 
     
    file_path = os.getcwd()+'/generated/salida_dj.pdf'
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


@login_required
def genera_etiquetas(request):
   print "Imprimir etiquetas"
   data = json.loads(request.body)
   print data
   lista_productos=[]
   for item in data['items']:
      lista_productos.append({'producto': item['description'], 'codigo': item['barcode'], 'precio': item['precioVenta'], 'cantidad': item['cantidad'] }) 
   #lista_productos = obtener_lista_productos()
   archivo = os.getcwd()+'/generated/salida_dj.pdf'
   generar_etiquetas(archivo,lista_productos,20,4,data['posicion'])  
    
   return HttpResponse(json.dumps({'result':'success'}), content_type='application/json')


@login_required
def guarda_producto(request):
   print "Guardar producto"
   if request.method=='POST':
      producto = json.loads(request.body)
      print producto 
      id = producto['categoria'];
      categoria = Categoria.objects.get(pk=id)
      print categoria
      Producto.objects.create(barcode=producto['barcode'],description=producto['descripcion'], existencia=0,precioCompra=producto['precioCompra'],precioVenta=producto['precioVenta'],  categoria=categoria, minimoexist=producto['puntoreorden'], ubicacion=producto['ubicacion'], falta = datetime.datetime.now())		 

      return HttpResponse(json.dumps({'result':'success'}), content_type='application/json')

 
@login_required
def guarda_ticket(request):
   print "Guardar Tickets"
   if request.method=='POST':
     received_json_data=json.loads(request.body)
     print received_json_data
     print "saludos"
     mov = Movimiento.objects.create_from_json(received_json_data)
     print mov
     return HttpResponse(json.dumps({'result':'success'}), content_type='application/json')
  

@login_required
def upload_file(request):
    print "Subiendo el archivo"
    if request.method == 'POST' and request.FILES['catalogo']:
        myfile = request.FILES['catalogo']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        print uploaded_file_url
        path_file = settings.BASE_DIR + uploaded_file_url 
        print path_file
        load = LoadData(path_file)
        load.carga_catalogo()
        
    return HttpResponse(json.dumps({'result':'success'}), content_type='application/json')

class LoadData:
   def __init__(self, pathfile):
       self.pathfile = pathfile
   
   def obtener_lista_prod_excel(self, filename, pos_codigo_barras = 1, pos_existencia = 2,pos_puntoreorden = 3,  pos_producto = 4, pos_precio_compra = 5, pos_precio_venta = 6, pos_ubicacion = 7,  pos_categoria = 8, pos_inicio = -1, pos_final = -1):
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
         existencia = 1
         if type(worksheet.cell(rx,pos_existencia).value) is float:
            existencia = int(worksheet.cell(rx,pos_existencia).value)
         puntoreorden = 1
         if type(worksheet.cell(rx,pos_puntoreorden).value) is float:
            puntoreorden = worksheet.cell(rx,pos_puntoreorden).value
         ubicacion = worksheet.cell(rx,pos_ubicacion)
         categoria = 1
         if type(worksheet.cell(rx,pos_categoria).value) is int:
            categoria = worksheet.cell(rx,pos_categoria).value 

         data.append({'producto': producto, 'codigo': codigo_barras, 'precioCompra': precioCompra,'precioVenta':precioVenta, 'existencia': existencia, 'categoria' : categoria , 'ubicacion': ubicacion, 'puntoreorden': puntoreorden})
       return data
	   
   def carga_catalogo(self):
       #Producto.objects.all().delete()	
       productos = self.obtener_lista_prod_excel(self.pathfile,1, 2, 3, 4,5,6,7,8, 3,-1)
       for producto in productos:
          print producto  
          cat_categoria = Categoria.objects.get(pk=producto['categoria'])
          Producto.objects.create(barcode=producto['codigo'],description=producto['producto'], existencia=producto['existencia'],precioCompra=producto['precioCompra'],precioVenta=producto['precioVenta'], categoria = cat_categoria, ubicacion=producto['ubicacion'], minimoexist=producto['puntoreorden'], falta=datetime.datetime.now())		  
       return 1       	
   
   
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
      catalogo = list(TipoMovimiento.objects.all())
      categorias = list(Categoria.objects.all())
      print vta
      print vta.codigo, vta.description
      context['tipo_movimiento'] = vta
      context['catalogo_tipos_mov'] = catalogo
      context['categorias'] = categorias
      return context


class PrintLabelView(TemplateView):
   template_name = 'precios/impresion_etiquetas.html'
   def get_context_data(self, **kwargs):
      context = super(TemplateView, self).get_context_data(**kwargs)
      compra = TipoMovimiento.objects.filter(codigo='COM')[0]
      context['tipo_movimiento'] = compra
      return context


class ImportCatalogView(TemplateView):
   template_name = 'precios/import_catalog.html'
   def get_context_data(self, **kwargs):
      context = super(TemplateView, self).get_context_data(**kwargs)
      compra = TipoMovimiento.objects.filter(codigo='COM')[0]
      context['tipo_movimiento'] = compra
      return context


