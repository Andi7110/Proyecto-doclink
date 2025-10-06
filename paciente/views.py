from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from datetime import date, datetime, time
from django.db.models import Q
from .decorators import paciente_required
from django.shortcuts import render, redirect, get_object_or_404
from bd.models import PolizaSeguro, ContactoEmergencia
from .forms import PolizaSeguroForm, ContactoEmergenciaForm

from bd.models import Usuario, Medico, Paciente, CitasMedicas


@login_required
@paciente_required
def views_home(request):
    return render(request, 'paciente/home.html')


@login_required
@paciente_required
def dashboard_paciente(request):
    usuario = request.user
    paciente = getattr(usuario, 'fk_paciente', None)
    
    if not paciente:
        # Si no hay paciente asociado, evita el error
        messages.error(request, "No tienes un paciente asociado.")
        return redirect('home')  # O a otra vista segura

    return render(request, "paciente/dashboard_paciente.html", {"paciente": paciente})

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
    ).order_by('-fecha_consulta', '-hora_inicio')

    context = {
        'paciente': paciente,
        'citas': citas,
        'ahora': ahora,
        'citas_futuras': citas_futuras,
        'citas_pasadas': citas_pasadas,
    }

    return render(request, 'paciente/agenda.html', context)


@login_required
def agregar_poliza(request):
    # Obtener el paciente directamente desde el usuario logueado
    paciente = getattr(request.user, 'fk_paciente', None)

    if not paciente:
        messages.error(request, "No se puede agregar póliza porque no hay paciente asignado a este usuario.")
        return redirect('dashboard_paciente')  # Redirige al dashboard

    if request.method == "POST":
        form = PolizaSeguroForm(request.POST)
        if form.is_valid():
            poliza = form.save(commit=False)
            poliza.paciente = paciente
            poliza.save()
            messages.success(request, "Póliza agregada correctamente.")
            return redirect('dashboard_paciente')
    else:
        form = PolizaSeguroForm()

    return render(request, 'paciente/agregar_poliza.html', {'form': form})



@login_required
def gestionar_contacto_emergencia(request):
    paciente = getattr(request.user, 'fk_paciente', None)

    if not paciente:
        messages.error(request, "No hay paciente asignado a este usuario.")
        return redirect('dashboard_paciente')

    contacto = getattr(paciente, 'contactoemergencia', None)

    if request.method == "POST":
        form = ContactoEmergenciaForm(request.POST, instance=contacto)
        if form.is_valid():
            contacto = form.save(commit=False)
            contacto.paciente = paciente
            contacto.save()
            messages.success(request, "Contacto de emergencia guardado correctamente.")
            return redirect('contacto_emergencia')   # 👈 aquí está la magia (se limpia el form)
    else:
        form = ContactoEmergenciaForm(instance=contacto)

    return render(request, "paciente/contacto_emergencia.html", {"form": form})

def buscar_medicos(request):
    tipo_filtro = request.GET.get("tipo_filtro", "todo")
    q = request.GET.get("q", "").strip()

    medicos = Medico.objects.all()

    if q:
        if tipo_filtro == "nombre":
            medicos = medicos.filter(
                Q(usuario__nombre__icontains=q) | Q(usuario__apellido__icontains=q)
            )
        elif tipo_filtro == "especialidad":
            medicos = medicos.filter(especialidad__icontains=q)
        elif tipo_filtro == "ubicacion":
            medicos = medicos.filter(ubicacion__icontains=q)
        # 'todo' busca en todos los campos
        elif tipo_filtro == "todo":
            medicos = medicos.filter(
                Q(usuario__nombre__icontains=q) |
                Q(usuario__apellido__icontains=q) |
                Q(especialidad__icontains=q) |
                Q(ubicacion__icontains=q)
            )

    context = {
        "medicos": medicos,
        "tipo_filtro": tipo_filtro,
        "q": q,
    }

    return render(request, "paciente/buscar_medicos.html", context)

def mapa_medicos(request):
    # Traer todos los médicos que tengan clínica con lat/lng
    medicos = Medico.objects.exclude(fk_clinica__latitud__isnull=True, fk_clinica__longitud__isnull=True)
    
    context = {
        "medicos": medicos
    }
    return render(request, "paciente/mapa_medicos.html", context)