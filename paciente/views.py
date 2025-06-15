from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from datetime import date, datetime, time
from django.db.models import Q
from .decorators import paciente_required

from bd.models import Usuario, Medico, Paciente, CitasMedicas


@login_required
@paciente_required
def views_home(request):
    return render(request, 'paciente/home.html')


@login_required
@paciente_required
def dashboard_paciente(request):
    return render(request, 'paciente/dashboard_paciente.html')


@login_required
@paciente_required
def agendar_cita(request):
    usuario = request.user

    # Verifica si el usuario tiene un paciente asociado
    if not hasattr(usuario, 'fk_paciente') or usuario.fk_paciente is None:
        raise PermissionDenied("No tienes permisos para agendar citas.")

    paciente = usuario.fk_paciente

    # Calcular edad desde fecha de nacimiento
    edad = None
    if usuario.fecha_nacimiento:
        hoy = date.today()
        nacimiento = usuario.fecha_nacimiento
        edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))

    # Filtro por especialidad
    especialidad = request.GET.get('especialidad')
    medicos = Medico.objects.all()
    if especialidad:
        medicos = medicos.filter(especialidad__icontains=especialidad)

    # Procesar formulario
    if request.method == 'POST':
        medico_id = request.POST.get('medico_id')
        fecha = request.POST.get('fecha_cita')
        hora_inicio = request.POST.get('hora_cita')
        motivo = request.POST.get('motivo')

        # Validar campos
        if medico_id and fecha and hora_inicio and motivo:
            try:
                medico = Medico.objects.get(id_medico=medico_id)

                # Prevenir duplicados: ya existe cita con mismo médico y horario
                if CitasMedicas.objects.filter(
                    fk_medico=medico,
                    fecha_consulta=fecha,
                    hora_inicio=hora_inicio
                ).exists():
                    messages.error(request, "Ya hay una cita agendada con este médico en esa fecha y hora.")
                    return redirect('agendar_cita')

                # Crear cita
                nueva_cita = CitasMedicas.objects.create(
                    fecha_consulta=fecha,
                    hora_inicio=hora_inicio,
                    status_cita_medica="Pendiente",
                    des_motivo_consulta_paciente=motivo,
                    fk_paciente=paciente,
                    fk_medico=medico
                )
                messages.success(request, "¡Cita agendada correctamente!")
                return redirect('agenda')

            except Medico.DoesNotExist:
                messages.error(request, "El médico seleccionado no existe.")
        else:
            messages.error(request, "Todos los campos son obligatorios.")

    context = {
        'edad': edad,
        'paciente': paciente,
        'medicos': medicos,
        'especialidad_seleccionada': especialidad,
        'nombre': usuario.get_full_name() if hasattr(usuario, 'get_full_name') else str(usuario),
        'sexo': getattr(usuario, 'sexo', ''),
    }

    return render(request, 'paciente/agendar_cita.html', context)


@login_required
@paciente_required
def ver_agenda(request):
    usuario = request.user

    if not hasattr(usuario, 'fk_paciente') or usuario.fk_paciente is None:
        raise PermissionDenied("No tienes permisos para ver esta agenda.")

    paciente = usuario.fk_paciente
    hoy = date.today()
    ahora = datetime.now().time()

    # Citas futuras
    citas_futuras = CitasMedicas.objects.filter(
        fk_paciente=paciente
    ).filter(
        Q(fecha_consulta__gt=hoy) |
        Q(fecha_consulta=hoy, hora_inicio__gte=ahora)
    ).order_by('fecha_consulta', 'hora_inicio')

    # Citas pasadas
    citas_pasadas = CitasMedicas.objects.filter(
        fk_paciente=paciente
    ).filter(
        Q(fecha_consulta__lt=hoy) |
        Q(fecha_consulta=hoy, hora_inicio__lt=ahora)
    ).order_by('-fecha_consulta', '-hora_inicio')

    context = {
        'paciente': paciente,
        'citas_futuras': citas_futuras,
        'citas_pasadas': citas_pasadas,
    }

    return render(request, 'paciente/agenda.html', context)
