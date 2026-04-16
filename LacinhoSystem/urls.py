from django.contrib import admin
from django.urls import path, include #Criar rotas

urlpatterns = [
    path('admin/', admin.site.urls),

    path('clientes/', include('clientes.urls')),
]