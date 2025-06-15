from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from datetime import date, datetime
from .decorators import paciente_required
from django.contrib import messages

from bd.models import Usuario, Medico, CitasMedicas

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

    if not hasattr(usuario, 'fk_paciente') or usuario.fk_paciente is None:
        raise PermissionDenied("No tienes permisos para agendar citas.")

    paciente = usuario.fk_paciente

    # Cálculo de edad 
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

    # Lista de médicos con nombre completo
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

    # Procesamiento del formulario
    if request.method == 'POST':
        medico_id = request.POST.get('medico_id')
        fecha_str = request.POST.get('fecha_cita')
        hora_str = request.POST.get('hora_cita')
        motivo = request.POST.get('motivo')

        if not (medico_id and fecha_str and hora_str and motivo):
            messages.error(request, "Por favor completa todos los campos.")
            return redirect('agendar_cita')
        
        print("medico_id:", medico_id)
        print("fecha_cita:", fecha_str)
        print("hora_cita:", hora_str)
        print("motivo:", motivo)


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

        CitasMedicas.objects.create(
            fecha_consulta=fecha,
            hora_inicio=hora,
            status_cita_medica="Pendiente",
            des_motivo_consulta_paciente=motivo,
            fk_paciente=paciente,
            fk_medico=medico
        )
        messages.success(request, "Cita agendada correctamente.")
        return redirect('agenda')

    context = {
        'edad': edad,
        'paciente': paciente,
        'medicos': medicos_con_nombre,
        'especialidad_seleccionada': especialidad,
        'nombre': usuario.get_full_name() if callable(getattr(usuario, 'get_full_name', None)) else f"{usuario.nombre} {usuario.apellido}",
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

    citas_confirmadas = CitasMedicas.objects.filter(
        fk_paciente=paciente
    ).order_by('fecha_consulta', 'hora_inicio')

    context = {
        'paciente': paciente,
        'citas_confirmadas': citas_confirmadas,
    }

    return render(request, 'paciente/agenda.html', context)
