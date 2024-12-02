from django.urls import path
from . import views  
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

from .views import (
    inicio,
    registrar_propietario,
    registrar_mascota,
    registrar_especie,
    registrar_vacuna,
    buscar_mascota,
    consultar_carnet,
)

def logout_then_redirect(request):
    auth_views.LogoutView.as_view()(request)  # Cierra la sesión
    return redirect('inicio')  # Redirige al inicio

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('registrar-propietario/', views.registrar_propietario, name='registrar_propietario'),
    path('registrar-mascota/', views.registrar_mascota, name='registrar_mascota'),
    path('registrar-especie/', views.registrar_especie, name='registrar_especie'),
    path('registrar-vacuna/', views.registrar_vacuna, name='registrar_vacuna'),
    path('buscar-mascota/', views.buscar_mascota, name='buscar_mascota'),
    path('consultar-carnet/', views.consultar_carnet, name='consultar_carnet'),
    path('carnet_mascota/<int:mascota_id>/', views.carnet_mascota, name='detalle_carnet_mascota'),  # Cambié el nombre aquí
    path('descargar_carnet_pdf/<int:mascota_id>/', views.descargar_carnet_pdf, name='descargar_carnet_pdf'),
    path('consultar-carnet/<int:mascota_id>/', views.carnet_mascota, name='carnet_por_mascota'),  # Cambié el nombre aquí
    path('registrar-cita/', views.registrar_cita, name='registrar_cita'),
    path('servicios/', views.servicios, name='servicios'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('clientes/', views.clientes, name='clientes'),
    path('admin/logout/', logout_then_redirect, name='custom_admin_logout'),
]
