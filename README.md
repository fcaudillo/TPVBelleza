# TPVBelleza git config --global http.sslverify false 
DOCUMENTGACION DEL DATABLE

https://bootstrap-table.wenzhixin.net.cn/documentation/

./manage.py makemigrations
./manage.py migrate
./manage.py makemigrations precios 

Cuando no queria reconstruir las tablas de precios
edite el archivo precios/migrations/0001_initial.py y borre managed = False y
volvi a correr

./manage.py sqlmigrate precios 001_initial
./manage.py makemigrations precios
./manage.py migrate precios 0001_initial

modi
 pip install -r requirements.txt
   37  cd ..
   38  ls
   39  cd consultaprecio/
   40  ./manage.py runserver 0.0.0.0:8000
   41  cat manage.py
   42  chmod +x manage.py
   43  ./manage.py runserver 0.0.0.0:8000
   44  pip install Django
   45  pip install djangorestframework
   46  ./manage.py runserver 0.0.0.0:8000
   47  pip install Django
   48  pip install Django==1.11
   49  ./manage.py runserver 0.0.0.0:8000

 python manage.py shell  //y poder usar los modelos en modo interactivo.

Para construir la imagen desde  Dockerfile.
docker build -t  tpv-verde 

Para ejecutarlo.

docker run -p 9000:8000 -detach  tpv-verde.

Para subirla tenemos:
docker login -u fcaudillo
docker push docker.io/fcaudillo/tpv-verde:latest

select cast(cast("codigoInterno" as integer) as varchar) from precios_producto where "codigoInterno" = '1'

update precios_producto set "codigoInterno" = cast(cast("codigoInterno" as float) as varchar) where "codigoInterno" != ''

 ./manage.py runserver 0.0.0.0:9000

docker cp css/* dev-verde:/app/app/TPVBelleza/consultaprecio/static/precio/css
docker cp js/* dev-verde:/app/app/TPVBelleza/consultaprecio/static/precio/js
docker cp index.html dev-verde:/app/app/TPVBelleza/consultaprecio/precios/templates/precios/puntoventa.html

./manage.py shell
y ya adentro ejecutar esto.
execfile('./precios/LoadCatalogoProv.py')
