
import xlrd


class Etiquetador(object):

   def __init__(self, size_font=32, width_barcode=64, height_barcode=2):
      self.size_font=size_font
      self.width_barcode=width_barcode
      self.height_barcode=height_barcode

   def print_product (self, product, barcode=None, price=None, repeat=1):
      for a in range (0,repeat):
          print "producto", product
          if barcode is not None:
             print "codigo barras ", barcode
          if price is not None:
             print "precio ", price


label = Etiquetador()


workbook = xlrd.open_workbook('precios.xlsx')
worksheet = workbook.sheet_by_name('Sheet1')
for rx in range(3,worksheet.nrows):  
   codigo_barras = worksheet.cell(rx,0).value;
   if type(worksheet.cell(rx,0).value) is float:
      codigo_barras = '%13.0f' % worksheet.cell(rx,0).value
   if type(codigo_barras) is unicode:
      if codigo_barras == u'' :
         codigo_barras = None
   producto = worksheet.cell(rx,1).value
   precio = None
   if type(worksheet.cell(rx,2).value) is float:
      precio = '$%.2f' % worksheet.cell(rx,2).value
   impresiones = 1
   if type(worksheet.cell(rx,3).value) is float:
      impresiones = worksheet.cell(rx,3).value
   label.print_product(producto,codigo_barras,precio,int(impresiones))

   

