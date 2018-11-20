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
   options = dict(dpi=300,module_height=6,center_text=True, text_distance=1, font_size=6)
   ean = barcode.get('ean13',codigo,writer=ImageWriter())
   return ean.save(filename,options)



def genera_etiqueta (producto, precio, codigo = None):
  etiqueta = []
  style = ParagraphStyle(
        name='Normal',
        spaceAfter=3,
        fontSize=8,
    )
  texto = '''
       <para align=center>{} <br/>
         <font fontSize=14 color=black><b>{}</b></font>
       </para>'''.format(producto,precio)
  #P = Paragraph(texto,styleSheet["BodyText"])
  P = Paragraph(texto,style)
  etiqueta.append(P)
  if codigo is not None:
     jpg_barcode = genera_barcode(codigo,'saludos_barcode')
     img = Image(jpg_barcode)
     img.drawHeight = 5*cm*img.drawHeight / img.drawWidth
     img.drawWidth = 7*cm 
     etiqueta.append(img)
  return etiqueta

def genera_matriz_from_list (lista, columnas):
   pos = 0
   respuesta = []
   while pos < len(lista):
     respuesta.append(lista[pos:pos+columnas])
     pos = pos + columnas
   return respuesta


def obtener_lista_productos():
    data = []
    data.append({'producto': 'Prooducto 1', 'codigo': '0123456789012', 'precio': '$30.00', 'cantidad': 20})
    data.append({'producto': 'Prooducto 2', 'codigo': '0123456789013', 'precio': '$40.00', 'cantidad': 20})
    data.append({'producto': 'Prooducto 3', 'codigo': '0123456789014', 'precio': '$50.00', 'cantidad': 30})
    data.append({'producto': 'Prooducto 4', 'codigo': '0123456789015', 'precio': '$60.00', 'cantidad': 40})
    return data

def obtener_lista_prod_excel(filename):
   data = []
   workbook = xlrd.open_workbook(filename)
   worksheet = workbook.sheet_by_name('Sheet1')
   for rx in range(3,worksheet.nrows): 
     codigo_barras = worksheet.cell(rx,1).value;
     if type(worksheet.cell(rx,1).value) is float:
        codigo_barras = '%13.0f' % worksheet.cell(rx,1).value
     if type(codigo_barras) is unicode:
        if codigo_barras == u'' :
	   codigo_barras = None
     producto = worksheet.cell(rx,2).value
     precio = None
     if type(worksheet.cell(rx,3).value) is float:
        precio = '$%.2f' % worksheet.cell(rx,3).value
     impresiones = 1
     if type(worksheet.cell(rx,0).value) is float:
        impresiones = int(worksheet.cell(rx,0).value)
     data.append({'producto': producto, 'codigo': codigo_barras, 'precio': precio, 'cantidad': impresiones})
   return data

def generate_page_pdf(productos_por_pagina, page_columnas):
    celdas = []
    for producto in productos_por_pagina:
       celda = None
       if producto is not None:
          celda = genera_etiqueta(producto["producto"],producto["precio"],producto["codigo"])
       celdas.append(celda)
    data = genera_matriz_from_list(celdas,page_columnas)
    t=Table(data,3*[6.8*cm], 10*[2.5*cm])
    t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.25,colors.black),
                       ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                       ('ALIGN',(0,0),(-1,-1),'CENTER'),
                       ('LEFTPADDING',(0,0),(-1,-1),6),
                       ('RIGTHPADDING',(0,0),(-1,-1),6),
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
   doc.rightMargin = 3.0 * cm
   # container for the 'Flowable' objects
   elements = []
   
   cantidad_celdas_vacias = ((ord(start_position[0]) - ord('a')) * 3) + ( (ord(start_position[1]) - ord('0')) -1)

   etiquetas = etiquetas + [None for _ in range(cantidad_celdas_vacias)]
   for producto in lista_productos:
      etiquetas = etiquetas + [producto.copy() for _ in range(producto['cantidad'])]
      while len(etiquetas) >= etiquetas_x_hoja:
        pagina = generate_page_pdf(etiquetas[0:etiquetas_x_hoja],page_columnas)
	elements.append(pagina)
        elements.append(PageBreak())
        print "tamaño buffer etiquetas ", len(etiquetas[0:etiquetas_x_hoja])
        del etiquetas[0:etiquetas_x_hoja]
   if len(etiquetas) > 0:
      etiquetas = etiquetas + [ None for _ in range(etiquetas_x_hoja - len(etiquetas))]
      pagina = generate_page_pdf(etiquetas[0:etiquetas_x_hoja],page_columnas)
      elements.append(pagina)
	
   # write the document to disk
   doc.build(elements)        
   return etiquetas
    

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument("--archivo_xls", help="Archivo donde se encuentran los productos en formato de excel")
   parser.add_argument("--archivo_pdf", help="Archivo de salida de impresion en formato pdf")
   parser.add_argument("--inicio_etiqueta", help="Posicion de la primera etiqueta en blanco de la primer hoja")
   args = parser.parse_args()
   file_input = 'precios.xlsx'
   file_output = 'otput.pdf'
   if args.archivo_xls is not None:
     file_input = args.archivo_xls
   if args.archivo_pdf is not None:
     file_output = args.archivo_pdf
   start_etiqueta = args.inicio_etiqueta
   if args.inicio_etiqueta is None:
      start_etiqueta = "a1"
     
   print args.archivo_xls
   print args.archivo_pdf
   #lista_productos = obtener_lista_productos()
   lista_productos = obtener_lista_prod_excel(file_input)
   print lista_productos
   generar_etiquetas(file_output,lista_productos,10,3,start_etiqueta)


#celda = genera_etiqueta("Carrito de niño, mi alegria. áéíóú azul","$23.00","0123456789123")
#celd#a2 = genera_etiqueta("Carrito de niño, mi alegria. áéíóú azul","$44.00")
 




