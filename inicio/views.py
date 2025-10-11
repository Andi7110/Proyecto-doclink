from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from bd.models import Usuario, Paciente,Rol,Medico, EmailVerificationToken
from django.db import IntegrityError
import pyotp
import qrcode
import io
import base64
import secrets
from datetime import timedelta
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import logging


def send_html_email(subject, template_name, context, recipient_list, from_email=None):
    """
    Envía un email HTML con fallback a texto plano usando templates de Django.
    """
    if from_email is None:
        from django.conf import settings
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)

    # Cargar templates HTML y texto
    html_template = get_template(f'emails/{template_name}.html')
    text_template = get_template(f'emails/{template_name}.txt')

    # Renderizar contenido
    html_content = html_template.render(context)
    text_content = text_template.render(context)

    # Crear email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=recipient_list
    )
    email.attach_alternative(html_content, "text/html")

    # Enviar
    email.send(fail_silently=False)


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
                if user.is_active:
                    login(request, user)
                    if user.two_factor_enabled:
                        return redirect('two_factor_verify')
                    else:
                        return redirigir_segun_usuario(user)
                else:
                    messages.error(request, "Tu cuenta no está activada. Contacta al administrador.")
            else:
                messages.error(request, "Usuario o contraseña incorrectos")
    else:
        form = CustomLoginForm()

    return render(request, 'inicio/login.html', {'form': form})



@require_POST
@csrf_protect
def custom_logout(request):
    return LogoutView.as_view()(request)


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
            # Crear médico
            medico = Medico.objects.create(
                no_jvpm=licencia,
                especialidad=especialidad
            )

            # Obtener el rol "medico"
            rol = Rol.objects.get(nombre__iexact='medico')

            # Crear usuario
            usuario = Usuario.objects.create(
                user_name=correo,
                correo=correo,
                password=password,
                telefono=telefono,
                nombre=nombre,
                apellido=apellido,
                fk_medico=medico,
                fk_rol=rol,
                is_active=True  # Activado inmediatamente para desarrollo
            )

            # Para desarrollo: sin verificación de email
            # Crear token de verificación
            # token = secrets.token_urlsafe(32)
            # expires_at = timezone.now() + timedelta(hours=24)
            # EmailVerificationToken.objects.create(user=usuario, token=token, expires_at=expires_at)

            # Enviar email de verificación
            # verification_url = f'http://127.0.0.1:8000/verificar-email/{token}/'
            # context = {
            #     'user_name': f'{usuario.nombre} {usuario.apellido}',
            #     'verification_url': verification_url,
            #     'user_type': 'medico'
            # }
            # send_html_email(
            #     'Verifica tu cuenta en DocLink',
            #     'email_verification',
            #     context,
            #     [usuario.correo]
            # )

            # Limpiar sesión
            for key in ['nombre_apellido', 'especialidad', 'licencia', 'correo', 'telefono', 'password']:
                request.session.pop(key, None)

            messages.success(request, "Registro exitoso. Ya puedes iniciar sesión.")
            return redirect('login')

        except Rol.DoesNotExist:
            messages.error(request, "Rol 'medico' no encontrado.")
            return redirect('registro_doctor')
        except IntegrityError:
            messages.error(request, "El correo ya está en uso.")
            return redirect('login')
        except Exception as e:
            logging.exception("Error al registrar doctor: %s", str(e))
            messages.error(request, f"Error al registrar: {str(e)}")
            return redirect('login')

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

            print(f"Session data: correo={correo}, telefono={telefono}, fecha_nacimiento={fecha_nacimiento}, dui={dui}, genero={genero}, password={password}, nombre_apellido={nombre_apellido}")

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
                user_name=correo,  # correo como nombre de usuario
                is_active=True  # Activado inmediatamente para desarrollo
            )

            # Para desarrollo: sin verificación de email
            # Crear token de verificación
            # token = secrets.token_urlsafe(32)
            # expires_at = timezone.now() + timedelta(hours=24)
            # EmailVerificationToken.objects.create(user=usuario, token=token, expires_at=expires_at)

            # Enviar email de verificación
            # verification_url = f'http://127.0.0.1:8000/verificar-email/{token}/'
            # context = {
            #     'user_name': f'{usuario.nombre} {usuario.apellido}',
            #     'verification_url': verification_url,
            #     'user_type': 'paciente'
            # }
            # send_html_email(
            #     'Verifica tu cuenta en DocLink',
            #     'email_verification',
            #     context,
            #     [usuario.correo]
            # )

            # Limpiar sesión
            for key in ['nombre_apellido', 'fecha_nacimiento', 'dui', 'genero', 'correo', 'telefono', 'password']:
                request.session.pop(key, None)

            messages.success(request, "Registro exitoso. Ya puedes iniciar sesión.")
            return redirect('login')

        except Rol.DoesNotExist:
            messages.error(request, "Rol 'paciente' no encontrado.")
            return redirect('login')
        except IntegrityError:
            messages.error(request, "El correo ya está en uso.")
            return redirect('login')
        except Exception as e:
            logging.exception("Error al registrar paciente: %s", str(e))
            messages.error(request, f"Error al registrar: {str(e)}")
            return redirect('login')

    return render(request, 'inicio/registro_paciente4.html')

@login_required
def cambiar_password_view(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(current_password):
            messages.error(request, "Contraseña actual incorrecta.")
            return redirect('cambiar_password')

        if new_password1 != new_password2:
            messages.error(request, "Las nuevas contraseñas no coinciden.")
            return redirect('cambiar_password')

        if len(new_password1) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            return redirect('cambiar_password')

        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, "Contraseña cambiada exitosamente.")
        return redirect('login')

    return render(request, 'inicio/cambiar_password.html')

def contraOlvidada_view(request):
    reset_code = None
    email = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'generate':  # Generar código
            email = request.POST.get('email')

            try:
                usuario = Usuario.objects.get(correo=email)
                # Generar código temporal
                import random
                reset_code = str(random.randint(100000, 999999))

                # Guardar código en sesión (en producción usarías un modelo)
                request.session['reset_email'] = email
                request.session['reset_code'] = reset_code

                # Mostrar código en consola (para desarrollo)
                print(f"\n=== CÓDIGO DE RECUPERACIÓN PARA {email} ===")
                print(f"Código: {reset_code}")
                print("=" * 50)

                messages.success(request, f"¡Código generado! Cópialo de arriba y continúa con el cambio de contraseña.")

            except Usuario.DoesNotExist:
                messages.error(request, "No existe una cuenta con ese email.")

        elif action == 'reset':  # Cambiar contraseña
            code = request.POST.get('code')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')

            # Verificar código
            if code != request.session.get('reset_code'):
                messages.error(request, "Código incorrecto.")
            elif new_password1 != new_password2:
                messages.error(request, "Las contraseñas no coinciden.")
            elif len(new_password1) < 8:
                messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            else:
                # Cambiar contraseña
                email = request.session.get('reset_email')
                try:
                    usuario = Usuario.objects.get(correo=email)
                    usuario.set_password(new_password1)
                    usuario.save()

                    # Limpiar sesión
                    del request.session['reset_email']
                    del request.session['reset_code']

                    messages.success(request, "¡Contraseña cambiada exitosamente! Ya puedes iniciar sesión.")
                    return redirect('login')

                except Usuario.DoesNotExist:
                    messages.error(request, "Error al cambiar contraseña.")

    return render(request, 'inicio/contra_olvidada.html', {
        'reset_code': reset_code,
        'email': email
    })

def reset_password_view(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        # Verificar código
        if code != request.session.get('reset_code'):
            messages.error(request, "Código incorrecto.")
            return redirect('reset_password')

        if new_password1 != new_password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('reset_password')

        if len(new_password1) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            return redirect('reset_password')

        # Cambiar contraseña
        email = request.session.get('reset_email')
        try:
            usuario = Usuario.objects.get(correo=email)
            usuario.set_password(new_password1)
            usuario.save()

            # Limpiar sesión
            del request.session['reset_email']
            del request.session['reset_code']

            messages.success(request, "Contraseña cambiada exitosamente. Ya puedes iniciar sesión.")
            return redirect('login')

        except Usuario.DoesNotExist:
            messages.error(request, "Error al cambiar contraseña.")

    return render(request, 'inicio/reset_password.html')

def autenticacion_view(request):
    return render(request, 'inicio/autenticacion.html')

@login_required
def vistaMedico_view(request):
    return redirect('dashboard_doctor.html')

@login_required
def vistaPacienteview(request):
    return render(request, 'paciente/dashboard_paciente.html')

def redirigir_segun_usuario(user):
    if hasattr(user, 'fk_medico') and user.fk_medico_id:
        return redirect('dashboard_doctor')

    elif hasattr(user, 'fk_paciente') and user.fk_paciente_id:
        return redirect('vista_paciente')
    else:
        return redirect('/admin/')

@login_required
def two_factor_setup_view(request):
    user = request.user
    if request.method == 'POST':
        if 'enable' in request.POST:
            # Generar secret
            secret = pyotp.random_base32()
            user.two_factor_secret = secret
            user.two_factor_enabled = False  # Aún no verificado
            user.save()

            # Generar QR
            totp = pyotp.TOTP(secret)
            uri = totp.provisioning_uri(name=user.correo, issuer_name="DocLink")
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(uri)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code = base64.b64encode(buffer.getvalue()).decode()

            return render(request, 'inicio/two_factor_setup.html', {
                'qr_code': qr_code,
                'secret': secret
            })
        elif 'verify' in request.POST:
            code = request.POST.get('code')
            totp = pyotp.TOTP(user.two_factor_secret)
            if totp.verify(code):
                user.two_factor_enabled = True
                user.save()
                messages.success(request, "2FA habilitado exitosamente.")
                return redirect('two_factor_setup')
            else:
                messages.error(request, "Código incorrecto.")
        elif 'disable' in request.POST:
            user.two_factor_enabled = False
            user.two_factor_secret = None
            user.save()
            messages.success(request, "2FA deshabilitado.")
            return redirect('two_factor_setup')

    return render(request, 'inicio/two_factor_setup.html', {
        'two_factor_enabled': user.two_factor_enabled
    })

@login_required
def two_factor_verify_view(request):
    if not request.user.two_factor_enabled:
        return redirect('dashboard_doctor')  # O donde corresponda

    if request.method == 'POST':
        code = request.POST.get('code')
        totp = pyotp.TOTP(request.user.two_factor_secret)
        if totp.verify(code):
            request.session['two_factor_verified'] = True
            return redirigir_segun_usuario(request.user)
        else:
            messages.error(request, "Código incorrecto.")

    return render(request, 'inicio/two_factor_verify.html')

def verify_email(request, token):
    try:
        verification = EmailVerificationToken.objects.get(token=token)
        if verification.is_expired():
            messages.error(request, "El token de verificación ha expirado.")
            return redirect('login')
        user = verification.user
        user.is_active = True
        user.save()
        verification.delete()

        # Enviar email de bienvenida basado en el tipo de usuario
        try:
            if hasattr(user, 'fk_medico') and user.fk_medico:
                # Es médico
                context = {
                    'user_name': f'{user.nombre} {user.apellido}',
                    'especialidad': user.fk_medico.especialidad,
                    'licencia': user.fk_medico.no_jvpm
                }
                send_html_email(
                    '¡Bienvenido a DocLink - Médico!',
                    'welcome_medico',
                    context,
                    [user.correo]
                )
            elif hasattr(user, 'fk_paciente') and user.fk_paciente:
                # Es paciente
                context = {
                    'user_name': f'{user.nombre} {user.apellido}'
                }
                send_html_email(
                    '¡Bienvenido a DocLink - Paciente!',
                    'welcome_paciente',
                    context,
                    [user.correo]
                )
        except Exception as e:
            logging.exception("Error al enviar email de bienvenida: %s", str(e))
            # No fallar la verificación por error en email de bienvenida

        messages.success(request, "Cuenta verificada exitosamente. Ahora puedes iniciar sesión.")
        return redirect('login')
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, "Token de verificación inválido.")
        return redirect('login')

from medico import views
