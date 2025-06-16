from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from bd.models import Usuario, Paciente,Rol,Medico
from django.db import IntegrityError
from medico import views


def inicio_view(request):
    if request.user.is_authenticated:
        return redirigir_segun_usuario(request.user)
    return render(request, 'inicio/inicial.html')



def login_view(request):
    if request.user.is_authenticated:
        return redirigir_segun_usuario(request.user)
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirigir_segun_usuario(user)
        
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

from django.contrib.auth.hashers import make_password

def registroDoctor_view(request):
    if request.method == 'POST':
        nombre_apellido = request.POST.get('nombre_apellido')
        especialidad = request.POST.get('especialidad')
        licencia = request.POST.get('licencia')

        # Guardar en sesión para usarlos en el paso 2
        request.session['nombre_apellido'] = nombre_apellido
        request.session['especialidad'] = especialidad
        request.session['licencia'] = licencia

        return redirect('registro_doctor2')  # O la URL correspondiente
    
    return render(request, 'inicio/registro_docto1.html')


def registroDoctor2_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')

        request.session['correo'] = correo
        request.session['telefono'] = telefono

        return redirect('registro_doctor3')

    return render(request, 'inicio/registro_docto2.html')


from django.contrib.auth.hashers import make_password

def registroDoctor3_view(request):
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('registro_doctor3')

        request.session['password'] = make_password(password1)  # Encriptada
        return redirect('registro_doctor4')

    return render(request, 'inicio/registro_docto3.html')


def registroDoctor4_view(request):
    if request.method == 'POST':
        nombre_apellido = request.session.get('nombre_apellido')
        especialidad = request.session.get('especialidad')
        licencia = request.session.get('licencia')
        correo = request.session.get('correo')
        telefono = request.session.get('telefono')
        password = request.session.get('password')

        if not all([nombre_apellido, especialidad, licencia, correo, telefono, password]):
            return redirect('registro_doctor')  # Manejo de error

        # Validar que el correo no esté registrado
        if Usuario.objects.filter(correo=correo).exists():
            messages.error(request, "Este correo ya está registrado.")
            return redirect('registro_doctor')

        partes = nombre_apellido.split(" ", 1)
        nombre = partes[0]
        apellido = partes[1] if len(partes) > 1 else ""

        try:
            medico = Medico.objects.create(
                no_jvpm=licencia,
                especialidad=especialidad
            )

            usuario = Usuario.objects.create(
                user_name=correo,
                correo=correo,
                password=password,
                telefono=telefono,
                nombre=nombre,
                apellido=apellido,
                fk_medico=medico
            )

            # Limpiar sesión
            for key in ['nombre_apellido', 'especialidad', 'licencia', 'correo', 'telefono', 'password']:
                request.session.pop(key, None)

            return redirect('vista_medico')
        except IntegrityError:
            messages.error(request, "El correo ya está en uso.")
            return redirect('registro_doctor')

    return render(request, 'inicio/registro_docto4.html')



def registroPaciente1_view(request):
    if request.method == 'POST':
        nombre_apellido = request.POST.get('nombre_apellido')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        dui = request.POST.get('dui')
        genero = request.POST.get('genero')

        request.session['nombre_apellido'] = nombre_apellido
        request.session['fecha_nacimiento'] = fecha_nacimiento
        request.session['dui'] = dui
        request.session['genero'] = genero

        return redirect('registro_paciente2')

    return render(request, 'inicio/registro_paciente1.html')


def registroPaciente2_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')

        request.session['correo'] = correo
        request.session['telefono'] = telefono

        return redirect('registro_paciente3')

    return render(request, 'inicio/registro_paciente2.html')


from django.contrib import messages
from django.contrib.auth.hashers import make_password

def registroPaciente3_view(request):
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('registro_paciente3')

        request.session['password'] = make_password(password1)
        return redirect('registro_paciente4')

    return render(request, 'inicio/registro_paciente3.html')


def registroPaciente4_view(request):
    if request.method == 'POST':
        try:
            correo = request.session.get('correo')
            telefono = request.session.get('telefono')
            fecha_nacimiento = request.session.get('fecha_nacimiento')
            dui = request.session.get('dui')
            genero = request.session.get('genero')
            password = request.session.get('password')
            nombre_apellido = request.session.get('nombre_apellido')

            # Validación de campos
            if not all([correo, telefono, fecha_nacimiento, dui, genero, password, nombre_apellido]):
                messages.error(request, "Faltan datos del formulario.")
                return redirect('registro_paciente1')

            # Verificar si el correo ya está en uso
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, "Este correo ya está registrado.")
                return redirect('registro_paciente1')

            # Dividir nombre y apellido
            partes = nombre_apellido.split(" ", 1)
            nombre = partes[0]
            apellido = partes[1] if len(partes) > 1 else ""

            # Crear paciente
            paciente = Paciente.objects.create(
                dui=dui
            )

            # Obtener el rol "paciente"
            rol = Rol.objects.get(nombre__iexact='paciente')

            # Crear usuario
            usuario = Usuario.objects.create(
                nombre=nombre,
                apellido=apellido,
                sexo=genero,
                fecha_nacimiento=fecha_nacimiento,
                correo=correo,
                telefono=telefono,
                password=password,  # ya está encriptada
                fk_paciente=paciente,
                fk_rol=rol,
                user_name=correo  # correo como nombre de usuario
            )

            # Limpiar sesión
            for key in ['nombre_apellido', 'fecha_nacimiento', 'dui', 'genero', 'correo', 'telefono', 'password']:
                request.session.pop(key, None)

            messages.success(request, "Registro exitoso")
            return redirect('vista_paciente')

        except Rol.DoesNotExist:
            messages.error(request, "Rol 'paciente' no encontrado.")
            return redirect('registro_paciente1')
        except IntegrityError:
            messages.error(request, "El correo ya está en uso.")
            return redirect('registro_paciente1')
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {str(e)}")
            return redirect('registro_paciente1')

    return render(request, 'inicio/registro_paciente4.html')

def contraOlvidada_view(request):
    return render(request, 'inicio/contra_olvidada.html')

def autenticacion_view(request):
    return render(request, 'inicio/autenticacion.html')

def vistaMedico_view(request):
    return redirect('dashboard_doctor')

def vistaPacienteview(request):
    return render(request, 'paciente/dashboard_paciente.html') 

def redirigir_segun_usuario(user):
    if hasattr(user, 'fk_medico') and user.fk_medico_id:
        return redirect('vista_medico')
    elif hasattr(user, 'fk_paciente') and user.fk_paciente_id:
        return redirect('vista_paciente')
    else:
        return redirect('/admin/')

