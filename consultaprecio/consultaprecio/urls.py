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
from precios.views import FindProductView, FindView, ChangeProductView,PrintLabelView,ImportCatalogView, RecargaTaeView,ReporteRecargaView, RecargaDatosTaeView
from precios.views import generar_codigo_barras, find_consulta, find_all, guarda_ticket, guarda_producto, genera_etiquetas,genera_etiquetas_mediana, download, upload_file, login_view, logout_view, resumen_movimiento, reporte_diario, recargatae , recargas_periodo, obtenerSaldo, find_products, on_line, reporte_vtadet, rep_vtadet, catalogo_productos, upload_catalogo_proveedor
from precios.views import PuntoVentaView, ImportCatalogProveedorView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^admin/', admin.site.urls),
        url('generar_codigo_barras/(?P<prefijo>\w+)/$',generar_codigo_barras, name='generar_codigo_barras'),
        url('recargatae/(?P<compania>\w+)/(?P<plan>\w+)/(?P<numero>\w+)/(?P<monto>\w+)/$',recargatae, name='recargatae'),
        url('recarga/$',login_required(RecargaTaeView.as_view()), name='recarga'),
        url('puntoventa/$',login_required(PuntoVentaView.as_view()), name='puntoventa'),
        url('on_line/$',on_line, name='on_line'),
        url('obtenerSaldo/$',obtenerSaldo,name='obtenerSaldo'),
        url('recargadatos/$',login_required(RecargaDatosTaeView.as_view()), name='recargadatos'),
        url('reporte_recargas/$',login_required(ReporteRecargaView.as_view()),name='reporte_recargas'),
	url('find_codigo/(?P<barcode>\w+)/$',find_consulta, name='find_codigo'),
        url('resumenmovimiento/(?P<fechaIni>\w+)/(?P<fechaFin>\w+)/$',resumen_movimiento, name='resumen_movimiento'),
        url('reporte_vtadet/(?P<fechaIni>\w+)/(?P<fechaFin>\w+)/$',reporte_vtadet, name='reporte_vtadet'),
        url('download/$',download, name='download'),
        url('recargas_periodo/(?P<fechaIni>\w+)/(?P<fechaFin>\w+)/$',recargas_periodo, name='recargas_periodo'),
        url('reportediario/$',reporte_diario, name='reporte_diario'),
        url('rep_vtadet/$',rep_vtadet, name='rep_vtadet'),
	url('find/$',find_all, name='find_all'),
        url('catalogo_productos/$',catalogo_productos,name='catalogo_productos'),
        url('find_products/',find_products,name='find_products'),
	url('tickets/add',guarda_ticket, name='ticket_add'),
        url('producto/add',guarda_producto,name='producto_add'),
        url('genera_etiquetas/$',genera_etiquetas,name='genera_etiquetas'),
        url('genera_etiquetas_mediana/$',genera_etiquetas_mediana,name='genera_etiquetas_mediana'),
	url('encuentra/(?P<barcode>\w+)/$',FindView.as_view(),name='encuentra'),
	url(r'consulta/',login_required(FindProductView.as_view()),name='consulta'),
	url(r'cambioprecio/',login_required(ChangeProductView.as_view()),name='cambioprecio'),
        url(r'importar/$',login_required(ImportCatalogView.as_view()),name='importar'),
        url(r'importarproveedor/$',login_required(ImportCatalogProveedorView.as_view()),name='importarproveedor'),
        url(r'subir_archivo$',upload_file, name='subir_archivo'),
        url(r'subir_archivo_proveedor$',upload_catalogo_proveedor, name='subir_archivo_proveedor'),
        url(r'login',login_view, name='login'),
        url(r'logout',logout_view, name='logout'),
        url(r'impresion/',login_required(PrintLabelView.as_view()),name='impresion')
]

