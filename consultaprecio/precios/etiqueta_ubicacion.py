#!/usr/bin/env python
# -*- coding: utf-8 -*-

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from barcode.writer import ImageWriter
import barcode
import argparse
import xlrd


styleSheet = getSampleStyleSheet()

def genera_barcode(codigo, filename):
   options = dict(dpi=300,module_height=9,center_text=True, text_distance=2, font_size=0)
   codigo  = codigo.strip();
   print "Codigo barrar a generar ", codigo
   ean = None 
   if len(codigo) == 13:
       ean = barcode.get('ean13',codigo,writer=ImageWriter())
   else:   
       options = dict(dpi=200,module_height=5,center_text=True, text_distance=2, font_size=0)
       ean = barcode.get('code128',codigo,writer=ImageWriter())
    
   return ean.save(filename,options)



def genera_etiqueta (codigo):
  etiqueta = []
  style = ParagraphStyle(
        name='Normal',
        spaceAfter=4,
        fontSize=15,
    )
  print "Producto ",codigo 
  texto = '''<para align=center> 
                {}
             </para>
          '''.format(codigo[:40])
  #P = Paragraph(texto,styleSheet["BodyText"])
  P = Paragraph(texto,style)
  etiqueta.append(P)
  if codigo is not None:
     jpg_barcode = genera_barcode(codigo,'barcode_chica')
     img = Image(jpg_barcode)
     img.drawHeight = 1.27*cm*img.drawHeight / img.drawWidth
     #img.drawWidth = 4.45*cm 
     img.drawWidth = 3.0*cm    
     etiqueta.append(img)
  return etiqueta

def genera_matriz_from_list (lista, columnas):
   pos = 0
   respuesta = []
   while pos < len(lista):
     lista_tmp = lista[pos:pos+columnas]
     lista_tmp.insert(1,None)
     lista_tmp.insert(3,None)
     lista_tmp.insert(5,None)
     respuesta.append(lista_tmp)
     pos = pos + columnas
   return respuesta


def obtener_lista_productos():
    data = []
    for x in range(81,161):
       cod = 'A-%03d' % x 
       data.append({'ubicacion':cod})
    return data

def obtener_lista_prod_excel(filename, pos_codigo_barras = 1, pos_producto = 2, pos_precio = 3, pos_impresiones = 0, pos_inicio = -1, pos_final = -1):
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
        if codigo_barras == u'' :
	   codigo_barras = None
     producto = worksheet.cell(rx,pos_producto).value
     precio = None
     if type(worksheet.cell(rx,pos_precio).value) is float:
        precio = '$%.2f' % worksheet.cell(rx,pos_precio).value
     impresiones = 1
     if type(worksheet.cell(rx,pos_impresiones).value) is float:
        impresiones = int(worksheet.cell(rx,pos_impresiones).value)
     data.append({'producto': producto, 'codigo': codigo_barras, 'precio': precio, 'cantidad': impresiones})
   return data

def generate_page_pdf(ubicaciones,page_renglones, page_columnas):
    celdas = []
    for caja in ubicaciones:
       celda = None
       if caja is not None:
          celda = genera_etiqueta(caja["ubicacion"])
       celdas.append(celda)
    data = genera_matriz_from_list(celdas,page_columnas)
    t=Table(data,[4.45*cm, 0.8 * cm,4.45*cm, 0.8 * cm,4.45*cm, 0.8 * cm,4.45*cm], page_renglones*[1.27*cm])
    t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.25,colors.black),
                       ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                       ('ALIGN',(0,0),(-1,-1),'CENTER'),
                       ('LEFTPADDING',(0,0),(-1,-1),0),
                       ('RIGTHPADDING',(0,0),(-1,-1),0),
                       ('TOPPADDING',(0,0),(-1,-1),6),
                       ('BOTTOMPADDING',(0,0),(-1,-1),6),
                       ('TEXTCOLOR',(0,0),(-1,-1),colors.red)]))
    return t; 

def generar_etiquetas(file_output,lista_productos,page_renglones, page_columnas, start_position = "a1"):
   etiquetas = []
   etiquetas_x_hoja = page_renglones * page_columnas
   doc = SimpleDocTemplate(file_output, pagesize=letter)
   doc.topMargin = 1.1 * cm
   doc.bottomMargin = 0
   doc.rightMargin = 2.6 * cm
   # container for the 'Flowable' objects
   elements = []
   
   cantidad_celdas_vacias = ((ord(start_position[0]) - ord('a')) * page_columnas) + ( (ord(start_position[1]) - ord('0')) -1)

   etiquetas = etiquetas + [None for _ in range(cantidad_celdas_vacias)]
   for producto in lista_productos:
      etiquetas = etiquetas + [producto.copy() for _ in range(1)]
      while len(etiquetas) >= etiquetas_x_hoja:
        pagina = generate_page_pdf(etiquetas[0:etiquetas_x_hoja],page_renglones,page_columnas)
	elements.append(pagina)
        elements.append(PageBreak())
        print "tamaño buffer etiquetas ", len(etiquetas[0:etiquetas_x_hoja])
        del etiquetas[0:etiquetas_x_hoja]
   if len(etiquetas) > 0:
      etiquetas = etiquetas + [ None for _ in range(etiquetas_x_hoja - len(etiquetas))]
      pagina = generate_page_pdf(etiquetas[0:etiquetas_x_hoja],page_renglones, page_columnas)
      elements.append(pagina)
	
   # write the document to disk
   doc.build(elements)        
   return etiquetas
    
if __name__ == "__main__":
   lista_productos = obtener_lista_productos()
   archivo = '/app/app/TPVBelleza/salida_ubicacion.pdf'
   generar_etiquetas(archivo,lista_productos,20,4,'a1')   

 




