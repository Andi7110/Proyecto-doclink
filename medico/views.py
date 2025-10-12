from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.db import connection, transaction
from collections import namedtuple
from django.db.models import Sum
from django.utils import timezone
from datetime import date, timedelta

from bd.models import RecetaMedica, CitasMedicas, Clinica, HorarioMedico, Medico, Usuario, Paciente, ValoracionConsulta, ConsultaMedica, SeguimientoClinico, ConsultaSeguimiento, GastosAdicionales
from .forms import PerfilMedicoForm, SeguimientoClinicoForm, ProgramarCitaSeguimientoForm
from bd.models import RecetaMedica, CitasMedicas, Clinica, HorarioMedico, Medico, Usuario, Paciente, ValoracionConsulta, ConsultaMedica
from .forms import PerfilMedicoForm

def detectar_tipo_archivo_base64(base64_data):
    """
    Detecta el tipo de archivo desde datos base64
    """
    try:
        import base64
        file_data = base64.b64decode(base64_data)

        # Detectar por magic bytes
        if file_data.startswith(b'\xff\xd8\xff'):  # JPEG
            return {'tipo': 'imagen', 'formato': 'JPEG', 'icono': 'bi-file-earmark-image', 'clase': 'text-primary'}
        elif file_data.startswith(b'\x89PNG'):  # PNG
            return {'tipo': 'imagen', 'formato': 'PNG', 'icono': 'bi-file-earmark-image', 'clase': 'text-primary'}
        elif file_data.startswith(b'GIF87a') or file_data.startswith(b'GIF89a'):  # GIF
            return {'tipo': 'imagen', 'formato': 'GIF', 'icono': 'bi-file-earmark-image', 'clase': 'text-primary'}
        elif file_data.startswith(b'BM'):  # BMP
            return {'tipo': 'imagen', 'formato': 'BMP', 'icono': 'bi-file-earmark-image', 'clase': 'text-primary'}
        elif file_data.startswith(b'RIFF') and file_data[8:12] == b'WEBP':  # WebP
            return {'tipo': 'imagen', 'formato': 'WebP', 'icono': 'bi-file-earmark-image', 'clase': 'text-primary'}
        elif file_data.startswith(b'%PDF'):  # PDF
            return {'tipo': 'documento', 'formato': 'PDF', 'icono': 'bi-file-earmark-pdf', 'clase': 'text-danger'}
        elif file_data.startswith(b'PK\x03\x04'):  # ZIP/DOCX/XLSX
            # Verificar contenido interno para determinar tipo específico
            file_content = file_data.decode('latin-1', errors='ignore')
            if '[Content_Types].xml' in file_content:
                if 'word/' in file_content:
                    return {'tipo': 'documento', 'formato': 'Word', 'icono': 'bi-file-earmark-word', 'clase': 'text-primary'}
                elif 'xl/' in file_content or 'worksheets' in file_content:
                    return {'tipo': 'documento', 'formato': 'Excel', 'icono': 'bi-file-earmark-excel', 'clase': 'text-success'}
                elif 'ppt/' in file_content:
                    return {'tipo': 'documento', 'formato': 'PowerPoint', 'icono': 'bi-file-earmark-ppt', 'clase': 'text-warning'}
            return {'tipo': 'archivo', 'formato': 'ZIP', 'icono': 'bi-file-earmark-zip', 'clase': 'text-muted'}
        elif file_data.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):  # DOC/XLS antiguos (OLE2)
            # Intentar identificar por contenido
            if b'WordDocument' in file_data:
                return {'tipo': 'documento', 'formato': 'Word', 'icono': 'bi-file-earmark-word', 'clase': 'text-primary'}
            elif b'Workbook' in file_data or b'Worksheet' in file_data:
                return {'tipo': 'documento', 'formato': 'Excel', 'icono': 'bi-file-earmark-excel', 'clase': 'text-success'}
            else:
                return {'tipo': 'documento', 'formato': 'Office', 'icono': 'bi-file-earmark-binary', 'clase': 'text-secondary'}
        else:
            return {'tipo': 'archivo', 'formato': 'Archivo', 'icono': 'bi-file-earmark', 'clase': 'text-muted'}
    except:
        return {'tipo': 'archivo', 'formato': 'Archivo', 'icono': 'bi-file-earmark-x', 'clase': 'text-danger'}

@login_required 
def views_home(request):
    return redirect('dashboard_doctor') 

@csrf_protect
def receta_medica(request):
    usuario = request.user
    medico = usuario.fk_medico

    if request.method == 'POST':
        medicamento = request.POST.get('medicamento')
        via = request.POST.get('via_administracion')
        dosis = request.POST.get('dosis')
        fecha_inicio = request.POST.get('fecha_inicio_tratamiento') or None
        fecha_fin = request.POST.get('fecha_fin_tratamiento') or None
        archivos_receta = request.FILES.get('archivos_receta')
        cita_id = request.POST.get('fk_citas_medicas')

        try:
            cita = CitasMedicas.objects.get(id_cita_medicas=cita_id)

            # Buscar la consulta médica asociada a la cita
            consulta = ConsultaMedica.objects.filter(fk_cita=cita).first()
            if consulta:
                # Actualizar la consulta médica con los datos de la receta
                consulta.medicamento = medicamento
                consulta.via_administracion = via
                consulta.dosis = dosis
                consulta.fecha_inicio_tratamiento = fecha_inicio
                consulta.fecha_fin_tratamiento = fecha_fin
                if archivos_receta:
                    consulta.archivos_receta = archivos_receta
                consulta.save()

                # Crear notificación
                from bd.models import MensajesNotificacion
                descripcion = f"Nueva receta médica enviada para su cita del {cita.fecha_consulta.strftime('%d/%m/%Y')}."
                MensajesNotificacion.objects.create(descripcion=descripcion)

                messages.success(request, "Receta asignada correctamente a la consulta.")
                # Consumir mensajes para que no aparezcan en otras páginas
                list(messages.get_messages(request))
            else:
                messages.error(request, "No se encontró la consulta médica para esta cita.")

            return redirect('receta_medica')

        except CitasMedicas.DoesNotExist:
            messages.error(request, "La cita médica seleccionada no existe.")
        except Exception as e:
            messages.error(request, f"Error al guardar la receta: {e}")

    # Filtramos citas solo del médico actual y completadas
    citas = CitasMedicas.objects.filter(
        fk_medico=medico,
        fk_paciente__isnull=False,  # evita errores por pacientes nulos
        status_cita_medica='Completada'  # solo citas completadas
    ).select_related('fk_paciente')

    # Extraemos pacientes únicos de esas citas
    pacientes_ids = citas.values_list('fk_paciente_id', flat=True).distinct()

    # Buscamos los usuarios que están relacionados con esos pacientes
    pacientes = Usuario.objects.filter(fk_paciente_id__in=pacientes_ids)

    return render(request, 'medico/receta_medica.html', {
        'citas': citas,
        'pacientes': pacientes
    })


def ubicacion_doctor(request):
    return render(request, 'medico/ubicacion_doctor.html')

@login_required
def clinica_doctor(request):
    usuario = request.user
    medico = usuario.fk_medico

    # Asegurar que existan clínica y horario
    if not medico.fk_clinica:
        from bd.models import Clinica
        clinica = Clinica.objects.create()
        medico.fk_clinica = clinica
        medico.save()
    else:
        clinica = medico.fk_clinica

    if not medico.fk_horario_medico:
        from bd.models import HorarioMedico
        horario = HorarioMedico.objects.create()
        medico.fk_horario_medico = horario
        medico.save()
    else:
        horario = medico.fk_horario_medico

    return render(request, 'medico/clinica_doctor.html', {
        'usuario': usuario,
        'medico': medico,
        'clinica': clinica,
        'horario': horario,
    })

@login_required
def config_clinica(request):
    medico = request.user.fk_medico
    clinica = medico.fk_clinica

    # Si no existe clínica, crearla
    if not clinica:
        from bd.models import Clinica
        clinica = Clinica.objects.create()
        medico.fk_clinica = clinica
        medico.save()

    if request.method == 'POST':
        clinica.nombre = request.POST.get('nombre')
        clinica.direccion = request.POST.get('direccion')
        clinica.telefono_clinica = request.POST.get('telefono_clinica')
        clinica.correo_electronico_clinica = request.POST.get('correo_electronico_clinica')
        clinica.sitio_web = request.POST.get('sitio_web')
        clinica.facebook = request.POST.get('facebook')
        clinica.instagram = request.POST.get('instagram')
        # Guardar coordenadas del mapa
        lat = request.POST.get('latitud')
        lng = request.POST.get('longitud')
        if lat and lng:
            clinica.latitud = lat
            clinica.longitud = lng
        clinica.save()

        messages.success(request, "Información de la clínica actualizada correctamente.")
        # Consumir mensajes para que no aparezcan en otras páginas
        list(messages.get_messages(request))
        return redirect('clinica_doctor')

    return render(request, 'medico/config_clinica.html')

@login_required
def config_horario(request):
    medico = request.user.fk_medico
    horario = medico.fk_horario_medico

    # Si no existe horario, crearlo
    if not horario:
        from bd.models import HorarioMedico
        horario = HorarioMedico.objects.create()
        medico.fk_horario_medico = horario
        medico.save()

    if request.method == 'POST':
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        status = request.POST.get('status_disponibilidad')

        horario.hora_inicio = hora_inicio
        horario.hora_fin = hora_fin
        horario.status_disponibilidad = status
        horario.save()

        messages.success(request, "Horario actualizado correctamente.")
        # Consumir mensajes para que no aparezcan en otras páginas
        list(messages.get_messages(request))
        return redirect('dashboard_doctor')

    return render(request, 'medico/config_horario.html')

@login_required
def config_perfildoc(request):
    usuario = request.user
    medico = usuario.fk_medico

    # Si no existe perfil médico, crearlo
    if not medico:
        from bd.models import Medico
        medico = Medico.objects.create()
        usuario.fk_medico = medico
        usuario.save()

    if request.method == 'POST':
        form = PerfilMedicoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Guardar campos de Usuario
                    usuario.nombre = form.cleaned_data['nombre']
                    usuario.apellido = form.cleaned_data['apellido']
                    usuario.correo = form.cleaned_data['correo']
                    usuario.telefono = form.cleaned_data['telefono']
                    usuario.departamento = form.cleaned_data['departamento']
                    usuario.municipio = form.cleaned_data['municipio']
                    if form.cleaned_data['foto_perfil']:
                        usuario.foto_perfil = form.cleaned_data['foto_perfil']
                    usuario.save()

                    # Guardar campos de Medico
                    medico.especialidad = form.cleaned_data['especialidad']
                    medico.sub_especialidad_1 = form.cleaned_data['sub_especialidad_1']
                    medico.sub_especialidad_2 = form.cleaned_data['sub_especialidad_2']
                    medico.no_jvpm = form.cleaned_data['no_jvpm']
                    medico.dui = form.cleaned_data['dui']
                    medico.descripcion = form.cleaned_data['descripcion']
                    medico.precio_consulta = form.cleaned_data.get('precio_consulta')
                    medico.save()

                messages.success(request, "Perfil médico actualizado correctamente.")
                # Consumir mensajes para que no aparezcan en otras páginas
                list(messages.get_messages(request))
                return redirect('clinica_doctor')
            except Exception as e:
                messages.error(request, f"Error al guardar los cambios: {e}")
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        # Inicializar formulario con valores actuales
        initial_data = {
            'nombre': usuario.nombre or '',
            'apellido': usuario.apellido or '',
            'correo': usuario.correo or '',
            'telefono': usuario.telefono or '',
            'departamento': usuario.departamento or '',
            'municipio': usuario.municipio or '',
            'especialidad': medico.especialidad or '',
            'sub_especialidad_1': medico.sub_especialidad_1 or '',
            'sub_especialidad_2': medico.sub_especialidad_2 or '',
            'no_jvpm': medico.no_jvpm or '',
            'dui': medico.dui or '',
            'descripcion': medico.descripcion or '',
            'precio_consulta': medico.precio_consulta,
            'foto_perfil': usuario.foto_perfil,
        }
        form = PerfilMedicoForm(initial=initial_data)

    return render(request, 'medico/config_perfildoc.html', {'form': form})

@login_required
def dashboard_doctor(request):
    usuario = request.user
    medico = usuario.fk_medico

    if not medico:
        return render(request, 'medico/no_es_medico.html')

    citas_raw = CitasMedicas.objects.filter(
        fk_medico=medico
    ).order_by('-fecha_consulta', '-hora_inicio').select_related('fk_paciente')

    # Citas próximas (Pendiente y En proceso) - próximos 5 días
    hoy = date.today()
    fecha_limite = hoy + timedelta(days=5)
    citas_proximas_raw = CitasMedicas.objects.filter(
        fk_medico=medico,
        status_cita_medica__in=['Pendiente', 'En proceso'],
        fecha_consulta__range=(hoy, fecha_limite)
    ).order_by('fecha_consulta', 'hora_inicio').select_related('fk_paciente')

    citas_proximas = []
    for cita in citas_proximas_raw:
        user_paciente = Usuario.objects.filter(fk_paciente=cita.fk_paciente).first()
        nombre_completo = f"{user_paciente.nombre} {user_paciente.apellido}" if user_paciente else "Paciente desconocido"
        citas_proximas.append({
            'id': cita.id_cita_medicas,
            'fecha': cita.fecha_consulta,
            'hora': cita.hora_inicio,
            'motivo': cita.des_motivo_consulta_paciente,
            'estado': cita.status_cita_medica,
            'nombre_paciente': nombre_completo,
            'paciente_id': cita.fk_paciente.id_paciente,
            'diagnostico': cita.diagnostico
        })

    # Citas completadas
    citas_completadas_raw = CitasMedicas.objects.filter(
        fk_medico=medico,
        status_cita_medica='Completada'
    ).order_by('-fecha_consulta', '-hora_inicio').select_related('fk_paciente')

    citas_completadas = []
    for cita in citas_completadas_raw:
        user_paciente = Usuario.objects.filter(fk_paciente=cita.fk_paciente).first()
        nombre_completo = f"{user_paciente.nombre} {user_paciente.apellido}" if user_paciente else "Paciente desconocido"
        citas_completadas.append({
            'id': cita.id_cita_medicas,
            'fecha': cita.fecha_consulta,
            'hora': cita.hora_inicio,
            'motivo': cita.des_motivo_consulta_paciente,
            'estado': cita.status_cita_medica,
            'nombre_paciente': nombre_completo,
            'paciente_id': cita.fk_paciente.id_paciente,
            'diagnostico': cita.diagnostico
        })

    #Ingresos de Factura
    ingresos = (
        CitasMedicas.objects
        .filter(fk_medico=medico, fk_factura__isnull=False)
        .values('fk_factura__fecha_emision')
        .annotate(total=Sum('fk_factura__monto'))
        .order_by('fk_factura__fecha_emision')
    )

    #Suma ingresos
    total_ingresos = (
    CitasMedicas.objects
    .filter(fk_medico=medico, fk_factura__isnull=False)
    .aggregate(suma=Sum('fk_factura__monto'))['suma'] or 0
    )

    # Pacientes consultados (únicos)
    pacientes_consultados = []
    pacientes_ids = set()
    for cita in citas_raw:
        if cita.fk_paciente and cita.fk_paciente.id_paciente not in pacientes_ids:
            user_paciente = Usuario.objects.filter(fk_paciente=cita.fk_paciente).first()
            nombre_completo = f"{user_paciente.nombre} {user_paciente.apellido}" if user_paciente else "Paciente desconocido"
            pacientes_consultados.append({
                'id': cita.fk_paciente.id_paciente,
                'nombre': nombre_completo
            })
            pacientes_ids.add(cita.fk_paciente.id_paciente)

    #valoraciones
    valoraciones = ValoracionConsulta.objects.all()

    return render(request, 'medico/dashboard_doctor.html', {
        'citas_proximas': citas_proximas,
        'citas_completadas': citas_completadas,
        'pacientes_consultados': pacientes_consultados,
        'ingresos': ingresos,
        'total_ingresos': total_ingresos,
        'valoraciones': valoraciones
    })

@require_POST
@login_required
def actualizar_estado_cita(request, cita_id):
    cita = get_object_or_404(CitasMedicas, id_cita_medicas=cita_id, fk_medico=request.user.fk_medico)

    accion = request.POST.get('accion')
    if accion == 'aceptar':
        cita.status_cita_medica = 'En proceso'
        messages.success(request, "Cita aceptada y movida a 'En proceso'.")
        # Consumir mensajes para que no aparezcan en otras páginas
        list(messages.get_messages(request))
    elif accion == 'cancelar':
        cita.status_cita_medica = 'Cancelado'
        cita.cancelado_por = 'medico'
        cita.fecha_cancelacion = timezone.now()
        messages.success(request, "Cita cancelada correctamente.")
        # Consumir mensajes para que no aparezcan en otras páginas
        list(messages.get_messages(request))

    cita.save()
    return redirect('agenda_medico')

@require_POST
@login_required
def actualizar_fecha_hora_cita(request, cita_id):
    cita = get_object_or_404(CitasMedicas, id_cita_medicas=cita_id, fk_medico=request.user.fk_medico)

    # Solo permitir editar si el estado es 'Pendiente'
    if cita.status_cita_medica != 'Pendiente':
        messages.error(request, "Solo se pueden editar citas con estado 'Pendiente'.")
        return redirect('agenda_medico')

    nueva_fecha = request.POST.get('fecha_consulta')
    nueva_hora = request.POST.get('hora_inicio')

    if nueva_fecha and nueva_hora:
        from datetime import datetime
        try:
            # Validar formato de fecha y hora
            fecha_dt = datetime.strptime(nueva_fecha, '%Y-%m-%d').date()
            hora_dt = datetime.strptime(nueva_hora, '%H:%M').time()

            cita.fecha_consulta = fecha_dt
            cita.hora_inicio = hora_dt
            cita.save()

            messages.success(request, "Fecha y hora de la cita actualizadas correctamente.")
            # Consumir mensajes para que no aparezcan en otras páginas
            list(messages.get_messages(request))
        except ValueError:
            messages.error(request, "Formato de fecha u hora inválido.")
    else:
        messages.error(request, "Debe proporcionar fecha y hora válidas.")

    return redirect('agenda_medico')

@login_required
def realizar_consulta(request, cita_id):
    cita = get_object_or_404(CitasMedicas, id_cita_medicas=cita_id, fk_medico=request.user.fk_medico)
    paciente = cita.fk_paciente
    usuario_paciente = Usuario.objects.filter(fk_paciente=paciente).first()

    # Calcular edad
    edad = None
    if usuario_paciente and usuario_paciente.fecha_nacimiento:
        from datetime import date
        today = date.today()
        edad = today.year - usuario_paciente.fecha_nacimiento.year - ((today.month, today.day) < (usuario_paciente.fecha_nacimiento.month, usuario_paciente.fecha_nacimiento.day))

    if request.method == 'POST':
        diagnostico = request.POST.get('diagnostico')
        tratamiento = request.POST.get('tratamiento')
        prescripcion = request.POST.get('prescripcion')
        observaciones = request.POST.get('observaciones')
        hora_fin = request.POST.get('hora_fin')
        adjunto = request.FILES.get('adjunto')
        # Campos de receta
        medicamento = request.POST.get('medicamento')
        via_administracion = request.POST.get('via_administracion')
        dosis = request.POST.get('dosis')
        fecha_inicio_tratamiento = request.POST.get('fecha_inicio_tratamiento') or None
        fecha_fin_tratamiento = request.POST.get('fecha_fin_tratamiento') or None
        archivos_receta = request.FILES.get('archivos_receta')

        # Codificar archivos a base64
        documentos_adjuntos_base64 = None
        if adjunto:
            import base64
            adjunto.seek(0)
            documentos_adjuntos_base64 = base64.b64encode(adjunto.read()).decode('utf-8')

        archivos_receta_base64 = None
        if archivos_receta:
            import base64
            archivos_receta.seek(0)
            archivos_receta_base64 = base64.b64encode(archivos_receta.read()).decode('utf-8')

        try:
            # Crear la consulta médica
            consulta = ConsultaMedica.objects.create(
                fk_cita=cita,
                sintomas=cita.des_motivo_consulta_paciente,  # Usar el motivo como síntomas
                diagnostico=diagnostico,
                tratamiento=tratamiento or prescripcion,  # Usar tratamiento o prescripción
                observaciones=observaciones,
                documentos_adjuntos=documentos_adjuntos_base64,
                medicamento=medicamento,
                via_administracion=via_administracion,
                dosis=dosis,
                fecha_inicio_tratamiento=fecha_inicio_tratamiento,
                fecha_fin_tratamiento=fecha_fin_tratamiento,
                archivos_receta=archivos_receta_base64
            )

            # Actualizar el estado de la cita a "Completada"
            cita.status_cita_medica = 'Completada'
            cita.diagnostico = diagnostico
            cita.notas_medicas = observaciones
            if hora_fin:
                cita.hora_fin = hora_fin
            cita.save()

            # Crear notificación si hay receta
            if consulta.medicamento or consulta.via_administracion or consulta.dosis:
                from bd.models import MensajesNotificacion
                descripcion = f"Nueva receta médica enviada para su cita del {cita.fecha_consulta.strftime('%d/%m/%Y')}."
                MensajesNotificacion.objects.create(
                    descripcion=descripcion
                )
                # Asociar a la cita si es necesario, pero el modelo no tiene fk directa, así que solo crear

            messages.success(request, "Consulta médica guardada correctamente.")
            # Consumir mensajes para que no aparezcan en otras páginas
            list(messages.get_messages(request))
            return redirect('dashboard_doctor')

        except Exception as e:
            messages.error(request, f"Error al guardar la consulta: {e}")

    return render(request, 'medico/realizar_consulta.html', {
        'paciente': paciente,
        'cita': cita,
        'usuario_paciente': usuario_paciente,
        'edad': edad
    })

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from bd.models import Paciente, Usuario, Factura, CitasMedicas
from django.utils import timezone

@login_required
def programar_cita_doc(request):
    if request.method == 'POST':
        # Verifica si se seleccionó un paciente existente
        paciente_id = request.POST.get('fk_paciente')
        paciente = None

        if paciente_id:
            try:
                paciente = Paciente.objects.get(id_paciente=paciente_id)
            except Paciente.DoesNotExist:
                messages.error(request, "Paciente no encontrado.")
                return redirect('programar_cita_doc')
        else:
            # Crear nuevo paciente
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            correo = request.POST.get('correo')
            telefono = request.POST.get('telefono')

            if not all([nombre, apellido, correo]):
                messages.error(request, "Debe ingresar los datos del nuevo paciente.")
                return redirect('programar_cita_doc')

            paciente = Paciente.objects.create(
                contacto_emergencia=nombre,
                tel_emergencia=telefono or ''
            )

            # Crear también el usuario
            Usuario.objects.create(
                user_name=correo,
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                telefono=telefono,
                fk_paciente=paciente
            )

        # Crear factura
        precio = request.POST.get('precio')
        factura = Factura.objects.create(
            fecha_emision=timezone.now().date(),
            monto=precio,
            fk_metodopago=None  # puedes definirlo después
        )

        # Crear la cita médica
        cita = CitasMedicas.objects.create(
            fk_paciente=paciente,
            fk_medico=request.user.fk_medico,
            fk_factura=factura,
            fecha_consulta=request.POST.get('fecha_consulta'),
            hora_inicio=request.POST.get('hora_inicio'),
            hora_fin=request.POST.get('hora_fin'),
            status_cita_medica=request.POST.get('status_cita_medica'),
            des_motivo_consulta_paciente=request.POST.get('des_motivo_consulta_paciente')
        )

        # Crear notificación
        from bd.models import MensajesNotificacion
        fecha_str = request.POST.get('fecha_consulta')
        hora_str = request.POST.get('hora_inicio')
        descripcion = f"Nueva cita médica programada para el {fecha_str} a las {hora_str}."
        MensajesNotificacion.objects.create(descripcion=descripcion)

        messages.success(request, "✅ Cita médica programada con éxito.")
        # Consumir mensajes para que no aparezcan en otras páginas
        list(messages.get_messages(request))
        return redirect('agenda_medico')

    else:
        # Filtrar pacientes que han tenido citas con este médico
        pacientes_ids = CitasMedicas.objects.filter(
            fk_medico=request.user.fk_medico
        ).values_list('fk_paciente_id', flat=True).distinct()

        pacientes = Paciente.objects.filter(id_paciente__in=pacientes_ids)

        # Si no hay pacientes con citas previas, mostrar todos los pacientes
        if not pacientes.exists():
            pacientes = Paciente.objects.all()

        return render(request, 'medico/programar_cita_doc.html', {
            'pacientes': pacientes
        })

@login_required
def ver_diagnostico_medico(request, cita_id):
    usuario = request.user
    medico = usuario.fk_medico

    if not medico:
        return render(request, 'medico/no_es_medico.html')

    try:
        cita = CitasMedicas.objects.get(id_cita_medicas=cita_id, fk_medico=medico)
    except CitasMedicas.DoesNotExist:
        raise PermissionDenied("Cita no encontrada o no tienes permisos.")

    # Obtener la consulta médica si existe
    try:
        consulta = cita.consulta_medica
    except ConsultaMedica.DoesNotExist:
        consulta = None

    # Si no hay consulta o no tiene receta, buscar en RecetaMedica
    if not consulta or not consulta.tiene_receta():
        try:
            receta = RecetaMedica.objects.get(fk_citas_medicas=cita)
            # Crear un objeto temporal con los datos de receta
            if not consulta:
                consulta = type('ConsultaTemp', (), {})()
                consulta.diagnostico = cita.diagnostico
                consulta.tratamiento = cita.notas_medicas
                consulta.observaciones = None
                consulta.documentos_adjuntos = None
                consulta.fecha_creacion = cita.fecha_consulta
                consulta.tiene_receta = lambda: True
            consulta.medicamento = receta.medicamento
            consulta.via_administracion = receta.via_administracion
            consulta.dosis = receta.dosis
            consulta.fecha_inicio_tratamiento = receta.fecha_inicio_tratamiento
            consulta.fecha_fin_tratamiento = receta.fecha_fin_tratamiento
            consulta.archivos_receta = None  # RecetaMedica no tiene archivo
            if not hasattr(consulta, 'tiene_receta'):
                consulta.tiene_receta = lambda: True
        except RecetaMedica.DoesNotExist:
            pass

    # Información del paciente
    usuario_paciente = Usuario.objects.filter(fk_paciente=cita.fk_paciente).first()
    nombre_paciente = usuario_paciente.get_full_name() if usuario_paciente else "Paciente desconocido"

    # Información de archivos adjuntos
    archivos_info = {}
    if consulta:
        try:
            if consulta.documentos_adjuntos:
                archivos_info['documentos'] = detectar_tipo_archivo_base64(consulta.documentos_adjuntos)
            if consulta.archivos_receta:
                archivos_info['receta'] = detectar_tipo_archivo_base64(consulta.archivos_receta)
        except:
            # En caso de error, usar valores por defecto
            archivos_info['documentos'] = {'tipo': 'archivo', 'formato': 'Archivo', 'icono': 'bi-file-earmark', 'clase': 'text-muted'}
            archivos_info['receta'] = {'tipo': 'archivo', 'formato': 'Archivo', 'icono': 'bi-file-earmark', 'clase': 'text-muted'}

    context = {
        'cita': cita,
        'consulta': consulta,
        'nombre_paciente': nombre_paciente,
        'archivos_info': archivos_info,
    }

    return render(request, 'medico/ver_diagnostico_medico.html', context)

@login_required
def agenda_medico(request):
    usuario = request.user
    medico = usuario.fk_medico

    if not medico:
        return render(request, 'medico/no_es_medico.html')

    hoy = date.today()

    # Citas futuras (cualquier estado distinto de Completada/Cancelado)
    citas_futuras_raw = (
        CitasMedicas.objects
        .filter(fk_medico=medico)
        .exclude(status_cita_medica__iexact='Completada')
        .exclude(status_cita_medica__iexact='Cancelado')
        .order_by('fecha_consulta', 'hora_inicio')
        .select_related('fk_paciente')
    )

    citas_futuras = []
    for cita in citas_futuras_raw:
        user_paciente = Usuario.objects.filter(fk_paciente=cita.fk_paciente).first()
        nombre_paciente = f"{user_paciente.nombre} {user_paciente.apellido}" if user_paciente else "Paciente desconocido"
        especialidad = medico.especialidad if medico.especialidad else ""
        clinica = medico.fk_clinica.nombre if medico.fk_clinica else ""

        citas_futuras.append({
            'cita': cita,
            'nombre_paciente': nombre_paciente,
            'especialidad': especialidad,
            'clinica': clinica,
        })

    # Citas completadas
    citas_completadas_raw = CitasMedicas.objects.filter(
        fk_medico=medico,
        status_cita_medica='Completada'
    ).order_by('-fecha_consulta', '-hora_inicio').select_related('fk_paciente')

    citas_completadas = []
    for cita in citas_completadas_raw:
        user_paciente = Usuario.objects.filter(fk_paciente=cita.fk_paciente).first()
        nombre_paciente = f"{user_paciente.nombre} {user_paciente.apellido}" if user_paciente else "Paciente desconocido"
        especialidad = medico.especialidad if medico.especialidad else ""
        clinica = medico.fk_clinica.nombre if medico.fk_clinica else ""

        citas_completadas.append({
            'cita': cita,
            'nombre_paciente': nombre_paciente,
            'especialidad': especialidad,
            'clinica': clinica,
        })

    # Citas canceladas
    citas_canceladas_raw = CitasMedicas.objects.filter(
        fk_medico=medico,
        status_cita_medica='Cancelado'
    ).order_by('-fecha_consulta', '-hora_inicio').select_related('fk_paciente')

    citas_canceladas = []
    for cita in citas_canceladas_raw:
        user_paciente = Usuario.objects.filter(fk_paciente=cita.fk_paciente).first()
        nombre_paciente = f"{user_paciente.nombre} {user_paciente.apellido}" if user_paciente else "Paciente desconocido"
        especialidad = medico.especialidad if medico.especialidad else ""
        clinica = medico.fk_clinica.nombre if medico.fk_clinica else ""

        citas_canceladas.append({
            'cita': cita,
            'nombre_paciente': nombre_paciente,
            'especialidad': especialidad,
            'clinica': clinica,
        })

    context = {
        'citas_futuras': citas_futuras,
        'citas_completadas': citas_completadas,
        'citas_canceladas': citas_canceladas,
        'hoy': hoy,
    }

    return render(request, 'medico/agenda_medico.html', context)


@login_required
def crear_seguimiento(request, cita_id):
    cita = get_object_or_404(CitasMedicas, id_cita_medicas=cita_id, fk_medico=request.user.fk_medico)
    paciente = cita.fk_paciente
    usuario_paciente = Usuario.objects.filter(fk_paciente=paciente).first()

    if request.method == 'POST':
        form = SeguimientoClinicoForm(request.POST, request.FILES)
        if form.is_valid():
            seguimiento = form.save(commit=False)
            seguimiento.fk_cita = cita
            seguimiento.fk_paciente = paciente
            seguimiento.fk_medico = request.user.fk_medico
            seguimiento.save()

            # Si se marca programar nueva consulta, crear la cita
            if seguimiento.programar_nueva_consulta and seguimiento.fecha_nueva_consulta and seguimiento.hora_nueva_consulta:
                CitasMedicas.objects.create(
                    fk_paciente=paciente,
                    fk_medico=request.user.fk_medico,
                    fecha_consulta=seguimiento.fecha_nueva_consulta,
                    hora_inicio=seguimiento.hora_nueva_consulta,
                    status_cita_medica='Pendiente',
                    des_motivo_consulta_paciente=f'Seguimiento programado - {seguimiento.notas_nueva_consulta or ""}'
                )

            messages.success(request, "Seguimiento clínico creado correctamente.")
            # Consumir mensajes para que no aparezcan en otras páginas
            list(messages.get_messages(request))
            return redirect('ver_seguimientos_paciente', paciente_id=paciente.id_paciente)
    else:
        form = SeguimientoClinicoForm()

    return render(request, 'medico/crear_seguimiento.html', {
        'form': form,
        'cita': cita,
        'paciente': paciente,
        'usuario_paciente': usuario_paciente
    })

@login_required
def ver_seguimientos_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id_paciente=paciente_id)
    usuario_paciente = Usuario.objects.filter(fk_paciente=paciente).first()

    # Solo el médico que atendió puede ver
    seguimientos = SeguimientoClinico.objects.filter(
        fk_paciente=paciente,
        fk_medico=request.user.fk_medico
    ).order_by('-fecha_creacion')

    return render(request, 'medico/ver_seguimientos.html', {
        'seguimientos': seguimientos,
        'paciente': paciente,
        'usuario_paciente': usuario_paciente
    })

@login_required
def crear_consulta_seguimiento(request, seguimiento_id=None, paciente_id=None):
    medico = request.user.fk_medico
    paciente = None

    if seguimiento_id:
        seguimiento_anterior = get_object_or_404(
            SeguimientoClinico,
            id_seguimiento_clinico=seguimiento_id,
            fk_medico=medico
        )
        paciente = seguimiento_anterior.fk_paciente
    elif paciente_id:
        paciente = get_object_or_404(Paciente, id_paciente=paciente_id)
        # Verificar que el médico haya atendido a este paciente
        if not CitasMedicas.objects.filter(fk_paciente=paciente, fk_medico=medico).exists():
            raise PermissionDenied("No tienes permisos para programar citas de seguimiento para este paciente.")

    # -------------------------------
    # Manejo del POST para programar cita
    # -------------------------------
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha_nueva_cita')
        hora_str = request.POST.get('hora_nueva_cita')
        motivo = (request.POST.get('motivo_nueva_cita') or '').strip()

        errores = []
        from datetime import datetime, date as _date

        # Validar fecha
        fecha_dt = None
        if fecha_str:
            try:
                fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except Exception:
                errores.append('fecha_nueva_cita: Formato inválido (YYYY-MM-DD)')
        else:
            errores.append('fecha_nueva_cita: Este campo es obligatorio')

        if fecha_dt and fecha_dt < _date.today():
            errores.append('fecha_nueva_cita: La fecha debe ser futura')

        # Validar hora
        hora_dt = None
        if hora_str:
            try:
                hora_dt = datetime.strptime(hora_str, '%H:%M').time()
            except Exception:
                errores.append('hora_nueva_cita: Formato inválido (HH:MM)')
        else:
            errores.append('hora_nueva_cita: Este campo es obligatorio')

        # Validar motivo
        if not motivo:
            errores.append('motivo_nueva_cita: Este campo es obligatorio')

        if errores:
            messages.error(request, "No se pudo programar la cita. " + " | ".join(errores))
            form = ProgramarCitaSeguimientoForm(request.POST)
        else:
            # Crear la nueva cita
            CitasMedicas.objects.create(
                fk_paciente=paciente,
                fk_medico=medico,
                fecha_consulta=fecha_dt,
                hora_inicio=hora_dt,
                status_cita_medica='Pendiente',
                des_motivo_consulta_paciente=motivo
            )
            messages.success(request, "Cita de seguimiento programada correctamente.")
            # Consumir mensajes para que no aparezcan en otras páginas
            list(messages.get_messages(request))
            return redirect('agenda_medico')
    else:
        form = ProgramarCitaSeguimientoForm()

    return render(request, 'medico/crear_consulta_seguimiento.html', {
        'form': form,
        'paciente': paciente,
        'motivo_sugerido': 'Consulta de seguimiento'
    })


@login_required
def ver_consultas_seguimiento(request):
    medico = request.user.fk_medico
    consultas = ConsultaSeguimiento.objects.filter(fk_medico=medico).order_by('-fecha_creacion')

    return render(request, 'medico/ver_consultas_seguimiento.html', {
        'consultas': consultas
    })

@login_required
def descargar_archivo_base64(request, consulta_id, tipo):
    """
    Vista para servir archivos desde base64 o FieldFile
    tipo: 'documentos' o 'receta'
    Parámetro GET 'download=true' fuerza descarga
    """
    force_download = request.GET.get('download') == 'true'
    consulta = get_object_or_404(ConsultaMedica, id_consulta_medica=consulta_id)

    if tipo == 'documentos':
        archivo_data = consulta.documentos_adjuntos
        tipo_archivo = 'documento'
    elif tipo == 'receta':
        archivo_data = consulta.archivos_receta
        tipo_archivo = 'receta'
    else:
        return HttpResponse("Tipo de archivo inválido", status=400)

    if not archivo_data:
        return HttpResponse("Archivo no encontrado", status=404)

    try:
        import base64
        import mimetypes
        from django.core.files.base import ContentFile

        # Verificar si es un string base64 o un FieldFile
        if isinstance(archivo_data, str):
            # Es un string base64
            file_data = base64.b64decode(archivo_data)
        elif hasattr(archivo_data, 'read'):
            # Es un FieldFile, leer el contenido
            archivo_data.seek(0)
            file_data = archivo_data.read()
        else:
            return HttpResponse("Formato de archivo no soportado", status=400)

        # Detectar tipo MIME basado en el contenido del archivo
        content_type, _ = mimetypes.guess_type(f'{tipo_archivo}_archivo')

        # Si no se puede detectar por nombre, intentar por contenido
        if not content_type:
            if file_data.startswith(b'\xff\xd8\xff'):  # JPEG
                content_type = 'image/jpeg'
            elif file_data.startswith(b'\x89PNG'):  # PNG
                content_type = 'image/png'
            elif file_data.startswith(b'GIF87a') or file_data.startswith(b'GIF89a'):  # GIF
                content_type = 'image/gif'
            elif file_data.startswith(b'BM'):  # BMP
                content_type = 'image/bmp'
            elif file_data.startswith(b'RIFF') and file_data[8:12] == b'WEBP':  # WebP
                content_type = 'image/webp'
            elif file_data.startswith(b'%PDF'):  # PDF
                content_type = 'application/pdf'
            elif file_data.startswith(b'PK\x03\x04'):  # ZIP/DOCX/XLSX
                # Verificar si es DOCX o XLSX por contenido interno
                if b'word/' in file_data:
                    content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                elif b'xl/' in file_data:
                    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                else:
                    content_type = 'application/zip'
            elif file_data.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):  # DOC/XLS antiguos
                content_type = 'application/msword'  # o 'application/vnd.ms-excel'
            else:
                content_type = 'application/octet-stream'

        # Determinar si mostrar inline o attachment
        if force_download:
            disposition = 'attachment'
        elif content_type.startswith('image/'):
            disposition = 'inline'
        elif content_type == 'application/pdf':
            disposition = 'inline'
        else:
            # Para documentos Office, intentar mostrar inline primero
            disposition = 'inline'

        # Crear nombre de archivo basado en tipo y contenido
        if content_type == 'image/jpeg':
            filename = f'{tipo_archivo}_imagen.jpg'
        elif content_type == 'image/png':
            filename = f'{tipo_archivo}_imagen.png'
        elif content_type == 'image/gif':
            filename = f'{tipo_archivo}_imagen.gif'
        elif content_type == 'image/bmp':
            filename = f'{tipo_archivo}_imagen.bmp'
        elif content_type == 'image/webp':
            filename = f'{tipo_archivo}_imagen.webp'
        elif content_type == 'application/pdf':
            filename = f'{tipo_archivo}.pdf'
        elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            filename = f'{tipo_archivo}.docx'
        elif content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            filename = f'{tipo_archivo}.xlsx'
        elif content_type == 'application/msword':
            filename = f'{tipo_archivo}.doc'
        else:
            filename = f'{tipo_archivo}_archivo'

        response = HttpResponse(file_data, content_type=content_type)
        response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
        return response
    except Exception as e:
        return HttpResponse(f"Error al procesar archivo: {e}", status=500)

@login_required
def historial_facturas(request):
    usuario = request.user
    medico = usuario.fk_medico

    if not medico:
        return render(request, 'medico/no_es_medico.html')

    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    # Query base
    facturas = Factura.objects.filter(
        citasmedicas__fk_medico=medico,
        citasmedicas__fk_factura__isnull=False
    ).select_related(
        'fk_metodopago',
        'citasmedicas__fk_paciente'
    ).order_by('-fecha_emision')

    # Aplicar filtros de fecha
    if fecha_desde:
        facturas = facturas.filter(fecha_emision__gte=fecha_desde)
    if fecha_hasta:
        facturas = facturas.filter(fecha_emision__lte=fecha_hasta)

    # Enriquecer datos
    facturas_enriquecidas = []
    for factura in facturas:
        # Obtener la cita asociada
        cita = CitasMedicas.objects.filter(fk_factura=factura).first()
        paciente = None
        if cita and cita.fk_paciente:
            paciente = Usuario.objects.filter(fk_paciente=cita.fk_paciente).first()

        # Calcular gastos adicionales
        gastos_adicionales = GastosAdicionales.objects.filter(fk_cita=cita) if cita else []
        total_gastos = sum(gasto.monto for gasto in gastos_adicionales)
        total_factura = factura.monto + total_gastos

        facturas_enriquecidas.append({
            'factura': factura,
            'paciente': paciente.get_full_name() if paciente else "Paciente desconocido",
            'fecha_cita': cita.fecha_consulta if cita else None,
            'metodo_pago': factura.fk_metodopago.tipometodopago if factura.fk_metodopago else "No especificado",
            'monto_consulta': factura.monto,
            'gastos_adicionales': gastos_adicionales,
            'total_gastos_adicionales': total_gastos,
            'total_factura': total_factura,
        })

    context = {
        'facturas': facturas_enriquecidas,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total_facturas': len(facturas_enriquecidas),
        'total_monto': sum(f['total_factura'] for f in facturas_enriquecidas if f['total_factura']),
    }

    return render(request, 'medico/historial_facturas.html', context)

@login_required
def gestionar_gastos_adicionales(request, cita_id):
    cita = get_object_or_404(CitasMedicas, id_cita_medicas=cita_id, fk_medico=request.user.fk_medico)

    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        monto = request.POST.get('monto')
        metodo_pago = request.POST.get('metodo_pago')

        if descripcion and monto:
            GastosAdicionales.objects.create(
                fk_cita=cita,
                descripcion=descripcion,
                monto=monto,
                metodo_pago=metodo_pago
            )
            messages.success(request, "Gasto adicional agregado correctamente.")
            # Consumir mensajes para que no aparezcan en otras páginas
            list(messages.get_messages(request))
            return redirect('gestionar_gastos_adicionales', cita_id=cita_id)
        else:
            messages.error(request, "Por favor complete todos los campos.")

    gastos = GastosAdicionales.objects.filter(fk_cita=cita)
    total_gastos = gastos.aggregate(total=models.Sum('monto'))['total'] or 0

    context = {
        'cita': cita,
        'gastos': gastos,
        'total_gastos': total_gastos,
    }

    return render(request, 'medico/gestionar_gastos_adicionales.html', context)

@require_POST
@login_required
def eliminar_gasto_adicional(request, gasto_id):
    gasto = get_object_or_404(GastosAdicionales, id_gastos_adicionales=gasto_id, fk_cita__fk_medico=request.user.fk_medico)
    cita_id = gasto.fk_cita.id_cita_medicas
    gasto.delete()
    messages.success(request, "Gasto adicional eliminado correctamente.")
    # Consumir mensajes para que no aparezcan en otras páginas
    list(messages.get_messages(request))
    return redirect('gestionar_gastos_adicionales', cita_id=cita_id)
