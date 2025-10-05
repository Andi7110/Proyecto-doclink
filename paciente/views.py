from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from datetime import date, datetime, time
from django.db.models import Q, Avg, Count
from .decorators import paciente_required

from bd.models import Usuario, Medico, Paciente, CitasMedicas, Clinica, ValoracionConsulta


@login_required
@paciente_required
def views_home(request):
    return render(request, 'paciente/home.html')


@login_required
@paciente_required
def dashboard_paciente(request):
    return render(request, 'paciente/dashboard_paciente.html')

#Agendar cita
@login_required
@paciente_required
def agendar_cita(request):
    usuario = request.user

    if not hasattr(usuario, 'fk_paciente') or usuario.fk_paciente is None:
        raise PermissionDenied("No tienes permisos para agendar citas.")

    paciente = usuario.fk_paciente

    # Calcular edad desde fecha de nacimiento
    edad = None
    if hasattr(usuario, 'fecha_nacimiento') and usuario.fecha_nacimiento:
        hoy = date.today()
        nacimiento = usuario.fecha_nacimiento
        edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))

    # Filtro por especialidad
    especialidad = request.GET.get('especialidad')
    medicos = Medico.objects.all()
    if especialidad:
        medicos = medicos.filter(especialidad__icontains=especialidad)

    # Crear lista enriquecida con nombre del médico
    medicos_con_nombre = []
    for medico in medicos:
        usuario_medico = Usuario.objects.filter(fk_medico=medico).first()
        if usuario_medico:
            nombre_completo = f"{usuario_medico.nombre or ''} {usuario_medico.apellido or ''}".strip()
        else:
            nombre_completo = "Nombre no disponible"
        medicos_con_nombre.append({
            'id_medico': medico.id_medico,
            'especialidad': medico.especialidad,
            'nombre_completo': nombre_completo,
        })

    if request.method == 'POST':
        medico_id = request.POST.get('medico_id')
        fecha_str = request.POST.get('fecha_cita')
        hora_str = request.POST.get('hora_cita')
        motivo = request.POST.get('motivo')

        if not (medico_id and fecha_str and hora_str and motivo):
            messages.error(request, "Por favor completa todos los campos.")
            return redirect('agendar_cita')

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora = datetime.strptime(hora_str, '%H:%M').time()
        except ValueError:
            messages.error(request, "Formato de fecha u hora inválido.")
            return redirect('agendar_cita')

        try:
            medico = Medico.objects.get(id_medico=medico_id)
        except Medico.DoesNotExist:
            messages.error(request, "Médico no encontrado.")
            return redirect('agendar_cita')

        try:
            CitasMedicas.objects.create(
                fecha_consulta=fecha,
                hora_inicio=hora,
                status_cita_medica="Pendiente",
                des_motivo_consulta_paciente=motivo,
                fk_paciente=paciente,
                fk_medico=medico
            )
        except Exception as e:
            messages.error(request, f"Error al guardar la cita: {e}")
            return redirect('agendar_cita')

        messages.success(request, "Cita agendada correctamente.")
        # Prevenir duplicado
        if CitasMedicas.objects.filter(
            fk_medico=medico,
            fecha_consulta=fecha,
            hora_inicio=hora
        ).exists():
            # messages.error(request, "Ya hay una cita agendada con este médico en esa fecha y hora.")
            return redirect('agendar_cita')

        CitasMedicas.objects.create(
            fecha_consulta=fecha,
            hora_inicio=hora,
            status_cita_medica="Pendiente",
            des_motivo_consulta_paciente=motivo,
            fk_paciente=paciente,
            fk_medico=medico
        )
        messages.success(request, "¡Cita agendada correctamente!")
        return redirect('agenda')

    context = {
        'edad': edad,
        'paciente': paciente,
        'medicos': medicos_con_nombre,
        'especialidad_seleccionada': especialidad,
        'nombre': usuario.get_full_name() if callable(getattr(usuario, 'get_full_name', None)) else f"{usuario.nombre} {usuario.apellido}",
        'sexo': getattr(usuario, 'sexo', ''),
        'hoy': date.today(),
        # Opcional: lista de especialidades para filtro rápido
        'especialidades': Medico.objects.values_list('especialidad', flat=True).distinct(),
    }

    return render(request, 'paciente/agendar_cita.html', context)

    return render(request, 'paciente/agenda.html', context)

@login_required
@paciente_required
def ver_agenda(request):
    usuario = request.user

    if not hasattr(usuario, 'fk_paciente') or usuario.fk_paciente is None:
        raise PermissionDenied("No tienes permisos para ver esta agenda.")

    paciente = usuario.fk_paciente
    hoy = date.today()
    ahora = datetime.now().time()

    citas = CitasMedicas.objects.filter()
    citas_futuras = CitasMedicas.objects.filter(
        fk_paciente=paciente
    ).filter(
        Q(fecha_consulta__gt=hoy) |
        Q(fecha_consulta=hoy, hora_inicio__gte=ahora)
    ).order_by('fecha_consulta', 'hora_inicio')

    ahora = datetime.now()

    citas_pasadas = CitasMedicas.objects.filter(
        fk_paciente=paciente
    ).filter(
        Q(fecha_consulta__lt=hoy) |
        Q(fecha_consulta=hoy, hora_inicio__lt=ahora)
    ).order_by('-fecha_consulta', '-hora_inicio').select_related('fk_medico', 'fk_medico__fk_clinica')

    # Enriquecer citas pasadas con info de valoración
    citas_pasadas_con_valoracion = []
    for cita in citas_pasadas:
        tiene_valoracion = hasattr(cita, 'valoracionconsulta') and cita.valoracionconsulta.exists()
        usuario_medico = Usuario.objects.filter(fk_medico=cita.fk_medico).first()
        nombre_medico = usuario_medico.get_full_name() if usuario_medico else "Nombre no disponible"
        especialidad = cita.fk_medico.especialidad if cita.fk_medico else ""
        clinica = cita.fk_medico.fk_clinica.nombre if cita.fk_medico and cita.fk_medico.fk_clinica else ""

        citas_pasadas_con_valoracion.append({
            'cita': cita,
            'tiene_valoracion': tiene_valoracion,
            'nombre_medico': nombre_medico,
            'especialidad': especialidad,
            'clinica': clinica,
        })

    context = {
        'paciente': paciente,
        'citas': citas,
        'ahora': ahora,
        'citas_futuras': citas_futuras,
        'citas_pasadas': citas_pasadas_con_valoracion,
    }

    return render(request, 'paciente/agenda.html', context)


@login_required
@paciente_required
def ranking_medico(request):
    # Filtros
    especialidad_filter = request.GET.get('especialidad', '')
    ubicacion_filter = request.GET.get('ubicacion', '')

    # Query base
    medicos = Medico.objects.select_related('fk_clinica').annotate(
        avg_rating=Avg('citasmedicas__valoracionconsulta__calificacion_consulta'),
        num_ratings=Count('citasmedicas__valoracionconsulta'),
        num_reviews=Count('citasmedicas__valoracionconsulta', filter=Q(citasmedicas__valoracionconsulta__resena__isnull=False))
    ).filter(
        Q(avg_rating__isnull=False)  # Solo médicos con al menos una valoración
    )

    # Aplicar filtros
    if especialidad_filter:
        medicos = medicos.filter(especialidad__icontains=especialidad_filter)

    if ubicacion_filter:
        medicos = medicos.filter(fk_clinica__municipio__icontains=ubicacion_filter)

    # Ordenar por promedio descendente
    medicos = medicos.order_by('-avg_rating')

    # Obtener opciones para filtros
    especialidades = Medico.objects.values_list('especialidad', flat=True).distinct().exclude(especialidad__isnull=True).exclude(especialidad='')
    ubicaciones = Clinica.objects.values_list('municipio', flat=True).distinct().exclude(municipio__isnull=True).exclude(municipio='')

    # Enriquecer con nombre del médico
    medicos_con_datos = []
    for medico in medicos:
        usuario_medico = Usuario.objects.filter(fk_medico=medico).first()
        nombre_completo = usuario_medico.get_full_name() if usuario_medico else "Nombre no disponible"
        clinica_nombre = medico.fk_clinica.nombre if medico.fk_clinica else "Sin clínica"

        medicos_con_datos.append({
            'id_medico': medico.id_medico,
            'nombre_completo': nombre_completo,
            'especialidad': medico.especialidad,
            'clinica': clinica_nombre,
            'ubicacion': medico.fk_clinica.municipio if medico.fk_clinica else '',
            'avg_rating': round(medico.avg_rating, 1) if medico.avg_rating else 0,
            'num_ratings': medico.num_ratings,
            'num_reviews': medico.num_reviews,
        })

    context = {
        'medicos': medicos_con_datos,
        'especialidades': especialidades,
        'ubicaciones': ubicaciones,
        'especialidad_filter': especialidad_filter,
        'ubicacion_filter': ubicacion_filter,
    }

    return render(request, 'paciente/ranking_medico.html', context)


@login_required
@paciente_required
def calificar_cita(request, cita_id):
    usuario = request.user

    if not hasattr(usuario, 'fk_paciente') or usuario.fk_paciente is None:
        raise PermissionDenied("No tienes permisos para calificar citas.")

    paciente = usuario.fk_paciente

    try:
        cita = CitasMedicas.objects.get(id_cita_medicas=cita_id, fk_paciente=paciente)
    except CitasMedicas.DoesNotExist:
        raise PermissionDenied("Cita no encontrada o no tienes permisos.")

    # Verificar que la cita ya pasó
    hoy = date.today()
    ahora = datetime.now().time()
    if cita.fecha_consulta > hoy or (cita.fecha_consulta == hoy and cita.hora_inicio > ahora):
        messages.error(request, "No puedes calificar una cita que aún no ha ocurrido.")
        return redirect('agenda')

    # Verificar si ya tiene valoración
    if ValoracionConsulta.objects.filter(fk_cita=cita).exists():
        messages.warning(request, "Esta cita ya ha sido calificada.")
        return redirect('agenda')

    if request.method == 'POST':
        calificacion = request.POST.get('calificacion')
        resena = request.POST.get('resena', '').strip()

        if not calificacion or not calificacion.isdigit() or not (1 <= int(calificacion) <= 5):
            messages.error(request, "Por favor selecciona una calificación válida (1-5 estrellas).")
            return redirect('calificar_cita', cita_id=cita_id)

        try:
            ValoracionConsulta.objects.create(
                calificacion_consulta=int(calificacion),
                resena=resena if resena else None,
                fk_cita=cita
            )
            messages.success(request, "¡Gracias por tu calificación!")
            return redirect('agenda')
        except Exception as e:
            messages.error(request, f"Error al guardar la calificación: {e}")
            return redirect('calificar_cita', cita_id=cita_id)

    # Información del médico
    usuario_medico = Usuario.objects.filter(fk_medico=cita.fk_medico).first()
    nombre_medico = usuario_medico.get_full_name() if usuario_medico else "Nombre no disponible"
    especialidad = cita.fk_medico.especialidad if cita.fk_medico else ""

    context = {
        'cita': cita,
        'nombre_medico': nombre_medico,
        'especialidad': especialidad,
    }

    return render(request, 'paciente/calificar_cita.html', context)

