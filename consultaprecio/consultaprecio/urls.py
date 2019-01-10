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
from precios.views import FindProductView, FindView, LoadDataView,ChangeProductView
from precios.views import find_consulta, find_all, guarda_ticket, guarda_producto


urlpatterns = [
    url(r'^admin/', admin.site.urls),
	url(r'loaddata/',LoadDataView.as_view()),
	url('find/(?P<barcode>\w+)/$',find_consulta),
	url('find/$',find_all),
	url('tickets/add',guarda_ticket),
        url('producto/add',guarda_producto),
	url('encuentra/(?P<barcode>\w+)/$',FindView.as_view()),
	url(r'consulta/',FindProductView.as_view()),
	url(r'cambioprecio/',ChangeProductView.as_view())
]
