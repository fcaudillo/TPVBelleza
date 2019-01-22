"""consultaprecio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from precios.views import FindProductView, FindView, ChangeProductView,PrintLabelView,ImportCatalogView
from precios.views import find_consulta, find_all, guarda_ticket, guarda_producto, genera_etiquetas, download, upload_file, login_view, logout_view
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^admin/', admin.site.urls),
	url('find/(?P<barcode>\w+)/$',find_consulta, name='find'),
        url('download/$',download, name='download'),
	url('find/$',find_all, name='find_all'),
	url('tickets/add',guarda_ticket, name='ticket_add'),
        url('producto/add',guarda_producto,name='producto_add'),
        url('genera_etiquetas',genera_etiquetas,name='genera_etiquetas'),
	url('encuentra/(?P<barcode>\w+)/$',FindView.as_view(),name='encuentra'),
	url(r'consulta/',login_required(FindProductView.as_view()),name='consulta'),
	url(r'cambioprecio/',login_required(ChangeProductView.as_view()),name='cambioprecio'),
        url(r'importar',login_required(ImportCatalogView.as_view()),name='importar'),
        url(r'subir_archivo',upload_file, name='subir_archivo'),
        url(r'login',login_view, name='login'),
        url(r'logout',logout_view, name='logout'),
        url(r'impresion/',login_required(PrintLabelView.as_view()),name='impresion')
]
