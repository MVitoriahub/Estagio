from django.urls import path
from . import views          # ← deve ser assim, e não "from .templates import views"

app_name = 'relatorios'

urlpatterns = [
    path('', views.relatorios_home, name='home'),
    path('<str:tipo>/periodo/', views.escolher_periodo, name='periodo'),
    path('<str:tipo>/gerar/', views.gerar_relatorio, name='gerar'),
    path('dashboard/', views.dashboard, name='dashboard'),
]