from django.urls import path
from . import views
from .views import views_home
from .views import receta_medica
from .views import ubicacion_doctor
from .views import clinica_doctor
from .views import config_clinica
from .views import config_horario
from .views import config_perfildoc



urlpatterns = [
    path('home/', views_home, name='home'),
     path('dashboard_doctor/', views.dashboard_doctor, name='dashboard_doctor'),
    path('receta_medica/', views.receta_medica, name='receta_medica'),
    path('ubicacion_doctor/', views.ubicacion_doctor, name='ubicacion_doctor'),
    path('clinica_doctor/', views.clinica_doctor, name='clinica_doctor'),
    path('config_clinica/', views.config_clinica, name='config_clinica'),
    path('config_horario/', views.config_horario, name='config_horario'),
    path('config_perfildoc/', views.config_perfildoc, name='config_perfildoc'),
    path('actualizar-cita/<int:cita_id>/', views.actualizar_estado_cita, name='actualizar_estado_cita'),
    path('actualizar-fecha-hora/<int:cita_id>/', views.actualizar_fecha_hora_cita, name='actualizar_fecha_hora_cita'),
    path('realizar-consulta/<int:cita_id>/', views.realizar_consulta, name='realizar_consulta'),
    path('programar_cita_doc/', views.programar_cita_doc, name='programar_cita_doc'),
    path('ver-diagnostico/<int:cita_id>/', views.ver_diagnostico_medico, name='ver_diagnostico_medico'),
    path('agenda/', views.agenda_medico, name='agenda_medico'),
    path('crear-seguimiento/<int:cita_id>/', views.crear_seguimiento, name='crear_seguimiento'),
    path('ver-seguimientos/<int:paciente_id>/', views.ver_seguimientos_paciente, name='ver_seguimientos_paciente'),
    path('crear-consulta-seguimiento/', views.crear_consulta_seguimiento, name='crear_consulta_seguimiento'),
    path('crear-consulta-seguimiento/<int:seguimiento_id>/', views.crear_consulta_seguimiento, name='crear_consulta_seguimiento_con_anterior'),
    path('crear-consulta-seguimiento-paciente/<int:paciente_id>/', views.crear_consulta_seguimiento, name='crear_consulta_seguimiento_paciente'),
    path('ver-consultas-seguimiento/', views.ver_consultas_seguimiento, name='ver_consultas_seguimiento'),
    path('descargar-archivo/<int:consulta_id>/<str:tipo>/', views.descargar_archivo_base64, name='descargar_archivo_base64'),
    path('historial-facturas/', views.historial_facturas, name='historial_facturas'),
    path('historial-pagos/', views.historial_pagos, name='historial_pagos'),
    path('gastos-adicionales/<int:cita_id>/', views.gestionar_gastos_adicionales, name='gestionar_gastos_adicionales'),
    path('editar-gasto/<int:gasto_id>/', views.editar_gasto_adicional, name='editar_gasto_adicional'),
    path('eliminar-gasto/<int:gasto_id>/', views.eliminar_gasto_adicional, name='eliminar_gasto_adicional'),
    path('marcar-gasto-pagado/<int:gasto_id>/', views.marcar_gasto_pagado, name='marcar_gasto_pagado'),
    path('generar-pdf/<int:factura_id>/', views.generar_pdf_factura, name='generar_pdf_factura'),
]

