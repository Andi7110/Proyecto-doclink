from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from bd.models import Usuario, Medico


def inicio_view(request):
    return render(request, 'inicio/inicial.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/admin/')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)

                # Verificar si el usuario tiene un médico asociado
                if user.fk_medico_id:
                    return redirect('vista_medico')  # Cambia esto al `name` real de la vista de médico

                # Puedes verificar roles adicionales aquí
                return redirect('/admin/')
        
        messages.error(request, "Usuario o contraseña incorrectos")
    else:
        form = CustomLoginForm()
    
    return render(request, 'inicio/login.html', {'form': form})



@require_POST
@csrf_protect
def custom_logout(request):
    return LogoutView.as_view()(request)


@login_required
def mi_vista_protegida(request):
    # Tu lógica aquí
    return render(request, 'inicio/registro_docto4.html')

def seleccion_view(request):
    return render(request, 'inicio/seleccion_registro.html')

def registroDoctor_view(request):
    return render(request, 'inicio/registro_docto1.html')

def registroDoctor2_view(request):
    return render(request, 'inicio/registro_docto2.html')

def registroDoctor3_view(request):
    return render(request, 'inicio/registro_docto3.html')

def registroDoctor4_view(request):
    return render(request, 'inicio/registro_docto4.html')

def registroPaciente1_view(request):
    return render(request, 'inicio/registro_paciente1.html')

def registroPaciente2_view(request):
    return render(request, 'inicio/registro_paciente2.html')

def registroPaciente3_view(request):
    return render(request, 'inicio/registro_paciente3.html')

def registroPaciente4_view(request):
    return render(request, 'inicio/registro_paciente4.html')

def contraOlvidada_view(request):
    return render(request, 'inicio/contra_olvidada.html')

def autenticacion_view(request):
    return render(request, 'inicio/autenticacion.html')

def vistaMedico_view(request):
    return render(request, 'medico/dashboard_doctor.html')  
