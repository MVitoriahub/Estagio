# produto/urls.py
from django.urls import path
from . import views

app_name = 'produto'

urlpatterns = [
    path('',                      views.listar,     name='listar'),
    path('criar/',                views.criar,      name='criar'),
    path('<int:pk>/',             views.visualizar, name='visualizar'),
    path('<int:pk>/editar/',      views.editar,     name='editar'),
    path('<int:pk>/excluir/',     views.excluir,    name='excluir'),
    ]