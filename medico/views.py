from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.db import connection
from collections import namedtuple

from bd.models import RecetaMedica, CitasMedicas, Clinica, HorarioMedico, Medico, Usuario, Paciente

@login_required 
def views_home(request):
    return redirect('dashboard_doctor') 

@csrf_protect
def receta_medica(request):
    if request.method == 'POST':
        medicamento = request.POST.get('medicamento')
        via = request.POST.get('via_administracion')
        dosis = request.POST.get('dosis')
        fecha_inicio = request.POST.get('fecha_inicio_tratamiento')
        fecha_fin = request.POST.get('fecha_fin_tratamiento')
        cita_id = request.POST.get('fk_citas_medicas')

        try:
            cita = CitasMedicas.objects.get(id_cita_medicas=cita_id)

            RecetaMedica.objects.create(
                medicamento=medicamento,
                via_administracion=via,
                dosis=dosis,
                fecha_inicio_tratamiento=fecha_inicio,
                fecha_fin_tratamiento=fecha_fin,
                fk_citas_medicas=cita
            )

            messages.success(request, "Receta guardada correctamente.")
            return redirect('receta_medica')

        except CitasMedicas.DoesNotExist:
            messages.error(request, "La cita médica seleccionada no existe.")
        except Exception as e:
            messages.error(request, f"Error al guardar la receta: {e}")

    citas = CitasMedicas.objects.all()
    contexto = {
        'citas': [
            {
                'id': c.id_cita_medicas,
                'descripcion': f"Cita #{c.id_cita_medicas} - {c.fecha_consulta}"
            }
            for c in citas
        ]
    }

    return render(request, 'medico/receta_medica.html', contexto)

def ubicacion_doctor(request):
    return render(request, 'medico/ubicacion_doctor.html')

@login_required
def clinica_doctor(request):
    usuario = request.user
    medico = usuario.fk_medico
    clinica = medico.fk_clinica
    horario = medico.fk_horario_medico

    return render(request, 'medico/clinica_doctor.html', {
        'usuario': usuario,
        'medico': medico,
        'clinica': clinica,
        'horario': horario,
    })

@login_required
def config_clinica(request):
    clinica = request.user.fk_medico.fk_clinica

    if request.method == 'POST':
        clinica.nombre = request.POST.get('nombre')
        clinica.direccion = request.POST.get('direccion')
        clinica.telefono_clinica = request.POST.get('telefono_clinica')
        clinica.correo_electronico_clinica = request.POST.get('correo_electronico_clinica')
        clinica.sitio_web = request.POST.get('sitio_web')
        clinica.facebook = request.POST.get('facebook')
        clinica.instagram = request.POST.get('instagram')
        clinica.save()

        messages.success(request, "Información de la clínica actualizada correctamente.")
        return redirect('clinica_doctor')

    return render(request, 'medico/config_clinica.html')

@login_required
def config_horario(request):
    medico = request.user.fk_medico
    horario = medico.fk_horario_medico

    if request.method == 'POST':
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        status = request.POST.get('status_disponibilidad')

        horario.hora_inicio = hora_inicio
        horario.hora_fin = hora_fin
        horario.status_disponibilidad = status
        horario.save()

        messages.success(request, "Horario actualizado correctamente.")
        return redirect('dashboard_doctor')

    return render(request, 'medico/config_horario.html')

@login_required
def config_perfildoc(request):
    medico = request.user.fk_medico

    if request.method == 'POST':
        medico.especialidad = request.POST.get('especialidad')
        medico.sub_especialidad_1 = request.POST.get('sub_especialidad_1')
        medico.sub_especialidad_2 = request.POST.get('sub_especialidad_2')
        medico.no_jvpm = request.POST.get('no_jvpm')
        medico.dui = request.POST.get('dui')
        medico.descripcion = request.POST.get('descripcion')
        medico.save()

        messages.success(request, "Perfil médico actualizado correctamente.")
        return redirect('clinica_doctor')

    return render(request, 'medico/config_perfildoc.html')

@login_required
def dashboard_doctor(request):
    usuario = request.user
    medico = usuario.fk_medico

    if not medico:
        return render(request, 'medico/no_es_medico.html')

    citas_raw = CitasMedicas.objects.filter(
        fk_medico=medico
    ).order_by('-fecha_consulta', '-hora_inicio').select_related('fk_paciente')

    citas = []
    for cita in citas_raw:
        user_paciente = Usuario.objects.filter(fk_paciente=cita.fk_paciente).first()
        nombre_completo = f"{user_paciente.nombre} {user_paciente.apellido}" if user_paciente else "Paciente desconocido"
        citas.append({
            'id': cita.id_cita_medicas,
            'fecha': cita.fecha_consulta,
            'hora': cita.hora_inicio,
            'motivo': cita.des_motivo_consulta_paciente,
            'estado': cita.status_cita_medica,
            'nombre_paciente': nombre_completo,
            'paciente_id': cita.fk_paciente.id_paciente
        })

    return render(request, 'medico/dashboard_doctor.html', {'citas': citas})

@require_POST
@login_required
def actualizar_estado_cita(request, cita_id):
    cita = get_object_or_404(CitasMedicas, id_cita_medicas=cita_id, fk_medico=request.user.fk_medico)

    accion = request.POST.get('accion')
    if accion == 'aceptar':
        cita.status_cita_medica = 'En proceso'
    elif accion == 'cancelar':
        cita.status_cita_medica = 'Cancelado'

    cita.save()
    return redirect('dashboard_doctor')

@login_required
def realizar_consulta(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id, doctor=request.user)

    if request.method == 'POST':
        pass

    return render(request, 'medico/realizar_consulta.html', {'paciente': paciente})
