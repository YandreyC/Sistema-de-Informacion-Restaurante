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
    path('clientes/crear/', views.clientes_crear, name='clientes_crear'),
    path('clientes/<int:pk>/editar/', views.clientes_editar, name='clientes_editar'),
    path('clientes/<int:pk>/eliminar/', views.clientes_eliminar, name='clientes_eliminar'),
    path('empleados/', views.empleados, name='empleados'),
    path('empleados/crear/', views.empleados_crear, name='empleados_crear'),
    path('empleados/<int:pk>/editar/', views.empleados_editar, name='empleados_editar'),
    path('empleados/<int:pk>/eliminar/', views.empleados_eliminar, name='empleados_eliminar'),
    path('mesas/', views.mesas, name='mesas'),
    path('mesas/crear/', views.mesas_crear, name='mesas_crear'),
    path('mesas/<int:pk>/editar/', views.mesas_editar, name='mesas_editar'),
    path('mesas/<int:pk>/eliminar/', views.mesas_eliminar, name='mesas_eliminar'),
    path('platos/', views.platos, name='platos'),
    path('platos/crear/', views.platos_crear, name='platos_crear'),
    path('platos/<int:pk>/editar/', views.platos_editar, name='platos_editar'),
    path('platos/<int:pk>/eliminar/', views.platos_eliminar, name='platos_eliminar'),
    path('ordenes/', views.ordenes, name='ordenes'),
    path('ordenes/crear/', views.ordenes_crear, name='ordenes_crear'),
    path('ordenes/<int:pk>/editar/', views.ordenes_editar, name='ordenes_editar'),
    path('ordenes/<int:pk>/eliminar/', views.ordenes_eliminar, name='ordenes_eliminar'),
    path('facturas/', views.facturas, name='facturas'),
    path('facturas/crear/', views.facturas_crear, name='facturas_crear'),
    path('facturas/<int:pk>/editar/', views.facturas_editar, name='facturas_editar'),
    path('facturas/<int:pk>/eliminar/', views.facturas_eliminar, name='facturas_eliminar'),
]