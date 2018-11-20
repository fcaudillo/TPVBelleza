
import xlrd
import argparse
import json

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
   
def findProducto (data, codigo):
   for item in data:
      if item['codigo'] == codigo:
        return item	 
   return None
   
if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument("--pos_barcode", nargs='?', const=1, type=int, default=1)
   parser.add_argument("--pos_descripcion", nargs='?', const=2, type=int, default=4)
   parser.add_argument("--pos_precio", nargs='?', const=3, type=int, default=6)
   parser.add_argument("--pos_impresiones", nargs='?', const=0, type=int, default=4)
   parser.add_argument("--pos_inicio", nargs='?', const=3, type=int, default=3)
   parser.add_argument("--pos_final", nargs='?', const=-1, type=int, default=-1)
   
   parser.add_argument("--archivo_xls", help="Archivo donde se encuentran los productos en formato de excel")
   parser.add_argument("--inicio_etiqueta", help="Posicion de la primera etiqueta en blanco de la primer hoja")
   args = parser.parse_args()

     
   print args.archivo_xls
   print args.pos_inicio
   print args.pos_final
   #lista_productos = obtener_lista_productos()
   #lista_productos = obtener_lista_prod_excel(args.archivo_xls,1, 4, 6, 4, 3,-1)

   lista_productos = obtener_lista_prod_excel(args.archivo_xls,args.pos_barcode, args.pos_descripcion, args.pos_precio, args.pos_impresiones, args.pos_inicio, args.pos_final)
   
   item = findProducto(lista_productos,'7502271341880')
   print 'dict', item  
   json.dump(item)
