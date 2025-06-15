from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from datetime import date
from bd.models import Medico,Paciente,CitasMedicas
from django.contrib import messages

def views_home(request):  
    return render(request, 'paciente/home.html')

def dashboard_paciente(request):
    return render(request, 'dashboard_paciente.html')

## Vista para ver la agenda del paciente
@login_required
def ver_agenda(request):
    usuario = request.user
    try:
        paciente = Paciente.objects.get(usuario=usuario)
    except Paciente.DoesNotExist:
        paciente = None

    citas = []
    if paciente:
        # Cambia 'fecha_cita' por 'fecha_consulta'
        citas = CitasMedicas.objects.filter(fk_paciente=paciente).order_by('fecha_consulta')

    context = {
        'citas': citas,
    }
    return render(request, 'paciente/agenda.html', context)

## Vista para agendar una cita médica
@login_required
def agendar_cita(request):
    usuario = request.user

    # Calcular edad si fecha_nacimiento está definida
    edad = None
    if hasattr(usuario, 'fecha_nacimiento') and usuario.fecha_nacimiento:
        hoy = date.today()
        edad = hoy.year - usuario.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (usuario.fecha_nacimiento.month, usuario.fecha_nacimiento.day)
        )

    # Filtrado de médicos por especialidad
    filtro = request.GET.get('especialidad', '')
    medicos = Medico.objects.all()
    if filtro:
        medicos = medicos.filter(especialidad__icontains=filtro)

    especialidades = Medico.objects.values_list('especialidad', flat=True).distinct()

    # Variables para mantener valores del formulario en caso de error
    medico_id = ''
    medico_nombre = ''
    fecha_cita = ''
    motivo = ''

    if request.method == 'POST':
        medico_id = request.POST.get('medico_id', '')
        fecha_cita = request.POST.get('fecha_cita', '')
        motivo = request.POST.get('motivo', '')

        if not medico_id:
            messages.error(request, "Debes seleccionar un médico.")
        elif not fecha_cita:
            messages.error(request, "Debes ingresar una fecha para la cita.")
        elif not motivo:
            messages.error(request, "Debes ingresar el motivo de la consulta.")
        else:
            try:
                medico = Medico.objects.get(pk=medico_id)
                paciente = Paciente.objects.get(usuario=usuario)
                CitasMedicas.objects.create(
                    fk_medico=medico,
                    fk_paciente=paciente,
                    fecha_cita=fecha_cita,
                    motivo=motivo,
                )
                messages.success(request, f"Cita agendada exitosamente para {fecha_cita}.")
                return redirect('agenda')
            except Medico.DoesNotExist:
                messages.error(request, "El médico seleccionado no existe.")
            except Paciente.DoesNotExist:
                messages.error(request, "No se encontró el paciente asociado.")
            else:
                medico_nombre = medico.get_nombre_display()

    # Si no se seleccionó un médico, pero se quiere mostrar el nombre que estaba
    if medico_id and not medico_nombre:
        try:
            medico_nombre = Medico.objects.get(pk=medico_id).get_nombre_display()
        except Medico.DoesNotExist:
            medico_nombre = ''

    context = {
        'nombre': f"{usuario.nombre} {usuario.apellido}",
        'edad': edad,
        'sexo': usuario.sexo,
        'medicos': medicos,
        'especialidades': especialidades,
        'filtro_especialidad': filtro,
        'medico_id': medico_id,
        'medico_nombre': medico_nombre,
        'fecha_cita': fecha_cita,
        'motivo': motivo,
    }
    return render(request, 'agendar_cita.html', context)
