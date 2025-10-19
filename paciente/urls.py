from django.urls import path
from . import views
from .views import views_home



urlpatterns = [
    path('home/', views_home, name='home'),
    path('dashboard_paciente/', views.dashboard_paciente, name='dashboard_paciente'),
    path('agendar_cita/', views.agendar_cita, name='agendar_cita'),
    path('agenda/', views.ver_agenda, name='agenda'),
    path('paciente/agregar-poliza/', views.agregar_poliza, name='agregar_poliza'),
    path('contacto-emergencia/', views.gestionar_contacto_emergencia, name='contacto_emergencia'),
    path("buscar-medicos/", views.buscar_medicos, name="buscar_medicos"),
    path('mapa-medicos/', views.mapa_medicos, name='mapa_medicos'),
    path('ranking_medico/', views.ranking_medico, name='ranking_medico'),
    path('calificar_medico/<int:cita_id>/', views.calificar_cita, name='calificar_medico'),
    path('ver_diagnostico/<int:cita_id>/', views.ver_diagnostico, name='ver_diagnostico'),
    path('pagar_gastos_adicionales/<int:cita_id>/', views.pagar_gastos_adicionales, name='pagar_gastos_adicionales'),
    path('cancelar_cita/<int:cita_id>/', views.cancelar_cita, name='cancelar_cita'),
    path('ver_recetas/', views.ver_recetas, name='ver_recetas'),
    path('generar_pdf_receta/<int:cita_id>/', views.generar_pdf_receta, name='generar_pdf_receta'),
    path('config_perfil_paciente/', views.config_perfil_paciente, name='config_perfil_paciente'),
    path('historial-facturas/', views.historial_facturas_paciente, name='historial_facturas_paciente'),
    path('generar-pdf/<int:factura_id>/', views.generar_pdf_factura_paciente, name='generar_pdf_factura_paciente'),
    path('historial-pagos/', views.historial_pagos_paciente, name='historial_pagos_paciente'),
    path('pagar-consulta/<int:cita_id>/', views.pagar_consulta_historial, name='pagar_consulta_historial'),
    path('pagar-gasto/<int:gasto_id>/', views.pagar_gasto_historial, name='pagar_gasto_historial'),

]