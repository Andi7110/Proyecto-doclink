from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.forms import ValidationError
from django.utils import timezone
from django.core.validators import RegexValidator

class UsuarioManager(BaseUserManager):
    def create_user(self, user_name, password=None, **extra_fields):
        if not user_name:
            raise ValueError('El nombre de usuario es obligatorio')
        user = self.model(user_name=user_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(user_name, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.BigAutoField(primary_key=True)
    user_name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    
    # Campos requeridos por Django
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Tus campos originales
    sexo = models.CharField(max_length=1, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    status_plataforma = models.CharField(max_length=1, blank=True, null=True)
    fecha_registro = models.DateField(default=timezone.now)
    
    # Relaciones
    fk_rol = models.ForeignKey('Rol', models.DO_NOTHING, db_column='fk_rol', blank=True, null=True)
    fk_admin = models.ForeignKey('Admin', models.DO_NOTHING, db_column='fk_admin', blank=True, null=True)
    fk_paciente = models.ForeignKey('Paciente', models.DO_NOTHING, db_column='fk_paciente', blank=True, null=True)
    fk_medico = models.ForeignKey('Medico', models.DO_NOTHING, db_column='fk_medico', blank=True, null=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'user_name'
    REQUIRED_FIELDS = ['correo']  # Campos requeridos para createsuperuser
    
    def get_full_name(self):
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        elif self.nombre:
            return self.nombre
        return self.user_name

    class Meta:
        managed = True
        db_table = 'usuario'

    def get_rol(self):
        if self.fk_medico:
            return 'medico'
        elif self.fk_paciente:
            return 'paciente'
        elif self.fk_admin:
            return 'admin'
        return None

    def __str__(self):
        return f"{self.nombre} {self.apellido}" if self.nombre and self.apellido else self.user_name

    def get_rol(self):
        if self.fk_medico:
            return 'medico'
        elif self.fk_paciente:
            return 'paciente'
        elif self.fk_admin:
            return 'admin'
        return None

    def __str__(self):
        return f"{self.nombre} {self.apellido}" if self.nombre and self.apellido else self.user_name

class Admin(models.Model):
    id_admin = models.BigAutoField(primary_key=True)
    cargo = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'admin'
    
    def __str__(self):
        return f"Admin {self.id_admin}: {self.cargo}" if self.cargo else f"Admin {self.id_admin}"

class CitasMedicas(models.Model):
    id_cita_medicas = models.BigAutoField(primary_key=True)
    fecha_consulta = models.DateField(blank=True, null=True)
    status_cita_medica = models.TextField(blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    des_motivo_consulta_paciente = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    notas_medicas = models.TextField(blank=True, null=True)
    cancelado_por = models.CharField(max_length=10, blank=True, null=True, choices=[('medico', 'Médico'), ('paciente', 'Paciente')])
    fecha_cancelacion = models.DateTimeField(blank=True, null=True)
    fk_mensajes_notificacion = models.ForeignKey('MensajesNotificacion', models.DO_NOTHING, db_column='fk_mensajes_notificacion', blank=True, null=True)
    fk_factura = models.ForeignKey('Factura', models.DO_NOTHING, db_column='fk_factura', blank=True, null=True)
    fk_paciente = models.ForeignKey('Paciente', models.DO_NOTHING, db_column='fk_paciente', blank=True, null=True)
    fk_medico = models.ForeignKey('Medico', models.DO_NOTHING, db_column='fk_medico', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'citas_medicas'
        ordering = ['fecha_consulta', 'hora_inicio']

    def clean(self):
        if self.fk_paciente:
            usuario_paciente = self.fk_paciente.usuario_set.first()
            if usuario_paciente and usuario_paciente.get_rol() != 'paciente':
                raise ValidationError("El paciente asignado no tiene rol de paciente")

        if self.fk_medico:
            usuario_medico = self.fk_medico.usuario_set.first()
            if usuario_medico and usuario_medico.get_rol() != 'medico':
                raise ValidationError("El médico asignado no tiene rol de médico")

    def __str__(self):
        fecha = self.fecha_consulta.strftime("%d/%m/%Y") if self.fecha_consulta else "Sin fecha"
        hora = self.hora_inicio.strftime("%H:%M") if self.hora_inicio else ""
        paciente_str = f" - {self.fk_paciente}" if self.fk_paciente else ""
        medico_str = f" - {self.fk_medico}" if self.fk_medico else ""
        return f"Cita {self.id_cita_medicas} ({fecha} {hora}){paciente_str}{medico_str}"


class Clinica(models.Model):
    id_clinica = models.BigAutoField(primary_key=True)
    nombre = models.TextField(blank=True, null=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    sitio_web = models.TextField(blank=True, null=True)
    facebook = models.TextField(blank=True, null=True)
    instagram = models.TextField(blank=True, null=True)
    correo_electronico_clinica = models.TextField(blank=True, null=True)
    telefono_clinica = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'clinica'

    def __str__(self):
        return self.nombre if self.nombre else f"Clínica {self.id_clinica}"

class Factura(models.Model):
    id_factura = models.BigAutoField(primary_key=True)
    numero_factura = models.TextField(blank=True, null=True)
    fecha_emision = models.DateField(blank=True, null=True)
    fk_metodopago = models.ForeignKey('MetodosPago', models.DO_NOTHING, db_column='fk_metodopago', blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'factura'
    
    def __str__(self):
        num_fact = f" - N° {self.numero_factura}" if self.numero_factura else ""
        fecha = f" - {self.fecha_emision}" if self.fecha_emision else ""
        return f"Factura {self.id_factura}{num_fact}{fecha}"

class HorarioMedico(models.Model):
    id_horario_medico = models.BigAutoField(primary_key=True)
    status_disponibilidad = models.CharField(max_length=1, blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'horario_medico'
    
    def __str__(self):
        inicio = self.hora_inicio.strftime("%H:%M") if self.hora_inicio else "??:??"
        fin = self.hora_fin.strftime("%H:%M") if self.hora_fin else "??:??"
        return f"Horario {self.id_horario_medico}: {inicio} a {fin}"

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
        managed = True
        db_table = 'medico'
    
    def get_nombre_display(self):
        # Obtener a través de la relación inversa con Usuario
        try:
            usuario = self.usuario_set.first()
            if usuario and usuario.get_rol() == 'medico':
                return str(usuario)
        except:
            pass
        
        # Fallback a otros campos
        if self.descripcion:
            return f"Dr. {self.descripcion[:30]}"
        
        return f"Médico {self.id_medico}"
    
    def __str__(self):
        return self.get_nombre_display()
    
class MensajesNotificacion(models.Model):
    id_mensaje_notificacion = models.BigAutoField(primary_key=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'mensajes_notificacion'
    
    def __str__(self):
        desc = f": {self.descripcion[:30]}..." if self.descripcion else ""
        return f"Mensaje {self.id_mensaje_notificacion}{desc}"

class MetodosPago(models.Model):
    id_metodopago = models.BigAutoField(primary_key=True)
    tipometodopago = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'metodos_pago'
    
    def __str__(self):
        return self.tipometodopago if self.tipometodopago else f"Método pago {self.id_metodopago}"

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
    dui = models.CharField(max_length=10, unique=True, null=False, blank=False, default='00000000-0')


    class Meta:
        managed = True
        db_table = 'paciente'
    
    def get_nombre_display(self):
        # Obtener a través de la relación inversa con Usuario
        try:
            usuario = self.usuario_set.first()
            if usuario and usuario.get_rol() == 'paciente':
                return str(usuario)
        except:
            pass
        
        # Fallback a nombre_responsable
        if self.nombre_responsable:
            return self.nombre_responsable
        
        return f"Paciente {self.id_paciente}"
    
    def __str__(self):
        return self.get_nombre_display()

class RankingMedico(models.Model):
    id_ranking_medico = models.BigAutoField(primary_key=True)
    nivel_de_ranking = models.IntegerField(blank=True, null=True)
    fk_valoracion_consulta = models.ForeignKey('ValoracionConsulta', models.DO_NOTHING, db_column='fk_valoracion_consulta', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ranking_medico'
    
    def __str__(self):
        nivel = f" - Nivel {self.nivel_de_ranking}" if self.nivel_de_ranking else ""
        return f"Ranking {self.id_ranking_medico}{nivel}"

class RecetaMedica(models.Model):
    id_receta_medica = models.BigAutoField(primary_key=True)
    medicamento = models.TextField(blank=True, null=True)
    via_administracion = models.TextField(blank=True, null=True)
    dosis = models.TextField(blank=True, null=True)
    fecha_inicio_tratamiento = models.DateField(blank=True, null=True)
    fecha_fin_tratamiento = models.DateField(blank=True, null=True)
    fk_citas_medicas = models.ForeignKey(CitasMedicas, models.DO_NOTHING, db_column='fk_citas_medicas', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'receta_medica'
    
    def __str__(self):
        medicamento = f" - {self.medicamento}" if self.medicamento else ""
        cita = f" (Cita: {self.fk_citas_medicas})" if self.fk_citas_medicas else ""
        return f"Receta {self.id_receta_medica}{medicamento}{cita}"

class Rol(models.Model):
    id_rol = models.BigAutoField(primary_key=True)
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'rol'
    
    def __str__(self):
        return self.nombre if self.nombre else f"Rol {self.id_rol}"


class ValoracionConsulta(models.Model):
    id_valoracion_consulta = models.BigAutoField(primary_key=True)
    calificacion_consulta = models.IntegerField(blank=True, null=True)
    resena = models.TextField(blank=True, null=True)
    fk_cita = models.ForeignKey(CitasMedicas, models.DO_NOTHING, db_column='fk_cita', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'valoracion_consulta'

    def __str__(self):
        calificacion = f" - {self.calificacion_consulta}★" if self.calificacion_consulta else ""
        return f"Valoración {self.id_valoracion_consulta}{calificacion}"
    
    
class ConsultaMedica(models.Model):
    id_consulta_medica = models.BigAutoField(primary_key=True)
    fk_cita = models.OneToOneField(CitasMedicas, on_delete=models.CASCADE, db_column='fk_cita', related_name='consulta_medica')
    sintomas = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    tratamiento = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    documentos_adjuntos = models.FileField(upload_to='documentos/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # Campos para receta médica
    medicamento = models.TextField(blank=True, null=True)
    via_administracion = models.TextField(blank=True, null=True)
    dosis = models.TextField(blank=True, null=True)
    fecha_inicio_tratamiento = models.DateField(blank=True, null=True)
    fecha_fin_tratamiento = models.DateField(blank=True, null=True)
    archivos_receta = models.FileField(upload_to='recetas/', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'consulta_medica'

    def __str__(self):
               return f"Consulta asociada a cita {self.fk_cita.id_cita_medicas}"

    def tiene_receta(self):
        return bool(self.medicamento or self.via_administracion or self.dosis)

class PolizaSeguro(models.Model):
    id = models.BigAutoField(primary_key=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='polizas')
    compania_aseguradora = models.CharField(max_length=150)
    numero_poliza = models.CharField(max_length=50, unique=True)
    fecha_vigencia = models.DateField()
    tipo_cobertura = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'bd_polizaseguro'
        verbose_name = "Póliza de Seguro"
        verbose_name_plural = "Pólizas de Seguros"

    def __str__(self):
        return f"{self.compania_aseguradora} - {self.numero_poliza}"
    

class ContactoEmergencia(models.Model):
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, related_name='contactos_emergencia')
    nombre_completo = models.CharField(max_length=150)
    parentesco = models.CharField(max_length=50)
    telefono = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?\d{7,15}$', 'Ingrese un número de teléfono válido.')]
    )
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre_completo} ({self.parentesco})"

class SeguimientoClinico(models.Model):
    id_seguimiento_clinico = models.BigAutoField(primary_key=True)
    fk_cita = models.ForeignKey(CitasMedicas, on_delete=models.CASCADE, db_column='fk_cita', related_name='seguimientos')
    fk_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, db_column='fk_paciente')
    fk_medico = models.ForeignKey(Medico, on_delete=models.CASCADE, db_column='fk_medico')
    diagnostico_final = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    tratamiento = models.TextField(blank=True, null=True)
    # Campos para receta médica
    medicamento = models.TextField(blank=True, null=True)
    dosis = models.TextField(blank=True, null=True)
    frecuencia = models.TextField(blank=True, null=True)  # e.g., "cada 8 horas"
    duracion = models.TextField(blank=True, null=True)  # e.g., "7 días"
    archivos_receta = models.FileField(upload_to='recetas_seguimiento/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # Para programar nueva consulta de seguimiento
    programar_nueva_consulta = models.BooleanField(default=False)
    fecha_nueva_consulta = models.DateField(blank=True, null=True)
    hora_nueva_consulta = models.TimeField(blank=True, null=True)
    notas_nueva_consulta = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'seguimiento_clinico'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Seguimiento {self.id_seguimiento_clinico} - Paciente: {self.fk_paciente} - Médico: {self.fk_medico}"

    def tiene_receta(self):
        return bool(self.medicamento or self.dosis or self.frecuencia or self.duracion)


class ConsultaSeguimiento(models.Model):
    id_consulta_seguimiento = models.BigAutoField(primary_key=True)
    fk_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, db_column='fk_paciente')
    fk_medico = models.ForeignKey(Medico, on_delete=models.CASCADE, db_column='fk_medico')
    fk_seguimiento_anterior = models.ForeignKey(SeguimientoClinico, on_delete=models.SET_NULL, blank=True, null=True, db_column='fk_seguimiento_anterior', related_name='consultas_seguimiento')
    # Campos de la consulta de seguimiento
    sintomas_actuales = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    tratamiento = models.TextField(blank=True, null=True)
    comparacion_primera_consulta = models.TextField(blank=True, null=True)
    mejoro_salud = models.CharField(max_length=1, choices=[('S', 'Sí'), ('N', 'No'), ('P', 'Parcialmente')], blank=True, null=True)
    necesita_receta_diferente = models.BooleanField(default=False)
    # Campos para receta médica
    medicamento = models.TextField(blank=True, null=True)
    dosis = models.TextField(blank=True, null=True)
    frecuencia = models.TextField(blank=True, null=True)
    duracion = models.TextField(blank=True, null=True)
    archivos_receta = models.FileField(upload_to='recetas_consulta_seguimiento/', blank=True, null=True)
    documentos_adjuntos = models.FileField(upload_to='documentos_seguimiento/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # Estado de la consulta
    consulta_completada = models.BooleanField(default=False)
    fecha_completada = models.DateTimeField(blank=True, null=True)
    # Programar nueva cita de seguimiento
    programar_nueva_cita = models.BooleanField(default=False)
    fecha_nueva_cita = models.DateField(blank=True, null=True)
    hora_nueva_cita = models.TimeField(blank=True, null=True)
    motivo_nueva_cita = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'consulta_seguimiento'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Consulta Seguimiento {self.id_consulta_seguimiento} - Paciente: {self.fk_paciente} - Médico: {self.fk_medico}"

    def tiene_receta(self):
        return bool(self.medicamento or self.dosis or self.frecuencia or self.duracion)

    def completar_consulta(self):
        self.consulta_completada = True
        self.fecha_completada = timezone.now()
        self.save()

