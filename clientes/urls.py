from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_clientes, name='listar_clientes'),
    path('criar/', views.criar_cliente, name='criar_cliente'),

    path('<int:id>/', views.visualizar_cliente, name='visualizar_cliente'),
    path('<int:id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('<int:id>/excluir/', views.excluir_cliente, name='excluir_cliente'),
]