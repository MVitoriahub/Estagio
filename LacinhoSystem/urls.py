from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),

    path('clientes/', include('clientes.urls')),

    path('produto/', include ('produto.urls')),

    path('estoque/', include ('estoque.urls')),

]