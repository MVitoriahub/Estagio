from django.urls import path
from . import views

app_name = 'venda'

urlpatterns = [
    path('',                            views.listar,                name='listar'),
    path('nova/',                       views.nova,                  name='nova'),
    path('finalizar/',                  views.finalizar,             name='finalizar'),
    path('<int:pk>/visualizar/',        views.visualizar,            name='visualizar'),
    path('<int:pk>/editar/',            views.editar,                name='editar'),
    path('<int:pk>/excluir/',           views.excluir,               name='excluir'),
    path('remover-item/<int:item_pk>/', views.remover_item,          name='remover_item'),
    path('item/<int:item_pk>/editar/',  views.editar_item,           name='editar_item'),
    path('variacoes/',                  views.variacoes_por_produto, name='variacoes_por_produto'),
]