from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_admin, name='login_admin'),
    path('registro/', views.registro_admin, name='registro_admin'),
    path('logout/', views.logout_admin, name='logout_admin'),
    path('recuperar-contraseña/', views.recuperar_contraseña, name='recuperar_contraseña'),
    path('cambiar-contraseña/', views.cambiar_contraseña, name='cambiar_contraseña'),
    
    # Vistas principales
    path('', views.inicio, name='inicio'),
    path('clientes/', views.clientes, name='clientes'), 
    path('empleados/', views.empleados, name='empleados'),
    path('mesas/', views.mesas, name='mesas'),
    path('platos/', views.platos, name='platos'),
    path('ordenes/', views.ordenes, name='ordenes'),
    path('facturas/', views.facturas, name='facturas'),
]