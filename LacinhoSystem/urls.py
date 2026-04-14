from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # 👇 só isso!
    path('clientes/', include('clientes.urls')),
]