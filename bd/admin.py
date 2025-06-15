from django.contrib import admin
from .models import (
    Admin, CitasMedicas, Clinica, Factura, HorarioMedico, Medico,
    MensajesNotificacion, MetodosPago, Paciente, RankingMedico,
    RecetaMedica, Rol, Usuario, ValoracionConsulta
)

@admin.register(CitasMedicas)
class CitasMedicasAdmin(admin.ModelAdmin):
    list_display = ('id_cita_medicas', 'fecha_consulta', 'status_cita_medica', 'fk_paciente', 'fk_medico')
    list_filter = ('status_cita_medica', 'fecha_consulta')
    search_fields = ('diagnostico', 'notas_medicas')
    raw_id_fields = ('fk_paciente', 'fk_medico')

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('id_medico', 'especialidad', 'fk_clinica', 'fk_ranking_medico')
    search_fields = ('especialidad', 'sub_especialidad_1', 'sub_especialidad_2')
    list_filter = ('especialidad', 'fk_clinica')

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('id_paciente', 'contacto_emergencia', 'poliza_vigente', 'nombre_aseguradora')
    search_fields = ('contacto_emergencia', 'nombre_aseguradora')
    list_filter = ('poliza_vigente',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'user_name', 'nombre', 'apellido', 'correo', 'fk_rol')
    search_fields = ('user_name', 'nombre', 'apellido', 'correo')
    list_filter = ('fk_rol', 'status_plataforma')

# Registro de los demás modelos con configuración básica
admin.site.register(Admin)
admin.site.register(Clinica)
admin.site.register(Factura)
admin.site.register(HorarioMedico)
admin.site.register(MensajesNotificacion)
admin.site.register(MetodosPago)
admin.site.register(RankingMedico)
admin.site.register(RecetaMedica)
admin.site.register(Rol)
admin.site.register(ValoracionConsulta)