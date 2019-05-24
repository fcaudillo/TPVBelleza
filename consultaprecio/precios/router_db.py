from precios.models import TipoMovimiento, Movimiento, Categoria, Compania, Plan, Recarga
import os

#ROUTED_MODELS = [Movimiento, DetalleMovimiento,TipoMovimiento,Categoria,Compania,Plan,Recarga]
db_name = os.environ.get('CLIENTE_ID') 

class MyDbRouter(object):
   def db_for_read(self,model,**hints):
     print ("estoy en db_for_read")
     return db_name

   def db_for_write(self,model,**hints):
     print ("Estoy en db_for_write")
     return db_name
      
