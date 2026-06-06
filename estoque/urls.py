from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    path('',                        views.listar,        name='listar'),
    path('<int:pk>/movimentacoes/', views.movimentacoes, name='movimentacoes'),
    path('<int:pk>/registrar/',     views.registrar,     name='registrar'),
    path('nova-variacao/<int:produto_pk>/', views.nova_variacao, name='nova_variacao'),
]