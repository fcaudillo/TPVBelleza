# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
from __future__ import absolute_import, unicode_literals

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
from precios.models import TipoMovimiento, Movimiento, Categoria, Compania, Plan, Recarga, Persona, HistoriaPrecioProveedor, CambioPrecio
from precios.etiqueta_chica import generar_etiquetas, obtener_lista_productos
from precios.etiqueta_mediana import generar_etiquetas_mediana
from precios.LoadCatalogoProv import LoadListaProdProv
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db import connection
#from celery import Celery
#from kombu import Connection, Exchange, Queue, Producer
from tasks import recarga, consultaSaldo 
import sys
from django.apps import apps
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cgi import escape

miapp = apps.get_app_config('precios')

def cargar_cambios_precios(request,proveedor):    
    print "proveedor", proveedor
    sql = """
            select p."codigoInterno",
                   p."codigoProveedor",
                   p."description",
                   pp2."description" as proveedor,
                   p."unidadVenta",
                   p."precioCompra" as "precioActualTlapa",
                   pp."precioCompra" as "ultimoPrecioProv",
                   p."precioVenta"
              from precios_producto p  left join precios_historiaprecioproveedor pp
                          on p.persona_id = pp.proveedor_id
                         and p."codigoProveedor" = pp."codigoProveedor"
                         left join precios_persona pp2  
                           on pp2.id = p.persona_id 
             where p.persona_id = %s
               and p."precioCompra" <> pp."precioCompra"
          """ % (proveedor)
    print sql
    CambioPrecio.objects.filter(proveedorId=proveedor).delete()
    cursor = connection.cursor()
    cursor.execute(sql, [])
    items = cursor.fetchall()
    for item in items:
      CambioPrecio.objects.create(codigoInterno=item[0],codigoProveedor=item[1],proveedor=item[3],proveedorId=proveedor,description=item[2],precioCompra=item[6],precioCompraAnt=item[5],precioVenta=item[7], fecha = datetime.datetime.now())

    return HttpResponse(json.dumps({"status":"success"}), content_type='application/json')

def find_cambio_precio(request,proveedor):
    result = [];
    print "Estoy en find_cambio_precio ", proveedor
    lista = list(CambioPrecio.objects.filter(proveedorId=proveedor).order_by('description'))
    for item in lista:
      result.append(item.as_dict())
    return HttpResponse(json.dumps(result), content_type='application/json')

def delete_cambio_precio(request, key):
   CambioPrecio.objects.filter(id=key).delete()
   return HttpResponse(json.dumps({"result":"success"}), content_type='application/json')


def siguiente_folio(prefix):
  prefijo = prefix.strip();
  dat = list(Producto.objects.raw("Select *, max(substr(barcode,length('%s'))) as maximo from precios_producto where  barcode like '%s' " % (prefijo,prefijo + '%%' ) ))
  if dat[0].id  == None:
     return 1
  
  #import pdb; pdb.set_trace()
  return int( dat[0].barcode[len(prefijo):]  ) + 1

def next_folio():
  sql = "select nextval('SEQ_PRODUCTOS')";
  cursor = connection.cursor();
  cursor.execute(sql,[])
  items = cursor.fetchall();
  return items[0];

def calcular_codigo_barras(codigo):
  if len(codigo.strip()) > 4:
     return codigo.strip()
  prefijo = 'A' 
  if len(codigo.strip()) > 0:
    prefijo = codigo.strip()

  siguiente = str(siguiente_folio(prefijo))
  codigo_generado = prefijo + siguiente.zfill(11 - len(prefijo) )
  return codigo_generado
    
  
@login_required
def generar_codigo_barras(request,prefijo):
   codigo = calcular_codigo_barras(prefijo) 
   return HttpResponse(json.dumps({'respuesta':'OK', 'codigo_barras': codigo}), content_type='application/json')

@login_required
def obtenerSaldo(request):
   try:
      result = consultaSaldo.apply_async([],queue='celeryx') 
      print "1. Esperando 8000 para resultados"
      result.wait(8000)
      print (result.result)
      monto = result.result
      return HttpResponse(monto, content_type='application/json')
   except:
     return HttpResponse(json.dumps({"saldo":-1}), content_type='application/json') 

def send_to_print(modulo, plantilla,  objetojson):
   try:
     print ("Imprimiendo desde el modulo: " + modulo)
     data = dict()
     datos_generales = dict()
     datos_generales['cliente_nombre'] = miapp.getConfiguracion().get('CLIENTE_NOMBRE')
     datos_generales['ticket_pie'] = miapp.getConfiguracion().get('TICKET_PIE')
     datos_generales['cliente_giro'] = miapp.getConfiguracion().get('CLIENTE_GIRO')
     data['datos_generales'] = datos_generales
     data['template'] = plantilla
     data['data'] = objetojson

     print_object = json.dumps(data)
     name_queue = 'msgreload_' +  os.environ['CLIENTE_ID']

     print("***** Enviando hacia  rabbitmq para impresion: " + name_queue)
     print (print_object)
     print ("**********************")
     task_queue = Queue(name_queue, Exchange(name_queue), routing_key=name_queue)
     broker_url = 'amqp://%s:%s@rabbitmq:5672//' % (os.environ['USUARIO_MQ'],os.environ['PASSWORD_MQ'])
     print (broker_url)
     with Connection(broker_url) as conn:
       with conn.channel() as channel:
         producer = Producer(channel)
         producer.publish(print_object,exchange=task_queue.exchange,routing_key=task_queue.routing_key,declare=[task_queue])
         print ("Se envio a impresion la plantilla " + plantilla)
   except Exception as e:
      print ("A ocuurido un error al enviar a impresion plantilla " + plantilla)
      print (e)



@login_required
def recargatae (request,compania, plan, numero,monto):
   print compania,plan,numero,monto
   planObj = None
   rec = None
   result = None

   try:
      planObj = Plan.objects.filter(plan = plan)[0]
      print ("monto req " + monto + " monto plan " + str(planObj.monto))
      if int(planObj.monto) != int(monto):
         return HttpResponse(json.dumps({'rcode':23, 'rcode_description': 'El monto no coincide con el plan'}), content_type='application/json')
      if planObj.compania.codigo != compania:
         return HttpResponse(json.dumps({'rcode':23, 'rcode_description': 'El plan no coincide con la compania'}), content_type='application/json')

      rec = Recarga.objects.create(plan = planObj,  celular = numero, monto= planObj.monto)
   except:
      return HttpResponse(json.dumps({'rcode':25, 'rcode_description':  'Error guardando la recarga' }), content_type='application/json')

   try:
      result = recarga.apply_async([compania,plan,numero,monto],queue='celeryx') 
      print "Esperando 16000 para resultados"
      result.wait(16000)
      print ("resultado 2" + result.result)
   except:
        rec.estatus = 'ERROR'
        rec.error = sys.exc_info()[0]
        rec.save()
        return HttpResponse(json.dumps({'rcode':26, 'rcode_description':  'Se envio al proveedor sin respuesta.' }), content_type='application/json')

   res = None
   try:
     print (result.result)
     res = json.loads(result.result)
     print (rec)
     if res['rcode'] != 0:
        rec.estatus = 'ERROR'
        rec.error = res['rcode_description']
        rec.save()
     else:
        rec.estatus = 'OK'
        rec.codigoautorizacion = res['op_authorization']
        print ("Codigo de autorizacion : ")
        print (res['op_authorization'])
        rec.save()
        try:
          #Guardar la venta
          mov = dict()
          mov['tipo_movimiento'] = TipoMovimiento.objects.filter(codigo='TAE')[0].id

          planObj = Plan.objects.filter(plan=plan)[0]
          mov['total'] = planObj.producto.precioVenta
          mov['descripcion'] = 'VENTA DE TIEMPO  AIRE'
          items = []
          mov['items'] = items
          pr = planObj.producto
          det_mov = dict()
          det_mov['cantidad'] = 1
          det_mov['barcode'] = pr.barcode
          det_mov['ubicacion'] = ''
          det_mov['description'] = planObj.description
          det_mov['precioCompra'] = pr.precioCompra
          det_mov['precioVenta'] = pr.precioVenta
          det_mov['total'] = det_mov['cantidad'] * pr.precioVenta
          items.append(det_mov)

          Movimiento.objects.create_from_json(mov,request.user)
        except:
           pass
   except:
      return HttpResponse(json.dumps({'rcode':234, 'rcode_description': 'Desconocido ' + result.result}), content_type='application/json')

   try:
     send_to_print("Recargas","print_recibo_tae",res)
   except Exception as e:
     print ("A ocurrido una execpcion en impresion de recibo")
 
   return HttpResponse(result.result, content_type='application/json') 

@login_required
def on_line(request):
   return HttpResponse(json.dumps({"on_line": True}), content_type='application/json')

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
      user = authenticate(request, username=username, password=password)
      if user is not None:
        login(request, user)
        return redirect('consulta')
      else:
        return render(request,'precios/login.html',{'error':'Invalid username o password'}) 
   return render(request, 'precios/login.html')



@login_required
def reporte_diario(request):
   hoy = datetime.datetime.now() 
   fini = hoy.strftime('%Y%m%d')
   ffin = fini 
   list_grupos = list(request.user.groups.all()); 
   nombres_grupos = [item.name for item in list_grupos] 
   es_master = True if 'Master' in nombres_grupos else False;
   return render(request,'precios/reporte_diario.html',{'pantalla':'reporte_diario','fini':fini, 'ffin':ffin, 'es_master': es_master,'nombre_cliente':miapp.getConfiguracion().get('CLIENTE_NOMBRE')})


@login_required
def rep_vtadet(request):
   hoy = datetime.datetime.now()
   fini = hoy.strftime('%Y%m%d')
   ffin = fini
   list_grupos = list(request.user.groups.all());
   nombres_grupos = [item.name for item in list_grupos]
   es_master = True if 'Master' in nombres_grupos else False;
   return render(request,'precios/reporte_vtadet.html',{'pantalla':'rep_vtadet','fini':fini, 'ffin':ffin, 'es_master': es_master,'nombre_cliente':miapp.getConfiguracion().get('CLIENTE_NOMBRE')})


@login_required
def find_movimiento(request,fechaIni, fechaFin):
    result = [];
    print "Estoy en find_movimiento"
    fini = datetime.datetime.strptime(fechaIni  + ' 0:0:0','%d/%m/%Y %H:%M:%S')
    ffin = datetime.datetime.strptime(fechaFin  + ' 23:59:59','%d/%m/%Y %H:%M:%S')
    lista = list(Movimiento.objects.filter(fecha__time__range=(fini,ffin)).order_by('tipo_movimiento__prioridad'))
    for item in lista:
      dat = {'fecha': item.fecha, 'Tipo Mov': item.tipo_movimiento.description }
      result.append(dat)
    return result



@login_required
def  recargas_periodo(request,fechaIni, fechaFin):
    result = [];
    fi = fechaIni[:4] + "/" + fechaIni[4:6] + "/" + fechaIni[6:8]
    ff = fechaFin[:4] + "/" + fechaFin[4:6] + "/" + fechaFin[6:8]
    fini = datetime.datetime.strptime(fi  + ' 0:0:0','%Y/%m/%d %H:%M:%S')
    ffin = datetime.datetime.strptime(ff  + ' 23:59:59','%Y/%m/%d %H:%M:%S')

    items = list(Recarga.objects.filter(falta__range=(fini,ffin)).order_by('-falta'))
    for item in items:
      dat = {'fecha': item.falta.strftime("%d/%m/%Y, %H:%M:%S"), "descripcion"  : item.plan.description, "telefono" : item.celular, "monto":  item.monto, "codigoautorizacion":item.codigoautorizacion, "error" : item.error, "estatus" : item.estatus }
      result.append(dat)

    return HttpResponse(json.dumps(result), content_type='application/json')


def venta_productos(request,fechaIni, fechaFin):
    result = [];
    fi = fechaIni[:4] + "/" + fechaIni[4:6] + "/" + fechaIni[6:8]
    ff = fechaFin[:4] + "/" + fechaFin[4:6] + "/" + fechaFin[6:8]
    fini = datetime.datetime.strptime(fi  + ' 0:0:0','%Y/%m/%d %H:%M:%S')
    ffin = datetime.datetime.strptime(ff  + ' 23:59:59','%Y/%m/%d %H:%M:%S')
    sql = """

                      select to_char(m.fecha,'DD/MM/YYYY HH24:MI:SS') as fecha,
                                 dm."cantidad",
                                 dm."description" as descripcion, 
                                 dm."precioCompra",
                                 dm."precioVenta",
                                 dm."cantidad" * dm."precioVenta" * tm."factor_conta" as total,
                                 tm."factor_conta",
                                 tm."description",
                                 m."id",
                                 dm."id" as "idDetalle"
                           from precios_detallemovimiento dm inner join precios_movimiento m on
                                                 m.id = dm.movimiento_id
                                                              inner join precios_tipomovimiento tm
                                                                on m.tipo_movimiento_id = tm.id
                          where tm.prioridad in (2,3,4,5)
                            and m.fecha between '%s' and '%s'
                           order by 1 DESC
          """ % (fini, ffin)
    print sql
    cursor = connection.cursor()
    cursor.execute(sql, [])
    items = cursor.fetchall()
    for item in items:
      dat = {'fecha': item[0] , 'cantidad'  : item[1],  'descripcion' : item[2], 'precioCompra':float(item[3]), 'precioVenta': float(item[4]), 'total':float(item[5]), 'factorConta':float(item[6]),'tipoMovimiento':item[7], 'movimientoId':item[8], 'detalleMovientoId': item[9] }
      result.append(dat)

    return HttpResponse(json.dumps(result), content_type='application/json')


@login_required
def  resumen_movimiento(request,fechaIni, fechaFin):
    result = [];
    fi = fechaIni[:4] + "/" + fechaIni[4:6] + "/" + fechaIni[6:8]
    ff = fechaFin[:4] + "/" + fechaFin[4:6] + "/" + fechaFin[6:8]
    fini = datetime.datetime.strptime(fi  + ' 0:0:0','%Y/%m/%d %H:%M:%S')
    ffin = datetime.datetime.strptime(ff  + ' 23:59:59','%Y/%m/%d %H:%M:%S')
    sql = """
			  select to_char(date(m.fecha),'DD/MM/YYYY') as fecha, 
			         tm."description" as description,
					 sum(dm."cantidad" * dm."precioCompra"  * tm."factor_conta") as totalCosto,
			         sum(dm."cantidad" * dm."precioVenta" * tm."factor_conta") as total,
					 sum(dm."cantidad" * (dm."precioVenta" - dm."precioCompra") * tm."factor_conta") as totalGanancia
			
			   from precios_detallemovimiento dm inner join precios_movimiento m on
			                         m.id = dm.movimiento_id
			                                      inner join precios_tipomovimiento tm
								on m.tipo_movimiento_id = tm.id  
			  where tm.prioridad in (2,3,4,5)
			    and m.fecha between  '%s' and '%s'
			  group by date(m.fecha), tm."description"
                          order by 1,2
          """ % (fini, ffin)
    print sql
    cursor = connection.cursor()
    cursor.execute(sql, [])
    items = cursor.fetchall()
    for item in items:
      dat = {'fecha': item[0] , "TipoMovimiento"  : item[1],  "totalVenta" : float(item[3]), "totalCosto":float(item[2]), "totalGanancia": float(item[4]) }
      result.append(dat)

    return HttpResponse(json.dumps(result), content_type='application/json')


@login_required
def  reporte_vtadet(request,fechaIni, fechaFin):
    result = [];
    fi = fechaIni[:4] + "/" + fechaIni[4:6] + "/" + fechaIni[6:8]
    ff = fechaFin[:4] + "/" + fechaFin[4:6] + "/" + fechaFin[6:8]
    fini = datetime.datetime.strptime(fi  + ' 0:0:0','%Y/%m/%d %H:%M:%S')
    ffin = datetime.datetime.strptime(ff  + ' 23:59:59','%Y/%m/%d %H:%M:%S')
    sql = """
                        select m.id as folio,
			       to_char(m.fecha,'DD/MM/YYYY HH:MI:SS') as fecha,
                               tm."description" as tipomovimiento,
							   usuario."username" as usuario,
							   dm."barcode" as codigo,
							   dm."description" as descripcion,
							   dm."cantidad",
							   dm."precioCompra",
							   dm."precioVenta",
							   tm."factor_conta" as factorconta,
                                                           dm."cantidad" * dm."precioVenta" as total
                           from precios_detallemovimiento dm inner join precios_movimiento m on
                                                 m.id = dm.movimiento_id
                                                              inner join precios_tipomovimiento tm
                                                                on m.tipo_movimiento_id = tm.id
				    		              inner join auth_user usuario
								    on m.user_id = usuario.id
                          where m.fecha between  '%s' and '%s'
                         
                          order by 1 desc,2 desc,5 desc
          """ % (fini, ffin)
    print sql
    cursor = connection.cursor()
    cursor.execute(sql, [])
    items = cursor.fetchall()
    for item in items:
      dat = {"folio":item[0],"fecha": item[1] , "tipomovimiento"  : item[2],"username":item[3], "codigo":item[4], "descripcion":item[5],"cantidad":float(item[6]),"preciocompra":float(item[7]),"precioventa":float(item[8]),"factor_conta":float(item[9]),"total":float(item[10])}
      result.append(dat)

    return HttpResponse(json.dumps(result), content_type='application/json')

#@login_required
def find_consulta(request,barcode):
   print 'barcode = ', barcode
   productos = list(Producto.objects.filter(barcode=barcode.strip()))
   if len(productos) == 0:
      productos = list(Producto.objects.filter(codigoInterno=barcode.strip()))
      if len(productos) == 0:
         return HttpResponse(status=204)
   pr = productos[0]
   return HttpResponse(json.dumps(pr.as_dict()), content_type='application/json')  



def updateProducto(request):
  data = json.loads(request.body)
  print 'data = ', data
  productos = list(Producto.objects.filter(codigoInterno=data['codigoInterno']))
  if len(productos) == 1:
   persona = Persona.objects.get(pk=data['proveedor'])
   print 'id = ', productos[0].id
   producto = Producto.objects.get(pk=productos[0].id)
   producto.codigoProveedor = data['codigoProveedor']
   producto.barcode=data['codigoBarras'] 
   producto.persona=persona 
   producto.description=data['descripcion']
   producto.descriptionCorta=data['descripcion']
   producto.existencia=data['existencia']
   producto.minimoexist=data['minimoExistencia']
   producto.maximoexist=data['maximoExistencia']
   producto.precioCompra=data['precioCompra']
   producto.precioVenta=data['precioVenta']
   producto.ubicacion=data['ubicacion']
   producto.unidadVenta=data['unidadVenta']
   producto.puede_venderse= data['puedeVenderse']
   producto.save();
  return HttpResponse("{'return','success'}", content_type='application/json')  

def findByCodigoInterno(request,codigoInterno):
   print 'xx codigoInterno = ', codigoInterno
   productos = list(Producto.objects.filter(codigoInterno=codigoInterno.strip()))
   if len(productos) == 0:
     return HttpResponse(status=204)
   pr = productos[0]
   return HttpResponse(json.dumps(pr.as_dict()), content_type='application/json')  


def findByCodigo(request,codigo):
   print 'findByCodigo = ', codigo
   if len(codigo.strip()) > 10:
     productos = list(Producto.objects.filter(barcode=codigo.strip()))
   else:
     productos = list(Producto.objects.filter(codigoInterno=codigo.strip()))
   if len(productos) == 0:
     return HttpResponse(status=204)
   pr = productos[0]
   return HttpResponse(json.dumps(pr.as_dict()), content_type='application/json')  


def find_historico(request,proveedor,codigo):
   codigo = codigo.strip()
   print '2. find-historico codigo = *',codigo,'*',"abc"
   persona = Persona.objects.get(pk=proveedor)
   print 'persona = ', persona 

   producto_proveedor = list(HistoriaPrecioProveedor.objects.filter(codigobarras=codigo).filter(proveedor=proveedor))
   if len(producto_proveedor) == 0:
     producto_proveedor = list(HistoriaPrecioProveedor.objects.filter(codigoProveedor=codigo).filter(proveedor=proveedor))
     if len(producto_proveedor) == 0:
       print 'No encontro el registro'
       return HttpResponse(status=204)
   print 'saludos 3'
   data = producto_proveedor[0]
   print 'data = ', data
   return HttpResponse(json.dumps(data.as_dict()), content_type='application/json')

def find_persona(request,tipopersona):
  print 'persona = ', tipopersona
  personas = None;
  if tipopersona == 'proveedor' :
    personas = list(Persona.objects.filter(es_proveedor=True))
  else:
    personas = list(Persona.objects.filter(es_cliente=True))
  result = [ obj.as_dict() for obj in personas ]

  return HttpResponse(json.dumps(result), content_type='application/json')


@login_required
def find_all(request): 
   productos = list(Producto.objects.filter(puede_venderse=True))
   result = [ obj.as_dict() for obj in productos ]
   return HttpResponse(json.dumps(result), content_type='application/json') 

def catalogo_productos(request): 
   print 'entrando catalogo_productos' 
   productos = list(Producto.objects.filter(puede_venderse=True))
   print '1..productos'
   result = [ obj.as_dict() for obj in productos ]
   return HttpResponse(json.dumps(result), content_type='application/json') 

def do_paginate(data_list, page_number):
    ret_data_list = data_list
    result_per_page = 500
    paginator = Paginator(data_list, result_per_page)
    try:
        ret_data_list = paginator.page(page_number)
    except EmptyPage:
        # get the lat page data if the page_number is bigger than last page number.
        ret_data_list = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # if the page_number is not an integer then return the first page data.
        ret_data_list = paginator.page(1)
    return [ret_data_list, paginator]

@login_required
def find_products(request):
   prod_list = Producto.objects.filter(puede_venderse=True).order_by('description')
   page_number = request.GET.get('page', 1)
   paginate_result = do_paginate(prod_list, page_number)
   list_prods = paginate_result[0]
   paginator = paginate_result[1]
   productos = list(list_prods.object_list)
   lista = [ obj.as_dict() for obj in productos ]
   result = {
              'num_pages' : paginator.num_pages,
              'current_page': page_number,
              'productos' : lista
            }

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
def genera_etiquetas_mediana(request):
   print "Imprimir etiquetas mediana"
   data = json.loads(request.body)
   print data
   lista_productos=[]
   for item in data['items']:
      precio = '${:,.2f}'.format(item['precioVenta'])
      lista_productos.append({'producto': item['description'], 'codigo': item['codigointerno'], 'medidas': precio, 'cantidad': item['cantidad'] }) 
   #lista_productos = obtener_lista_productos()
   archivo = os.getcwd()+'/generated/salida_dj.pdf'
   generar_etiquetas_mediana(archivo,lista_productos,10,3,data['posicion'])  
    
   return HttpResponse(json.dumps({'result':'success'}), content_type='application/json')

#@login_required
def guarda_producto(request):
   print "Guardar producto"
   if request.method=='POST':
      producto = json.loads(request.body)
      print producto 
      id = producto['categoria'];
      categoria = Categoria.objects.get(pk=id)
      Producto.objects.create(codigoInterno=next_folio(),barcode=producto['barcode'],description=producto['descripcion'], existencia=0,precioCompra=producto['precioCompra'],precioVenta=producto['precioVenta'],  categoria=categoria, minimoexist=producto['puntoreorden'], maximoexist=producto['maximoexist'], ubicacion=producto['ubicacion'], falta = datetime.datetime.now())		 

      return HttpResponse(json.dumps({'result':'success'}), content_type='application/json')

def guarda_producto_nuevo(request):
   print "1.Guardar producto nuevo"
   if request.method=='POST':
      producto = json.loads(request.body)
      print producto
      categoria = Categoria.objects.filter(codigo='root')[0]
      persona = Persona.objects.get(pk=producto['proveedor'])
      print persona
      prod_bd = Producto.objects.filter(codigoProveedor=producto['codigoProveedor'],persona=persona)
      if prod_bd.exists():
        print "producto existente"
        return HttpResponse(json.dumps({'result':'El registro ya existe'}),status=404, content_type='application/json')
      folio = str(next_folio()[0])
      Producto.objects.create(
	codigoInterno=folio,
	barcode=producto['codigoBarras'].strip(),
        codigoProveedor=producto['codigoProveedor'].strip(),
	description=producto['descripcion'].strip(), 
	existencia=producto['existencia'],
	precioCompra=producto['precioCompra'],
	precioVenta=producto['precioVenta'],  
	categoria=categoria, 
	minimoexist=producto['minimoExistencia'], 
	maximoexist=producto['maximoExistencia'], 
	ubicacion=producto['ubicacion'], 
        unidadVenta=producto['unidadVenta'].strip(), 
        persona=persona,
	falta = datetime.datetime.now())

      return HttpResponse(json.dumps({'result':'success','folio': folio}), content_type='application/json')
 
@login_required
def guarda_ticket(request):
   if request.method=='POST' or request.method == 'GET':
     received_json_data=json.loads(request.body)
     print received_json_data
     current_user = request.user
     mov = Movimiento.objects.create_from_json(received_json_data, current_user)
     now = datetime.datetime.now()
     fecha = now.strftime("%m/%d/%Y %H:%M:%S")
     return HttpResponse(json.dumps({'result':'success','folio':mov.id,'fecha': fecha}), content_type='application/json')
  


@login_required
def upload_catalogo_proveedor(request):
    print "Subiendo el archivo"
    if request.method == 'POST' and request.FILES['catalogo_proveedor']:
        myfile = request.FILES['catalogo_proveedor']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        print uploaded_file_url
        path_file = settings.BASE_DIR + uploaded_file_url 
        print path_file
        load = LoadListaProdProv(path_file)
        load.carga_catalogo()
        
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
   
   def obtener_lista_prod_excel(self, filename, pos_codigo_barras = 0,pos_codigoproveedor = 1, pos_existencia = 2,pos_puntoreorden = 3, pos_maximoexist= 4,  pos_producto = 5, pos_precio_compra = 6, pos_precio_venta = 7, pos_ubicacion = 8,  pos_categoria = 9, pos_inicio = -1, pos_final = -1):
       data = []
       workbook = xlrd.open_workbook(filename)
       worksheet = workbook.sheet_by_name('Configuracion')
       pos_codigo_barras = ord(worksheet.cell(1,1).value) - ord('A')
       pos_codigo_proveedor = ord(worksheet.cell(2,1).value) - ord('A')
       pos_codigo_interno = ord(worksheet.cell(3,1).value) - ord('A')
       pos_existencia = ord(worksheet.cell(4,1).value) - ord('A')
       pos_puntoreorden = ord(worksheet.cell(5,1).value) - ord('A')
       pos_maximoexist = ord(worksheet.cell(6,1).value) - ord('A')
       pos_producto = ord(worksheet.cell(7,1).value) - ord('A')
       pos_description_corta = ord(worksheet.cell(8,1).value) - ord('A')
       pos_precio_compra = ord(worksheet.cell(9,1).value) - ord('A')
       pos_precio_venta = ord(worksheet.cell(10,1).value) - ord('A')
       pos_unidad_venta = ord(worksheet.cell(11,1).value) - ord('A') 
       pos_ubicacion = ord(worksheet.cell(12,1).value) - ord('A')
       pos_categoria = ord(worksheet.cell(13,1).value) - ord('A')
       pos_inicio = int(worksheet.cell(14,1).value) - 1
       pos_final = int(worksheet.cell(15,1).value)
       print "codigo_interno", pos_codigo_interno
       print "codigo proveeddor", pos_codigo_proveedor, " letra ", worksheet.cell(2,1).value 
       print "precio_compra " , pos_precio_compra
       worksheet = workbook.sheet_by_name('Productos')
       proveedor = worksheet.cell(0,1).value
       for rx in range(pos_inicio,pos_final): 
         print "pos codigo prov ", pos_codigo_proveedor, " = ", 2
         print "valor 2 ", worksheet.cell(rx,int(pos_codigo_proveedor)).value
         print "valor prov ", worksheet.cell(rx,pos_codigo_proveedor).value, " -> ", worksheet.cell(rx,2).value
         codigo_barras = worksheet.cell(rx,pos_codigo_barras).value;
         if codigo_barras is None:
           codigo_barras = ''
         if type(worksheet.cell(rx,pos_codigo_barras).value) is float:
           codigo_barras = '%13.0f' % worksheet.cell(rx,pos_codigo_barras).value
         for ren in range(0,8): 
           print "ren = ", ren, " valor = " , worksheet.cell(rx,ren).value 
         codigoproveedor = worksheet.cell(rx,pos_codigo_proveedor).value;
         if type(worksheet.cell(rx,pos_codigo_proveedor).value) is float:
           codigoproveedor = '%d' % worksheet.cell(rx,pos_codigo_proveedor).value

         codigoInterno = worksheet.cell(rx,pos_codigo_interno).value
         if type(worksheet.cell(rx,pos_codigo_interno).value) is float:
            codigoInterno = '%d' % worksheet.cell(rx,pos_codigo_interno).value

         if type(codigo_barras) is unicode:
            if codigo_barras == u'':
               codigo_barras = ''
         producto = worksheet.cell(rx,pos_producto).value
         descriptionCorta = worksheet.cell(rx,pos_description_corta).value
         unidadVenta = worksheet.cell(rx,pos_unidad_venta).value

         precioCompra = worksheet.cell(rx,pos_precio_compra).value
         precioVenta = worksheet.cell(rx,pos_precio_venta).value	
         existencia = 1
         if type(worksheet.cell(rx,pos_existencia).value) is float:
            existencia = int(worksheet.cell(rx,pos_existencia).value) 
         puntoreorden = 1 
         if type(worksheet.cell(rx,pos_puntoreorden).value) is float: 
            puntoreorden = worksheet.cell(rx,pos_puntoreorden).value
          
         maximoexist = 1
         if type(worksheet.cell(rx,pos_maximoexist).value) is float:
            maximoexist = worksheet.cell(rx,pos_maximoexist).value
         ubicacion = worksheet.cell(rx,pos_ubicacion).value
         print "codigo interno  ", worksheet.cell(rx,pos_codigo_interno).value
         categoria = Categoria.objects.filter(codigo=worksheet.cell(rx,pos_categoria).value)[0]
         persona = Persona.objects.filter(codigo=worksheet.cell(0,1).value)[0]
         if type(worksheet.cell(rx,pos_categoria).value) is str: 
            cat_tmp = worksheet.cell(rx,pos_categoria).value 
            cat_bus = Categoria.objects.filter(codigo=cat_tmp)
            if cat_bus.count() > 0:
              categoria = cat_bus[0]
         data.append({'producto': producto,'descriptionCorta':descriptionCorta,'unidadVenta':unidadVenta,  'codigo': codigo_barras,'codigoInterno':codigoInterno, 'codigoProveedor': codigoproveedor, 'precioCompra': precioCompra,'precioVenta':precioVenta, 'existencia': existencia, 'categoria' : categoria , 'ubicacion': ubicacion, 'puntoreorden': puntoreorden, 'maximoexist': maximoexist,'persona':persona})
       return data
	   
   def carga_catalogo(self):
       #Producto.objects.all().delete()	
       productos = self.obtener_lista_prod_excel(self.pathfile,0, 1, 2, 3,4,5,6,7,8,9, 3,-1)
       for producto in productos:
          print producto  
          #producto['codigo'] = calcular_codigo_barras(producto['codigo'])
          producto['codigo'] = producto['codigo'] if producto['codigo'] else producto['codigoInterno']
          Producto.objects.create(barcode=producto['codigo'],codigoProveedor=producto['codigoProveedor'],codigoInterno=producto['codigoInterno'],description=producto['producto'], descriptionCorta=producto['descriptionCorta'],unidadVenta=producto['unidadVenta'], existencia=producto['existencia'],precioCompra=producto['precioCompra'],precioVenta=producto['precioVenta'], categoria = producto['categoria'], ubicacion=producto['ubicacion'], minimoexist=producto['puntoreorden'],maximoexist=producto['maximoexist'],persona=producto['persona'],falta=datetime.datetime.now())		  
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
      list_grupos = list(self.request.user.groups.all()); 
      nombres_grupos = [item.name for item in list_grupos] 
      context['nombre_cliente'] = escape(miapp.getConfiguracion().get('CLIENTE_NOMBRE'))
      context['ticket_pie'] = escape(miapp.getConfiguracion().get('TICKET_PIE'))
      context['cliente_giro'] = miapp.getConfiguracion().get('CLIENTE_GIRO')
      context['cliente_direccion'] = escape(miapp.getConfiguracion().get('CLIENTE_DIRECCION'))
      context['tipo_movimiento'] = vta
      context['pantalla'] = 'ventas'
      context['ip_impresora'] = miapp.getConfiguracion().get('IP_IMPRESORA')
      context['adicional'] = miapp.getConfiguracion().get('TICKET_ADICIONAL')
      context['es_master'] = True if 'Master' in nombres_grupos else False;
      return context


class PuntoVentaView(TemplateView):
   template_name = 'precios/puntoventa.html'
   def get_context_data(self, **kwargs):
      context = super(TemplateView, self).get_context_data(**kwargs)
      vta = TipoMovimiento.objects.filter(codigo='VTA')[0]
      list_grupos = list(self.request.user.groups.all()); 
      nombres_grupos = [item.name for item in list_grupos] 
      context['nombre_cliente'] = escape(miapp.getConfiguracion().get('CLIENTE_NOMBRE'))
      context['ticket_pie'] = escape(miapp.getConfiguracion().get('TICKET_PIE'))
      context['cliente_giro'] = miapp.getConfiguracion().get('CLIENTE_GIRO')
      context['cliente_direccion'] = escape(miapp.getConfiguracion().get('CLIENTE_DIRECCION'))
      context['tipo_movimiento'] = vta
      context['pantalla'] = 'ventas'
      context['ip_impresora'] = miapp.getConfiguracion().get('IP_IMPRESORA')
      context['adicional'] = miapp.getConfiguracion().get('TICKET_ADICIONAL')
      context['es_master'] = True if 'Master' in nombres_grupos else False;
      return context


class ChangeProductView(TemplateView):
   template_name = 'precios/cambioprecio.html'
   def get_context_data(self, **kwargs):
      context = super(TemplateView, self).get_context_data(**kwargs)
      vta = TipoMovimiento.objects.filter(codigo='VTA')[0]
      catalogo = list(TipoMovimiento.objects.all())
      categorias = list(Categoria.objects.all())
      #import pdb; pdb.set_trace()
      list_grupos = list(self.request.user.groups.all()); 
      nombres_grupos = [item.name for item in list_grupos] 
      context['nombre_cliente'] = miapp.getConfiguracion().get('CLIENTE_NOMBRE')
      context['tipo_movimiento'] = vta
      context['catalogo_tipos_mov'] = catalogo
      context['categorias'] = categorias
      context['pantalla'] = 'movimiento_inventario'
      context['es_master'] = True if 'Master' in nombres_grupos else False;
      return context

   def dispatch(self, request, *args, **kwargs):
      list_grupos = list(self.request.user.groups.all()); 
      nombres_grupos = [item.name for item in list_grupos] 
      if not 'Master' in nombres_grupos:
        return redirect('consulta')
      return super(ChangeProductView,self).dispatch(request,args, kwargs)

class PrintLabelView(TemplateView):
   template_name = 'precios/impresion_etiquetas.html'
   def get_context_data(self, **kwargs):
      context = super(TemplateView, self).get_context_data(**kwargs)
      compra = TipoMovimiento.objects.filter(codigo='COM')[0]
      list_grupos = list(self.request.user.groups.all()); 
      nombres_grupos = [item.name for item in list_grupos] 
      context['nombre_cliente'] = miapp.getConfiguracion().get('CLIENTE_NOMBRE')
      context['tipo_movimiento'] = compra
      context['pantalla'] = 'impresion'
      context['es_master'] = True if 'Master' in nombres_grupos else False;
      return context


class ImportCatalogView(TemplateView):
   template_name = 'precios/import_catalog.html'
   def get_context_data(self, **kwargs):
      context = super(TemplateView, self).get_context_data(**kwargs)
      compra = TipoMovimiento.objects.filter(codigo='INV')[0]
      list_grupos = list(self.request.user.groups.all()); 
      nombres_grupos = [item.name for item in list_grupos] 
      context['nombre_cliente'] = miapp.getConfiguracion().get('CLIENTE_NOMBRE')
      context['tipo_movimiento'] = compra
      context['pantalla'] = 'importacion'
      context['es_master'] = True if 'Master' in nombres_grupos else False;
      return context


class ImportCatalogProveedorView(TemplateView):
   template_name = 'precios/import_catalog_proveedor.html'
   def get_context_data(self, **kwargs):
      context = super(TemplateView, self).get_context_data(**kwargs)
      compra = TipoMovimiento.objects.filter(codigo='INV')[0]
      list_grupos = list(self.request.user.groups.all()); 
      nombres_grupos = [item.name for item in list_grupos] 
      context['nombre_cliente'] = miapp.getConfiguracion().get('CLIENTE_NOMBRE')
      context['tipo_movimiento'] = compra
      context['pantalla'] = 'importacion'
      context['es_master'] = True if 'Master' in nombres_grupos else False;
      return context

class RecargaTaeView(TemplateView):
   template_name = 'precios/recarga.html'
   def get_context_data(self, **kwargs):
      context = super(TemplateView, self).get_context_data(**kwargs)
      companias = list(Compania.objects.all())
      planes = list(Plan.objects.filter(tipoplan=0).order_by('compania'))
      planes_json = [] 
      for  item in planes:
         planes_json.append({"plan": item.plan, "description": item.description, "monto": item.monto, "compania" : item.compania.codigo })
      print planes_json
      list_grupos = list(self.request.user.groups.all()); 
      nombres_grupos = [item.name for item in list_grupos] 
      context['nombre_cliente'] = miapp.getConfiguracion().get('CLIENTE_NOMBRE')
      context['titulo'] = 'Recargas  a celular'
      context['companias'] = companias
      context['planes'] = json.dumps(planes_json)
      context['pantalla'] = 'recarga'
      context['es_master'] = True if 'Master' in nombres_grupos else False;
      return context


class RecargaDatosTaeView(TemplateView):
   template_name = 'precios/recarga.html'
   def get_context_data(self, **kwargs):
      context = super(TemplateView, self).get_context_data(**kwargs)
      companias = [] 
      planes = list(Plan.objects.filter(tipoplan=1).order_by('compania'))
      planes_json = [] 
      tmp_compania = ''
      for  item in planes:
         if item.compania.codigo != tmp_compania:
            companias.append(item.compania)
            tmp_compania = item.compania.codigo
         planes_json.append({"plan": item.plan, "description": item.description, "monto": item.monto, "compania" : item.compania.codigo })
      print planes_json
      list_grupos = list(self.request.user.groups.all()); 
      nombres_grupos = [item.name for item in list_grupos] 
      context['nombre_cliente'] = miapp.getConfiguracion().get('CLIENTE_NOMBRE') 
      context['titulo'] = 'Recargas plan de internet (datos) ' 
      context['companias'] = companias
      context['planes'] = json.dumps(planes_json)
      context['pantalla'] = 'recargadatos'
      context['es_master'] = True if 'Master' in nombres_grupos else False;
      return context


class ReporteRecargaView(TemplateView):
   template_name = 'precios/reporte_recarga.html'
   def get_context_data(self, **kwargs):
      print "Estoy en ReporteRecargaView"
      list_grupos = list(self.request.user.groups.all()); 
      nombres_grupos = [item.name for item in list_grupos] 
      es_master = True if 'Master' in nombres_grupos else False;
      context = super(TemplateView, self).get_context_data(**kwargs)
      hoy = datetime.datetime.now() 
      print (hoy.strftime('%Y%m%d'))
      context['nombre_cliente'] = miapp.getConfiguracion().get('CLIENTE_NOMBRE') 
      context['fini'] = hoy.strftime('%Y%m%d')
      context['ffin'] = context['fini'] 
      context['pantalla'] = 'reporte_recarga'
      context['es_master'] = es_master
      return context

