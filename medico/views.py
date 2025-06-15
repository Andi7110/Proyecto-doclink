from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import ConsultaForm
from .models import Consulta
from paciente.models import Paciente

@login_required
def views_home(request):
    return render(request, 'medico/home.html')

@login_required
def vistaMedico_view(request):
    doctor = request.user  # Este debe ser un objeto del modelo Usuario (bd.Usuario)
    print(f"Usuario logueado: {doctor} (ID: {doctor.id})")  # Esto mostrará en la terminal
    pacientes = Paciente.objects.filter(doctor=doctor)
    return render(request, 'medico/dashboard_doctor.html', {'pacientes': pacientes})

@login_required
def realizar_consulta(request, paciente_id):
    # Verifica que el paciente pertenezca al doctor logueado para seguridad
    paciente = get_object_or_404(Paciente, id=paciente_id, doctor=request.user)

    consulta = Consulta.objects.filter(
        paciente=paciente,
        doctor=request.user,
        consulta_completada=False
    ).first()

    if request.method == 'POST':
        form = ConsultaForm(request.POST, request.FILES, instance=consulta)
        if form.is_valid():
            nueva_consulta = form.save(commit=False)
            nueva_consulta.paciente = paciente
            nueva_consulta.doctor = request.user
            nueva_consulta.save()
            return redirect('historial_consulta', paciente_id=paciente.id)
    else:
        form = ConsultaForm(instance=consulta)

    context = {
        'paciente': paciente,
        'form': form,
        'consulta': consulta,
    }
    return render(request, 'medico/realizar_consulta.html', context)

