from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_jefatura, name='login_jefatura'),
    path('logout/', views.logout_jefatura, name='logout_jefatura'),
    path('', views.listado_cajeros, name='listado_cajeros'),
    path('ingresar/', views.crear_cajero, name='crear_cajero'),
    path('editar/<int:pk>/', views.editar_cajero, name='editar_cajero'),
    path('eliminar/<int:pk>/', views.eliminar_cajero, name='eliminar_cajero'),
    path('colacion/<int:pk>/', views.cambiar_colacion, name='cambiar_colacion'),
    path('reanudar/<int:pk>/', views.reanudar_turno, name='reanudar_turno'),
    path('cierre-general/', views.cierre_general_jornada, name='cierre_general_jornada'),
    path('auditoria/', views.historial_auditoria, name='historial_auditoria'),
    path('auditoria/exportar/', views.exportar_csv, name='exportar_csv'),
]