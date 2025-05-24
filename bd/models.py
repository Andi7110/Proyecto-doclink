# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Admin(models.Model):
    id_admin = models.BigAutoField(primary_key=True)
    cargo = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin'


class CitasMedicas(models.Model):
    id_cita_medicas = models.BigAutoField(primary_key=True)
    fecha_consulta = models.DateField(blank=True, null=True)
    status_cita_medica = models.TextField(blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    des_motivo_consulta_paciente = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    notas_medicas = models.TextField(blank=True, null=True)
    fk_mensajes_notificacion = models.ForeignKey('MensajesNotificacion', models.DO_NOTHING, db_column='fk_mensajes_notificacion', blank=True, null=True)
    fk_factura = models.ForeignKey('Factura', models.DO_NOTHING, db_column='fk_factura', blank=True, null=True)
    fk_paciente = models.ForeignKey('Paciente', models.DO_NOTHING, db_column='fk_paciente', blank=True, null=True)
    fk_medico = models.ForeignKey('Medico', models.DO_NOTHING, db_column='fk_medico', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'citas_medicas'


class Clinica(models.Model):
    id_clinica = models.BigAutoField(primary_key=True)
    nombre = models.TextField(blank=True, null=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    sitio_web = models.TextField(blank=True, null=True)
    facebook = models.TextField(blank=True, null=True)
    instagram = models.TextField(blank=True, null=True)
    correo_electronico_clinica = models.TextField(blank=True, null=True)
    telefono_clinica = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clinica'


class Factura(models.Model):
    id_factura = models.BigAutoField(primary_key=True)
    numero_factura = models.TextField(blank=True, null=True)
    fecha_emision = models.DateField(blank=True, null=True)
    fk_metodopago = models.ForeignKey('MetodosPago', models.DO_NOTHING, db_column='fk_metodopago', blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'factura'


class HorarioMedico(models.Model):
    id_horario_medico = models.BigAutoField(primary_key=True)
    status_disponibilidad = models.CharField(max_length=1, blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'horario_medico'


class Medico(models.Model):
    id_medico = models.BigAutoField(primary_key=True)
    dui = models.TextField(blank=True, null=True)
    no_jvpm = models.TextField(blank=True, null=True)
    especialidad = models.TextField(blank=True, null=True)
    sub_especialidad_1 = models.TextField(blank=True, null=True)
    sub_especialidad_2 = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fk_horario_medico = models.ForeignKey(HorarioMedico, models.DO_NOTHING, db_column='fk_horario_medico', blank=True, null=True)
    fk_clinica = models.ForeignKey(Clinica, models.DO_NOTHING, db_column='fk_clinica', blank=True, null=True)
    fk_ranking_medico = models.ForeignKey('RankingMedico', models.DO_NOTHING, db_column='fk_ranking_medico', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'medico'


class MensajesNotificacion(models.Model):
    id_mensaje_notificacion = models.BigAutoField(primary_key=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mensajes_notificacion'


class MetodosPago(models.Model):
    id_metodopago = models.BigAutoField(primary_key=True)
    tipometodopago = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'metodos_pago'


class Paciente(models.Model):
    id_paciente = models.BigAutoField(primary_key=True)
    tel_emergencia = models.TextField(blank=True, null=True)
    contacto_emergencia = models.TextField(blank=True, null=True)
    poliza_vigente = models.CharField(max_length=1, blank=True, null=True)
    no_carne_poliza = models.TextField(blank=True, null=True)
    no_poliza = models.TextField(blank=True, null=True)
    nombre_aseguradora = models.TextField(blank=True, null=True)
    nombre_responsable = models.TextField(blank=True, null=True)
    fk_cuadro_clinico = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'paciente'


class RankingMedico(models.Model):
    id_ranking_medico = models.BigAutoField(primary_key=True)
    nivel_de_ranking = models.IntegerField(blank=True, null=True)
    fk_valoracion_consulta = models.ForeignKey('ValoracionConsulta', models.DO_NOTHING, db_column='fk_valoracion_consulta', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ranking_medico'


class RecetaMedica(models.Model):
    id_receta_medica = models.BigAutoField(primary_key=True)
    medicamento = models.TextField(blank=True, null=True)
    via_administracion = models.TextField(blank=True, null=True)
    dosis = models.TextField(blank=True, null=True)
    fecha_inicio_tratamiento = models.DateField(blank=True, null=True)
    fecha_fin_tratamiento = models.DateField(blank=True, null=True)
    fk_citas_medicas = models.ForeignKey(CitasMedicas, models.DO_NOTHING, db_column='fk_citas_medicas', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'receta_medica'


class Rol(models.Model):
    id_rol = models.BigAutoField(primary_key=True)
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rol'


class Usuario(models.Model):
    id_usuario = models.BigAutoField(primary_key=True)
    user_name = models.TextField()
    password = models.TextField()
    sexo = models.CharField(max_length=1, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    nombre = models.TextField(blank=True, null=True)
    apellido = models.TextField(blank=True, null=True)
    correo = models.TextField(blank=True, null=True)
    departamento = models.TextField(blank=True, null=True)
    municipio = models.TextField(blank=True, null=True)
    telefono = models.TextField(blank=True, null=True)
    status_plataforma = models.CharField(max_length=1, blank=True, null=True)
    fecha_registro = models.DateField(blank=True, null=True)
    fk_rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='fk_rol', blank=True, null=True)
    fk_admin = models.ForeignKey(Admin, models.DO_NOTHING, db_column='fk_admin', blank=True, null=True)
    fk_paciente = models.ForeignKey(Paciente, models.DO_NOTHING, db_column='fk_paciente', blank=True, null=True)
    fk_medico = models.ForeignKey(Medico, models.DO_NOTHING, db_column='fk_medico', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario'


class ValoracionConsulta(models.Model):
    id_valoracion_consulta = models.BigAutoField(primary_key=True)
    calificacion_consulta = models.IntegerField(blank=True, null=True)
    resena = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'valoracion_consulta'
