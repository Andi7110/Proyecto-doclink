from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from datetime import date, datetime, time
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from django.db import transaction
from .decorators import paciente_required
from django.shortcuts import render, redirect, get_object_or_404
from bd.models import PolizaSeguro, ContactoEmergencia, GastosAdicionales
from .forms import PolizaSeguroForm, ContactoEmergenciaForm, PerfilPacienteForm, MetodoPagoForm

from bd.models import Usuario, Medico, Paciente, CitasMedicas, Clinica, ValoracionConsulta, SeguimientoClinico, MetodosPago, Factura

DEPARTAMENTOS_EL_SALVADOR = [
    'Ahuachapán', 'Santa Ana', 'Sonsonate', 'Chalatenango', 'Cuscatlán',
    'La Libertad', 'La Paz', 'San Miguel', 'San Salvador', 'San Vicente',
    'Cabañas', 'Usulután', 'Morazán', 'La Unión'
]

def obtener_departamento_direccion(direccion):
    if not direccion:
        return 'No especificado'
    for depto in DEPARTAMENTOS_EL_SALVADOR:
        if depto.lower() in direccion.lower():
            return depto
    return 'No especificado'


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
    else:
        edad = ""

    # Filtro por especialidad
    especialidad = request.GET.get('especialidad')
    clinica_id = request.GET.get('clinica')
    medicos = Medico.objects.all()
    if especialidad:
        medicos = medicos.filter(especialidad__icontains=especialidad)
    if clinica_id:
        medicos = medicos.filter(fk_clinica_id=clinica_id)

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
            'precio_consulta': medico.precio_consulta,
        })

    if request.method == 'POST':
        # Procesar formulario de cita y pago
        medico_id = request.POST.get('medico_id')
        fecha_str = request.POST.get('fecha_cita')
        hora_str = request.POST.get('hora_cita')
        motivo = request.POST.get('motivo')

        # Datos del pago
        metodo_pago = request.POST.get('metodo_pago')
        numero_tarjeta = request.POST.get('numero_tarjeta')
        fecha_expiracion = request.POST.get('fecha_expiracion')
        cvv = request.POST.get('cvv')
        nombre_titular = request.POST.get('nombre_titular')
        tipo_tarjeta = request.POST.get('tipo_tarjeta')

        # Validar campos básicos de la cita
        if not (medico_id and fecha_str and hora_str and motivo):
            messages.error(request, "Por favor completa todos los campos de la cita.")
            return redirect('agendar_cita')

        # Validar campos de pago
        if not metodo_pago:
            messages.error(request, "Por favor selecciona un método de pago.")
            return redirect('agendar_cita')

        # Obtener el precio de consulta del médico
        try:
            medico = Medico.objects.get(id_medico=medico_id)
            monto_consulta = medico.precio_consulta
            if not monto_consulta:
                messages.error(request, "El médico no ha configurado un precio de consulta. Contacta al médico.")
                return redirect('agendar_cita')
        except Medico.DoesNotExist:
            messages.error(request, "Médico no encontrado.")
            return redirect('agendar_cita')

        # Validar campos de tarjeta si es necesario
        if metodo_pago == 'tarjeta':
            if not all([numero_tarjeta, fecha_expiracion, cvv, nombre_titular, tipo_tarjeta]):
                messages.error(request, "Por favor completa todos los campos de la tarjeta.")
                return redirect('agendar_cita')

            # Validar formato de número de tarjeta
            if not numero_tarjeta.isdigit() or len(numero_tarjeta) != 16:
                messages.error(request, "El número de tarjeta debe tener 16 dígitos.")
                return redirect('agendar_cita')

            # Validar formato de fecha de expiración
            import re
            if not re.match(r'^\d{2}/\d{2}$', fecha_expiracion):
                messages.error(request, "Formato de fecha de expiración inválido (MM/YY).")
                return redirect('agendar_cita')

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora = datetime.strptime(hora_str, '%H:%M').time()
            monto = float(monto_consulta)
        except ValueError:
            messages.error(request, "Formato de fecha, hora o monto inválido.")
            return redirect('agendar_cita')

        try:
            medico = Medico.objects.get(id_medico=medico_id)
        except Medico.DoesNotExist:
            messages.error(request, "Médico no encontrado.")
            return redirect('agendar_cita')

        # Verificar que no haya cita duplicada
        if CitasMedicas.objects.filter(
            fk_medico=medico,
            fecha_consulta=fecha,
            hora_inicio=hora
        ).exists():
            messages.error(request, "Ya hay una cita agendada con este médico en esa fecha y hora.")
            return redirect('agendar_cita')

        try:
            with transaction.atomic():
                # Crear método de pago si es tarjeta
                metodo_pago_obj = None
                if metodo_pago == 'tarjeta':
                    metodo_pago_obj = MetodosPago.objects.create(
                        tipometodopago='tarjeta',
                        numero_tarjeta=numero_tarjeta,
                        fecha_expiracion=fecha_expiracion,
                        cvv=cvv,
                        nombre_titular=nombre_titular,
                        tipo_tarjeta=tipo_tarjeta
                    )
                else:
                    # Para efectivo, crear registro básico
                    metodo_pago_obj = MetodosPago.objects.create(
                        tipometodopago='efectivo'
                    )

                # Crear factura
                factura = Factura.objects.create(
                    fecha_emision=timezone.now().date(),
                    monto=monto,
                    fk_metodopago=metodo_pago_obj
                )

                # Crear cita médica
                cita = CitasMedicas.objects.create(
                    fecha_consulta=fecha,
                    hora_inicio=hora,
                    status_cita_medica="Pendiente",
                    des_motivo_consulta_paciente=motivo,
                    fk_paciente=paciente,
                    fk_medico=medico,
                    fk_factura=factura,
                    metodo_pago=metodo_pago,
                    monto_consulta=monto,
                    pago_confirmado=False  # Se confirma cuando la cita se pone en proceso
                )

            messages.success(request, "¡Cita agendada correctamente!")
            # Consumir mensajes para que no aparezcan en otras páginas
            list(messages.get_messages(request))
            return redirect('agenda')

        except Exception as e:
            messages.error(request, f"Error al guardar la cita: {e}")
            return redirect('agendar_cita')

    context = {
        'edad': edad,
        'paciente': paciente,
        'medicos': medicos_con_nombre,
        'especialidad_seleccionada': especialidad,
        'clinica_seleccionada': clinica_id,
        'nombre': usuario.get_full_name() if callable(getattr(usuario, 'get_full_name', None)) else f"{usuario.nombre} {usuario.apellido}",
        'sexo': getattr(usuario, 'sexo', '') or '',
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

    # Query base (sin enriquecer)
    citas = CitasMedicas.objects.filter()

    # Construir lista enriquecida de citas futuras (para mostrar acciones si ya están "Completada")
    citas_qs_futuras = CitasMedicas.objects.filter(
        fk_paciente=paciente,
        status_cita_medica__in=['Pendiente', 'En proceso']
    ).filter(
        Q(fecha_consulta__gt=hoy) |
        Q(fecha_consulta=hoy, hora_inicio__gte=ahora)
    ).order_by('fecha_consulta', 'hora_inicio').select_related('fk_medico', 'fk_medico__fk_clinica')

    citas_futuras = []
    for cita in citas_qs_futuras:
        tiene_valoracion = ValoracionConsulta.objects.filter(fk_cita=cita).exists()
        usuario_medico = Usuario.objects.filter(fk_medico=cita.fk_medico).first()
        nombre_medico = usuario_medico.get_full_name() if usuario_medico else "Nombre no disponible"
        especialidad = cita.fk_medico.especialidad if cita.fk_medico else ""
        clinica = cita.fk_medico.fk_clinica.nombre if cita.fk_medico and cita.fk_medico.fk_clinica else ""

        citas_futuras.append({
            'cita': cita,
            'tiene_valoracion': tiene_valoracion,
            'nombre_medico': nombre_medico,
            'especialidad': especialidad,
            'clinica': clinica,
        })

    ahora = datetime.now()

    # Citas completadas
    citas_completadas = CitasMedicas.objects.filter(
        fk_paciente=paciente,
        status_cita_medica='Completada'
    ).order_by('-fecha_consulta', '-hora_inicio').select_related('fk_medico', 'fk_medico__fk_clinica')

    # Enriquecer citas completadas con info de valoración
    citas_completadas_con_valoracion = []
    for cita in citas_completadas:
        tiene_valoracion = ValoracionConsulta.objects.filter(fk_cita=cita).exists()
        usuario_medico = Usuario.objects.filter(fk_medico=cita.fk_medico).first()
        nombre_medico = usuario_medico.get_full_name() if usuario_medico else "Nombre no disponible"
        especialidad = cita.fk_medico.especialidad if cita.fk_medico else ""
        clinica = cita.fk_medico.fk_clinica.nombre if cita.fk_medico and cita.fk_medico.fk_clinica else ""

        citas_completadas_con_valoracion.append({
            'cita': cita,
            'tiene_valoracion': tiene_valoracion,
            'nombre_medico': nombre_medico,
            'especialidad': especialidad,
            'clinica': clinica,
        })

    # Citas canceladas
    citas_canceladas = CitasMedicas.objects.filter(
        fk_paciente=paciente,
        status_cita_medica='Cancelado'
    ).order_by('-fecha_consulta', '-hora_inicio').select_related('fk_medico', 'fk_medico__fk_clinica')

    citas_canceladas_lista = []
    for cita in citas_canceladas:
        usuario_medico = Usuario.objects.filter(fk_medico=cita.fk_medico).first()
        nombre_medico = usuario_medico.get_full_name() if usuario_medico else "Nombre no disponible"
        especialidad = cita.fk_medico.especialidad if cita.fk_medico else ""
        clinica = cita.fk_medico.fk_clinica.nombre if cita.fk_medico and cita.fk_medico.fk_clinica else ""

        citas_canceladas_lista.append({
            'cita': cita,
            'nombre_medico': nombre_medico,
            'especialidad': especialidad,
            'clinica': clinica,
        })

    context = {
        'paciente': paciente,
        'citas': citas,
        'ahora': ahora,
        'citas_futuras': citas_futuras,
        'citas_completadas': citas_completadas_con_valoracion,
        'citas_canceladas': citas_canceladas_lista,
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
            # Consumir mensajes para que no aparezcan en otras páginas
            list(messages.get_messages(request))
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
            # Consumir mensajes para que no aparezcan en otras páginas
            list(messages.get_messages(request))
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
    import requests
    from django.conf import settings

    # API Key de SerpApi (debería estar en settings)
    serpapi_key = getattr(settings, 'SERPAPI_KEY', None)

    # Traer todas las clínicas con sus médicos
    clinicas = Clinica.objects.prefetch_related('medico_set').all()

    # Separar clínicas con y sin coordenadas
    clinicas_con_coordenadas = []
    clinicas_sin_coordenadas = []

    for clinica in clinicas:
        if clinica.latitud and clinica.longitud:
            clinicas_con_coordenadas.append(clinica)
        else:
            clinicas_sin_coordenadas.append(clinica)

    # Filtrar clínicas por departamento si se especifica
    departamento = request.GET.get('departamento', '')
    if departamento:
        clinicas_con_coordenadas_filtradas = []
        for clinica in clinicas_con_coordenadas:
            # Obtener departamento de la dirección de la clínica
            departamento_clinica = obtener_departamento_direccion(clinica.direccion)
            if departamento_clinica.lower() == departamento.lower():
                clinicas_con_coordenadas_filtradas.append(clinica)
        clinicas_con_coordenadas = clinicas_con_coordenadas_filtradas

    # Intentar geocoding para clínicas sin coordenadas si hay API key
    if serpapi_key and clinicas_sin_coordenadas:
        for clinica in clinicas_sin_coordenadas:
            if clinica.direccion:
                try:
                    # Usar SerpApi para geocoding
                    geocode_url = "https://serpapi.com/search.json"
                    geocode_params = {
                        'engine': 'google_maps',
                        'q': clinica.direccion + ', El Salvador',
                        'api_key': serpapi_key,
                        'limit': 1
                    }

                    geocode_response = requests.get(geocode_url, params=geocode_params, timeout=10)
                    if geocode_response.status_code == 200:
                        geocode_data = geocode_response.json()
                        local_results = geocode_data.get('local_results', [])
                        if local_results and local_results[0].get('latitude') and local_results[0].get('longitude'):
                            # Actualizar coordenadas en la base de datos
                            clinica.latitud = local_results[0]['latitude']
                            clinica.longitud = local_results[0]['longitude']
                            clinica.save()
                            # Mover a clínicas con coordenadas
                            clinicas_con_coordenadas.append(clinica)
                            clinicas_sin_coordenadas.remove(clinica)
                except Exception as e:
                    print(f"Error en geocoding para clínica {clinica.nombre}: {e}")
                    continue

    # Parámetros de búsqueda
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    mostrar_cercanas = request.GET.get('cercanas', 'false').lower() == 'true'
    user_lat = request.GET.get('user_lat')
    user_lng = request.GET.get('user_lng')
    departamento = request.GET.get('departamento', '')

    # serpapi_key ya fue definido arriba
    lugares_medicos = []
    if serpapi_key and (query != 'hospitales clínicas médicos El Salvador' or mostrar_cercanas or departamento):
        try:
            # Si se solicita mostrar clínicas cercanas y se tienen coordenadas del usuario
            if mostrar_cercanas and user_lat and user_lng:
                # Usar las coordenadas del usuario como centro
                centro_lat = float(user_lat)
                centro_lng = float(user_lng)

                # Llamada a SerpApi con coordenadas del usuario
                url = "https://serpapi.com/search.json"
                params = {
                    'engine': 'google_maps',
                    'q': 'hospitales clínicas médicos',
                    'll': f'@{centro_lat},{centro_lng},14z',  # Centro en las coordenadas del usuario con zoom
                    'api_key': serpapi_key,
                    'type': 'hospital,clinic,doctor',
                    'limit': 15
                }
            # Si se solicita mostrar clínicas cercanas pero no hay coordenadas del usuario, usar clínicas registradas
            elif mostrar_cercanas and clinicas_con_coordenadas:
                # Usar la primera clínica como centro para buscar cercanas
                centro_lat = clinicas_con_coordenadas[0].latitud
                centro_lng = clinicas_con_coordenadas[0].longitud

                # Llamada a SerpApi con coordenadas específicas
                url = "https://serpapi.com/search.json"
                params = {
                    'engine': 'google_maps',
                    'q': 'hospitales clínicas médicos',
                    'll': f'@{centro_lat},{centro_lng},14z',  # Centro en las coordenadas con zoom
                    'api_key': serpapi_key,
                    'type': 'hospital,clinic,doctor',
                    'limit': 15
                }
            else:
                # Búsqueda normal con filtro de departamento si se especifica
                search_query = query
                search_location = location

                if departamento:
                    search_location = f"{departamento}, El Salvador"

                url = "https://serpapi.com/search.json"
                params = {
                    'engine': 'google_maps',
                    'q': search_query,
                    'location': search_location,
                    'api_key': serpapi_key,
                    'type': 'hospital,clinic,doctor',
                    'limit': 20
                }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                lugares_medicos = data.get('local_results', [])

                # Filtrar solo lugares con coordenadas válidas
                lugares_medicos = [
                    lugar for lugar in lugares_medicos
                    if lugar.get('latitude') and lugar.get('longitude')
                ]
        except Exception as e:
            print(f"Error al consultar SerpApi: {e}")
            lugares_medicos = []

    context = {
        "clinicas_con_coordenadas": clinicas_con_coordenadas,
        "clinicas_sin_coordenadas": clinicas_sin_coordenadas,
        "lugares_medicos": lugares_medicos,
        "query": query,
        "location": location,
        "mostrar_cercanas": mostrar_cercanas,
        "user_lat": user_lat,
        "user_lng": user_lng,
        "departamento": departamento
    }
    return render(request, "paciente/mapa_medicos.html", context)
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
        medicos = medicos.filter(fk_clinica__direccion__icontains=ubicacion_filter)

    # Ordenar por promedio descendente
    medicos = medicos.order_by('-avg_rating')

    # Obtener opciones para filtros
    especialidades = Medico.objects.values_list('especialidad', flat=True).distinct().exclude(especialidad__isnull=True).exclude(especialidad='')
    ubicaciones = DEPARTAMENTOS_EL_SALVADOR

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
            'ubicacion_clinica': medico.fk_clinica.direccion if medico.fk_clinica and medico.fk_clinica.direccion else 'No especificada',
            'departamento': obtener_departamento_direccion(medico.fk_clinica.direccion if medico.fk_clinica else None),
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
    # hoy = date.today()
    # ahora = datetime.now().time()
    # if cita.fecha_consulta > hoy or (cita.fecha_consulta == hoy and cita.hora_inicio > ahora):
    #     messages.error(request, "No puedes calificar una cita que aún no ha ocurrido.")
    #     return redirect('agenda')

    # Verificar si ya tiene valoración
    if ValoracionConsulta.objects.filter(fk_cita=cita).exists():
        messages.warning(request, "Esta cita ya ha sido calificada.")
        return redirect('agenda')

    if request.method == 'POST':
        calificacion = request.POST.get('calificacion')
        resena = request.POST.get('resena', '').strip()

        if not calificacion or not calificacion.isdigit() or not (1 <= int(calificacion) <= 5):
            messages.error(request, "Por favor selecciona una calificación válida (1-5 estrellas).")
            return redirect('calificar_medico', cita_id=cita_id)

        try:
            ValoracionConsulta.objects.create(
                calificacion_consulta=int(calificacion),
                resena=resena if resena else None,
                fk_cita=cita
            )
            messages.success(request, "¡Gracias por tu calificación!")
            # Consumir mensajes para que no aparezcan en otras páginas
            list(messages.get_messages(request))
            return redirect('agenda')
        except Exception as e:
            messages.error(request, f"Error al guardar la calificación: {e}")
            return redirect('calificar_medico', cita_id=cita_id)

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


@login_required
@paciente_required
def ver_diagnostico(request, cita_id):
    usuario = request.user

    if not hasattr(usuario, 'fk_paciente') or usuario.fk_paciente is None:
        raise PermissionDenied("No tienes permisos para ver diagnósticos.")

    paciente = usuario.fk_paciente

    try:
        cita = CitasMedicas.objects.get(id_cita_medicas=cita_id, fk_paciente=paciente)
    except CitasMedicas.DoesNotExist:
        raise PermissionDenied("Cita no encontrada o no tienes permisos.")

    # Obtener la consulta médica si existe
    try:
        consulta = cita.consulta_medica
    except ConsultaMedica.DoesNotExist:
        consulta = None

    # Si no hay consulta o no tiene receta, buscar en RecetaMedica
    if not consulta or not consulta.tiene_receta():
        try:
            from bd.models import RecetaMedica
            receta = RecetaMedica.objects.get(fk_citas_medicas=cita)
            # Crear un objeto temporal con los datos de receta
            if not consulta:
                consulta = type('ConsultaTemp', (), {})()
                consulta.diagnostico = cita.diagnostico
                consulta.tratamiento = cita.notas_medicas
                consulta.observaciones = None
                consulta.documentos_adjuntos = None
                consulta.fecha_creacion = cita.fecha_consulta
                consulta.tiene_receta = lambda: True
            consulta.medicamento = receta.medicamento
            consulta.via_administracion = receta.via_administracion
            consulta.dosis = receta.dosis
            consulta.fecha_inicio_tratamiento = receta.fecha_inicio_tratamiento
            consulta.fecha_fin_tratamiento = receta.fecha_fin_tratamiento
            consulta.archivos_receta = None  # RecetaMedica no tiene archivo
            if not hasattr(consulta, 'tiene_receta'):
                consulta.tiene_receta = lambda: True
        except RecetaMedica.DoesNotExist:
            pass

    # Verificar si ya tiene valoración
    tiene_valoracion = ValoracionConsulta.objects.filter(fk_cita=cita).exists()

    # Obtener gastos adicionales no pagados con tarjeta (para mostrar y pagar)
    gastos_adicionales_pendientes = GastosAdicionales.objects.filter(fk_cita=cita, pagado=False, metodo_pago='tarjeta')
    total_gastos_pendientes = gastos_adicionales_pendientes.aggregate(total=Sum('monto'))['total'] or 0

    # Obtener TODOS los gastos adicionales (para el total general)
    todos_gastos_adicionales = GastosAdicionales.objects.filter(fk_cita=cita)
    total_todos_gastos = todos_gastos_adicionales.aggregate(total=Sum('monto'))['total'] or 0

    # Información del médico
    usuario_medico = Usuario.objects.filter(fk_medico=cita.fk_medico).first()
    nombre_medico = usuario_medico.get_full_name() if usuario_medico else "Nombre no disponible"
    especialidad = cita.fk_medico.especialidad if cita.fk_medico else ""

    context = {
        'cita': cita,
        'consulta': consulta,
        'tiene_valoracion': tiene_valoracion,
        'gastos_adicionales': gastos_adicionales_pendientes,  # Solo pendientes con tarjeta para el modal
        'todos_gastos_adicionales': todos_gastos_adicionales,  # Todos los gastos para mostrar
        'total_gastos_adicionales': total_gastos_pendientes,  # Total de pendientes
        'total_todos_gastos': total_todos_gastos,  # Total de todos los gastos
        'total_a_pagar': (cita.monto_consulta or 0) + total_todos_gastos,  # Consulta + todos los gastos
        'hay_gastos_pendientes': gastos_adicionales_pendientes.exists(),
        'nombre_medico': nombre_medico,
        'especialidad': especialidad,
    }

    return render(request, 'paciente/ver_diagnostico.html', context)


@login_required
@paciente_required
def cancelar_cita(request, cita_id):
    usuario = request.user

    if not hasattr(usuario, 'fk_paciente') or usuario.fk_paciente is None:
        raise PermissionDenied("No tienes permisos para cancelar citas.")

    paciente = usuario.fk_paciente

    try:
        cita = CitasMedicas.objects.get(id_cita_medicas=cita_id, fk_paciente=paciente)
    except CitasMedicas.DoesNotExist:
        raise PermissionDenied("Cita no encontrada o no tienes permisos.")

    # Verificar que la cita esté pendiente o en proceso
    if cita.status_cita_medica not in ['Pendiente', 'En proceso']:
        messages.error(request, "Solo puedes cancelar citas pendientes o en proceso.")
        return redirect('agenda')

    # Cambiar estado a Cancelado
    cita.status_cita_medica = 'Cancelado'
    cita.cancelado_por = 'paciente'
    cita.fecha_cancelacion = timezone.now()
    cita.save()

    messages.success(request, "Cita cancelada correctamente.")
    # Consumir mensajes para que no aparezcan en otras páginas
    list(messages.get_messages(request))
    return redirect('agenda')

@login_required
@paciente_required
def ver_recetas(request):
    usuario = request.user
    paciente = usuario.fk_paciente

    # Obtener todas las citas completadas del paciente
    citas_completadas = CitasMedicas.objects.filter(
        fk_paciente=paciente,
        status_cita_medica='Completada'
    ).select_related('fk_medico')

    recetas = []
    for cita in citas_completadas:
        # Buscar receta en ConsultaMedica o RecetaMedica
        consulta = None
        try:
            consulta = cita.consulta_medica
        except:
            pass

        if consulta and consulta.tiene_receta():
            recetas.append({
                'cita': cita,
                'consulta': consulta,
                'tipo': 'consulta'
            })
        else:
            # Buscar en RecetaMedica
            try:
                from bd.models import RecetaMedica
                receta_db = RecetaMedica.objects.get(fk_citas_medicas=cita)
                # Crear objeto similar
                consulta_temp = type('ConsultaTemp', (), {})()
                consulta_temp.medicamento = receta_db.medicamento
                consulta_temp.via_administracion = receta_db.via_administracion
                consulta_temp.dosis = receta_db.dosis
                consulta_temp.fecha_inicio_tratamiento = receta_db.fecha_inicio_tratamiento
                consulta_temp.fecha_fin_tratamiento = receta_db.fecha_fin_tratamiento
                consulta_temp.archivos_receta = None
                consulta_temp.tiene_receta = lambda: True
                recetas.append({
                    'cita': cita,
                    'consulta': consulta_temp,
                    'tipo': 'receta_db'
                })
            except RecetaMedica.DoesNotExist:
                pass

    # Agregar recetas de seguimientos clínicos
    try:
        seguimientos = SeguimientoClinico.objects.filter(
            fk_paciente=paciente
        ).select_related('fk_cita', 'fk_medico')

        for seguimiento in seguimientos:
            if seguimiento.tiene_receta():
                # Crear objeto similar a consulta
                consulta_temp = type('ConsultaTemp', (), {})()
                consulta_temp.medicamento = seguimiento.medicamento
                consulta_temp.dosis = seguimiento.dosis
                consulta_temp.fecha_inicio_tratamiento = None  # No hay en seguimiento
                consulta_temp.fecha_fin_tratamiento = None
                try:
                    consulta_temp.archivos_receta = seguimiento.archivos_receta
                except:
                    consulta_temp.archivos_receta = None
                consulta_temp.tiene_receta = lambda: True
                recetas.append({
                    'cita': seguimiento.fk_cita,
                    'consulta': consulta_temp,
                    'tipo': 'seguimiento',
                    'seguimiento': seguimiento
                })
    except:
        # Si hay problemas con la tabla de seguimientos, continuar sin ella
        pass

    return render(request, 'paciente/ver_recetas.html', {
        'recetas': recetas
    })

@login_required
@paciente_required
def generar_pdf_receta(request, cita_id):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from django.http import HttpResponse

    usuario = request.user
    paciente = usuario.fk_paciente

    try:
        cita = CitasMedicas.objects.get(id_cita_medicas=cita_id, fk_paciente=paciente)
    except CitasMedicas.DoesNotExist:
        return HttpResponse("Receta no encontrada", status=404)

    # Buscar receta
    consulta = None
    try:
        consulta = cita.consulta_medica
    except:
        pass

    if not consulta or not consulta.tiene_receta():
        try:
            from bd.models import RecetaMedica
            receta_db = RecetaMedica.objects.get(fk_citas_medicas=cita)
            consulta = type('ConsultaTemp', (), {})()
            consulta.medicamento = receta_db.medicamento
            consulta.via_administracion = receta_db.via_administracion
            consulta.dosis = receta_db.dosis
            consulta.fecha_inicio_tratamiento = receta_db.fecha_inicio_tratamiento
            consulta.fecha_fin_tratamiento = receta_db.fecha_fin_tratamiento
        except RecetaMedica.DoesNotExist:
            return HttpResponse("Receta no encontrada", status=404)

    # Generar PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receta_{cita_id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Receta Médica", styles['Title']))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Paciente: {usuario.nombre} {usuario.apellido}", styles['Normal']))
    story.append(Paragraph(f"Fecha de Cita: {cita.fecha_consulta.strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Spacer(1, 12))

    if consulta.medicamento:
        story.append(Paragraph(f"Medicamento: {consulta.medicamento}", styles['Normal']))
    if consulta.via_administracion:
        story.append(Paragraph(f"Vía de Administración: {consulta.via_administracion}", styles['Normal']))
    if consulta.dosis:
        story.append(Paragraph(f"Dosis: {consulta.dosis}", styles['Normal']))
    if consulta.fecha_inicio_tratamiento:
        story.append(Paragraph(f"Fecha Inicio: {consulta.fecha_inicio_tratamiento.strftime('%d/%m/%Y')}", styles['Normal']))
    if consulta.fecha_fin_tratamiento:
        story.append(Paragraph(f"Fecha Fin: {consulta.fecha_fin_tratamiento.strftime('%d/%m/%Y')}", styles['Normal']))

    doc.build(story)
    return response

@login_required
@paciente_required
def config_perfil_paciente(request):
    usuario = request.user
    paciente = getattr(usuario, 'fk_paciente', None)

    # Si no existe perfil paciente, crearlo
    if not paciente:
        from bd.models import Paciente
        paciente = Paciente.objects.create()
        usuario.fk_paciente = paciente
        usuario.save()

    if request.method == 'POST':
        form = PerfilPacienteForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Guardar campos de Usuario
                    usuario.nombre = form.cleaned_data['nombre']
                    usuario.apellido = form.cleaned_data['apellido']
                    usuario.correo = form.cleaned_data['correo']
                    usuario.telefono = form.cleaned_data['telefono']
                    usuario.departamento = form.cleaned_data['departamento']
                    usuario.municipio = form.cleaned_data['municipio']
                    usuario.fecha_nacimiento = form.cleaned_data.get('fecha_nacimiento')
                    usuario.sexo = form.cleaned_data.get('sexo')
                    # Guardar foto de perfil en base64
                    if form.cleaned_data['foto_perfil']:
                        usuario.foto_perfil = form.cleaned_data['foto_perfil']
                    usuario.save()

                messages.success(request, "Perfil paciente actualizado correctamente.")
                # Consumir mensajes para que no aparezcan en otras páginas
                list(messages.get_messages(request))
                return redirect('dashboard_paciente')
            except Exception as e:
                messages.error(request, f"Error al guardar los cambios: {e}")
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        # Inicializar formulario con valores actuales
        initial_data = {
            'nombre': usuario.nombre or '',
            'apellido': usuario.apellido or '',
            'correo': usuario.correo or '',
            'telefono': usuario.telefono or '',
            'departamento': usuario.departamento or '',
            'municipio': usuario.municipio or '',
            'fecha_nacimiento': usuario.fecha_nacimiento,
            'sexo': usuario.sexo or '',
            'foto_perfil': usuario.foto_perfil,
        }
        form = PerfilPacienteForm(initial=initial_data)

    return render(request, 'paciente/config_perfil_paciente.html', {'form': form})

@login_required
@paciente_required
def historial_facturas_paciente(request):
    usuario = request.user
    paciente = usuario.fk_paciente

    if not paciente:
        messages.error(request, "No tienes un perfil de paciente asociado.")
        return redirect('dashboard_paciente')

    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    numero_factura = request.GET.get('numero_factura')

    # Query base - citas con facturas del paciente
    citas_con_facturas = CitasMedicas.objects.filter(
        fk_paciente=paciente,
        fk_factura__isnull=False
    ).select_related(
        'fk_factura',
        'fk_factura__fk_metodopago',
        'fk_medico'
    ).order_by('-fk_factura__fecha_emision')

    # Aplicar filtros de fecha
    if fecha_desde:
        citas_con_facturas = citas_con_facturas.filter(fk_factura__fecha_emision__gte=fecha_desde)
    if fecha_hasta:
        citas_con_facturas = citas_con_facturas.filter(fk_factura__fecha_emision__lte=fecha_hasta)
    if numero_factura:
        citas_con_facturas = citas_con_facturas.filter(
            Q(fk_factura__documento_interno__icontains=numero_factura) |
            Q(fk_factura__numero_factura__icontains=numero_factura)
        )

    # Enriquecer datos
    facturas_enriquecidas = []
    for cita in citas_con_facturas:
        factura = cita.fk_factura
        medico = None
        if cita.fk_medico:
            medico = Usuario.objects.filter(fk_medico=cita.fk_medico).first()

        # Calcular gastos adicionales
        gastos_adicionales = GastosAdicionales.objects.filter(fk_cita=cita)
        total_gastos = sum(gasto.monto for gasto in gastos_adicionales)
        total_factura = factura.monto + total_gastos

        facturas_enriquecidas.append({
            'factura': factura,
            'medico': medico.get_full_name() if medico else "Médico desconocido",
            'fecha_cita': cita.fecha_consulta,
            'metodo_pago': factura.fk_metodopago.get_tipometodopago_display() if factura.fk_metodopago else "No especificado",
            'monto_consulta': factura.monto,
            'gastos_adicionales': gastos_adicionales,
            'total_gastos_adicionales': total_gastos,
            'total_factura': total_factura,
            'status_pago': "Confirmado" if cita.pago_confirmado else "Pendiente",
        })

    context = {
        'facturas': facturas_enriquecidas,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'numero_factura': numero_factura,
        'total_facturas': len(facturas_enriquecidas),
        'total_monto': sum(f['total_factura'] for f in facturas_enriquecidas if f['total_factura']),
    }

    return render(request, 'paciente/historial_facturas.html', context)

@login_required
@paciente_required
def historial_pagos_paciente(request):
    usuario = request.user
    paciente = usuario.fk_paciente

    if not paciente:
        messages.error(request, "No tienes un perfil de paciente asociado.")
        return redirect('dashboard_paciente')

    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    # Obtener todas las citas pagadas del paciente
    citas_pagadas = CitasMedicas.objects.filter(
        fk_paciente=paciente,
        fk_factura__isnull=False
    ).select_related('fk_medico', 'fk_factura').order_by('-fecha_consulta')

    # Aplicar filtros de fecha
    if fecha_desde:
        citas_pagadas = citas_pagadas.filter(fecha_consulta__gte=fecha_desde)
    if fecha_hasta:
        citas_pagadas = citas_pagadas.filter(fecha_consulta__lte=fecha_hasta)

    # Obtener gastos adicionales pagados
    gastos_pagados = GastosAdicionales.objects.filter(
        fk_cita__fk_paciente=paciente,
        pagado=True
    ).select_related('fk_cita__fk_medico').order_by('-fecha_creacion')

    # Aplicar filtros de fecha a gastos
    if fecha_desde:
        gastos_pagados = gastos_pagados.filter(fecha_creacion__date__gte=fecha_desde)
    if fecha_hasta:
        gastos_pagados = gastos_pagados.filter(fecha_creacion__date__lte=fecha_hasta)

    # Preparar datos para el template
    pagos = []

    # Agregar consultas pagadas
    for cita in citas_pagadas:
        usuario_medico = Usuario.objects.filter(fk_medico=cita.fk_medico).first()
        nombre_medico = usuario_medico.get_full_name() if usuario_medico else "Médico desconocido"

        pagos.append({
            'tipo': 'consulta',
            'fecha': cita.fecha_consulta,
            'medico': nombre_medico,
            'descripcion': f"Consulta médica - {cita.des_motivo_consulta_paciente or 'Sin motivo especificado'}",
            'monto': cita.fk_factura.monto,
            'metodo_pago': cita.fk_factura.fk_metodopago.get_tipometodopago_display() if cita.fk_factura.fk_metodopago else "No especificado",
            'estado': 'Completado'
        })

    # Agregar gastos adicionales pagados
    for gasto in gastos_pagados:
        usuario_medico = Usuario.objects.filter(fk_medico=gasto.fk_cita.fk_medico).first()
        nombre_medico = usuario_medico.get_full_name() if usuario_medico else "Médico desconocido"

        pagos.append({
            'tipo': 'gasto_adicional',
            'fecha': gasto.fecha_creacion.date(),
            'medico': nombre_medico,
            'descripcion': gasto.descripcion,
            'monto': gasto.monto,
            'metodo_pago': gasto.get_metodo_pago_display(),
            'estado': 'Completado'
        })

    # Ordenar por fecha descendente
    pagos.sort(key=lambda x: x['fecha'], reverse=True)

    # Calcular totales
    total_consultas = sum(p['monto'] for p in pagos if p['tipo'] == 'consulta')
    total_gastos = sum(p['monto'] for p in pagos if p['tipo'] == 'gasto_adicional')
    total_general = total_consultas + total_gastos

    context = {
        'pagos': pagos,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total_consultas': total_consultas,
        'total_gastos': total_gastos,
        'total_general': total_general,
        'total_pagos': len(pagos),
    }

    return render(request, 'paciente/historial_pagos.html', context)


@login_required
@paciente_required
def pagar_gastos_adicionales(request, cita_id):
    usuario = request.user

    if not hasattr(usuario, 'fk_paciente') or usuario.fk_paciente is None:
        raise PermissionDenied("No tienes permisos para pagar gastos adicionales.")

    paciente = usuario.fk_paciente

    try:
        cita = CitasMedicas.objects.get(id_cita_medicas=cita_id, fk_paciente=paciente)
    except CitasMedicas.DoesNotExist:
        raise PermissionDenied("Cita no encontrada o no tienes permisos.")

    # Obtener gastos adicionales no pagados con tarjeta
    gastos_adicionales = GastosAdicionales.objects.filter(fk_cita=cita, pagado=False, metodo_pago='tarjeta')

    if not gastos_adicionales.exists():
        messages.warning(request, "No hay gastos adicionales pendientes de pago con tarjeta.")
        return redirect('ver_diagnostico', cita_id=cita_id)

    if request.method == 'POST':
        # Procesar datos de la tarjeta
        numero_tarjeta = request.POST.get('numero_tarjeta')
        fecha_expiracion = request.POST.get('fecha_expiracion')
        cvv = request.POST.get('cvv')
        nombre_titular = request.POST.get('nombre_titular')
        tipo_tarjeta = request.POST.get('tipo_tarjeta')

        # Validar campos
        if not all([numero_tarjeta, fecha_expiracion, cvv, nombre_titular, tipo_tarjeta]):
            messages.error(request, "Por favor completa todos los campos.")
            return redirect('ver_diagnostico', cita_id=cita_id)

        # Validar formato de número de tarjeta
        if not numero_tarjeta.isdigit() or len(numero_tarjeta) != 16:
            messages.error(request, "El número de tarjeta debe tener 16 dígitos.")
            return redirect('ver_diagnostico', cita_id=cita_id)

        # Validar formato de fecha de expiración
        import re
        if not re.match(r'^\d{2}/\d{2}$', fecha_expiracion):
            messages.error(request, "Formato de fecha de expiración inválido (MM/YY).")
            return redirect('ver_diagnostico', cita_id=cita_id)

        try:
            with transaction.atomic():
                # Crear método de pago
                metodo_pago_obj = MetodosPago.objects.create(
                    tipometodopago='tarjeta',
                    numero_tarjeta=numero_tarjeta,
                    fecha_expiracion=fecha_expiracion,
                    cvv=cvv,
                    nombre_titular=nombre_titular,
                    tipo_tarjeta=tipo_tarjeta
                )

                # Marcar gastos adicionales como pagados
                gastos_adicionales.update(pagado=True)

                # Crear factura para los gastos adicionales
                total_gastos = gastos_adicionales.aggregate(total=Sum('monto'))['total'] or 0
                factura = Factura.objects.create(
                    fecha_emision=timezone.now().date(),
                    monto=total_gastos,
                    fk_metodopago=metodo_pago_obj
                )

                messages.success(request, f"¡Pago procesado correctamente! Se han pagado ${total_gastos} por gastos adicionales.")
                # Consumir mensajes para que no aparezcan en otras páginas
                list(messages.get_messages(request))
                return redirect('ver_diagnostico', cita_id=cita_id)

        except Exception as e:
            messages.error(request, f"Error al procesar el pago: {e}")
            return redirect('ver_diagnostico', cita_id=cita_id)

    # Si no es POST, redirigir a la vista de diagnóstico
    return redirect('ver_diagnostico', cita_id=cita_id)


@login_required
@paciente_required
def generar_pdf_factura_paciente(request, factura_id):
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from io import BytesIO
        from django.http import HttpResponse
        import os
        from num2words import num2words  # Para convertir números a letras
    
        # Obtener la factura
        factura = get_object_or_404(Factura, id_factura=factura_id)
        cita = CitasMedicas.objects.filter(fk_factura=factura).first()
    
        if not cita or cita.fk_paciente != request.user.fk_paciente:
            raise PermissionDenied("No tienes permisos para ver esta factura.")
    
        # Obtener datos del paciente
        usuario_paciente = Usuario.objects.filter(fk_paciente=cita.fk_paciente).first()
        nombre_paciente = usuario_paciente.get_full_name() if usuario_paciente else "Paciente desconocido"
    
        # Obtener gastos adicionales
        gastos_adicionales = GastosAdicionales.objects.filter(fk_cita=cita, pagado=True)
    
        # Obtener datos de la clínica
        clinica = cita.fk_medico.fk_clinica
        medico = cita.fk_medico
        usuario_medico = Usuario.objects.filter(fk_medico=medico).first()
    
        # Crear el PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
        # Estilos
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='Small', fontSize=8))
    
        # Contenido del PDF
        story = []
    
        # Logo más pequeño y más arriba
        try:
            logo_path = os.path.join('inicio', 'static', 'img', 'logo.png')
            if os.path.exists(logo_path):
                logo = Image(logo_path, 1*inch, 0.5*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
            else:
                # Intentar con static directo
                logo_path = os.path.join('static', 'img', 'logo.png')
                if os.path.exists(logo_path):
                    logo = Image(logo_path, 1*inch, 0.5*inch)
                    logo.hAlign = 'CENTER'
                    story.append(logo)
        except:
            pass
    
        story.append(Spacer(1, 3))
    
        # Información del documento tributario (primero)
        doc_info = [
            ["DOCUMENTO TRIBUTARIO ELECTRÓNICO"],
            ["FACTURA"],
            [f"Código de generación: {factura.codigo_generacion or 'N/A'}"],
            [f"Sello de recepción: {factura.sello_recepcion or 'N/A'}"],
            [f"Número de control: {factura.numero_control or 'N/A'}"],
            ["Modelo de facturación: Previo Versión de JSON: 1"],
            ["Tipo de transmisión: Normal"],
            [f"Fecha de emisión: {factura.fecha_emision.strftime('%d/%m/%Y') if factura.fecha_emision else 'N/A'}"],
            [f"Hora de emisión: {timezone.now().strftime('%I:%M:%S %p')}"],
            [f"Documento interno: {factura.documento_interno or 'N/A'}"],
        ]
    
        # Información de la clínica (después)
        if clinica:
            clinica_info = [
                [clinica.nombre or "CLÍNICA MÉDICA"],
                ["Servicios Médicos y Consultas"],
                ["Categoría: Centro Médico"],
                [clinica.direccion or "Dirección no especificada"],
                [f"Teléfono: {clinica.telefono_clinica or 'N/A'}"],
                [f"Correo: {clinica.correo_electronico_clinica or 'N/A'}"],
                ["Tipo Establecimiento: Clínica"],
                [f"NIT: {medico.dui or 'N/A'}"],
                [f"NRC: {medico.no_jvpm or 'N/A'}"],
            ]
        else:
            clinica_info = [
                ["CLÍNICA MÉDICA"],
                ["Servicios Médicos y Consultas"],
                ["Categoría: Centro Médico"],
                ["Dirección no especificada"],
                ["Teléfono: N/A"],
                ["Correo: N/A"],
                ["Tipo Establecimiento: Clínica"],
                ["NIT: N/A"],
                ["NRC: 12345"],
            ]
    
        # Combinar ambas secciones en una sola tabla vertical
        header_info = doc_info + clinica_info
    
        header_table = Table(header_info, colWidths=[15*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),   # Todo alineado a la izquierda
            ('FONTSIZE', (0, 0), (-1, -1), 6),     # Fuente más pequeña
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),  # Títulos en negrita
            ('FONTNAME', (0, 2), (-1, 9), 'Helvetica'),       # Detalles del documento normal
            ('FONTNAME', (0, 10), (-1, 10), 'Helvetica-Bold'), # Título de clínica en negrita
            ('FONTNAME', (0, 11), (-1, -1), 'Helvetica'),      # Detalles de clínica normal
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 6))
    
        # Información del paciente (cliente)
        paciente_info = [
            [f"Nombre: {nombre_paciente}", f"DUI: {cita.fk_paciente.dui if cita.fk_paciente and cita.fk_paciente.dui else 'N/A'}"],
            [f"Correo Electrónico: {usuario_paciente.correo if usuario_paciente else 'N/A'}", f"Teléfono: {usuario_paciente.telefono if usuario_paciente else 'N/A'}"],
            [f"Dirección: {usuario_paciente.departamento or ''}, {usuario_paciente.municipio or ''}, El Salvador", ""],
            ["Condición de la operación: Contado", f"Moneda: USD"],
            [f"Municipio: {usuario_paciente.municipio or 'N/A'}", f"Departamento: {usuario_paciente.departamento or 'N/A'}"],
        ]
    
        paciente_table = Table(paciente_info, colWidths=[8*cm, 5*cm])
        paciente_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        story.append(paciente_table)
        story.append(Spacer(1, 6))
    
        # VENTA A CUENTA DE TERCEROS (adaptado para médico)
        venta_terceros = [
            ["VENTA DE SERVICIOS MÉDICOS", ""],
            [f"NIT: {medico.dui or 'N/A'}", f"Nombre: {usuario_medico.get_full_name() if usuario_medico else str(medico)}"],
        ]
    
        venta_table = Table(venta_terceros, colWidths=[8*cm, 5*cm])
        venta_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        story.append(venta_table)
        story.append(Spacer(1, 6))
    
        # CUERPO DEL DOCUMENTO
        cuerpo_title = Paragraph("<b>CUERPO DEL DOCUMENTO</b>", styles['Left'])
        story.append(cuerpo_title)
        story.append(Spacer(1, 6))
    
        # Tabla de ítems
        header = ['No.', 'Código', 'Descripción', 'Precio Unitario', 'Ventas gravadas']
        data = [header]
    
        # Consulta médica
        total_gastos = sum(gasto.monto for gasto in gastos_adicionales)
        total_factura = factura.monto + total_gastos
    
        data.append([
            '1', 'CONS001', 'Consulta médica especializada',
            f"${factura.monto:.2f}", f"${factura.monto:.2f}"
        ])
    
        # Gastos adicionales
        for i, gasto in enumerate(gastos_adicionales, 2):
            data.append([
                str(i), f'GAST{i-1:03d}', gasto.descripcion,
                f"${gasto.monto:.2f}", f"${gasto.monto:.2f}"
            ])
    
        cuerpo_table = Table(data, colWidths=[0.5*cm, 2*cm, 5*cm, 2.5*cm, 2.5*cm])
        cuerpo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (6, 1), (11, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(cuerpo_table)
        story.append(Spacer(1, 6))
    
        # Sumas más compactas
        sumas_info = [
            ["Subtotal Consulta:", f"${factura.monto:.2f}"],
            ["Gastos Adicionales:", f"${total_gastos:.2f}"],
            ["TOTAL:", f"${total_factura:.2f}"],
        ]
    
        sumas_table = Table(sumas_info, colWidths=[4*cm, 3*cm])
        sumas_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (-1, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(sumas_table)
        story.append(Spacer(1, 6))
    
        # Total simple
        total_simple = [
            ["TOTAL A PAGAR:", f"${total_factura:.2f}"],
        ]
    
        total_simple_table = Table(total_simple, colWidths=[4*cm, 9*cm])
        total_simple_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgreen),
        ]))
        story.append(total_simple_table)
        story.append(Spacer(1, 6))
    
        # Valor en letras (al final)
        try:
            valor_letras = num2words(total_factura, lang='es').upper() + " DOLARES"
        except:
            valor_letras = "N/A"
    
        valor_info = [
            [f"Valor en Letras: {valor_letras}"],
        ]
    
        valor_table = Table(valor_info, colWidths=[13*cm])
        valor_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(valor_table)
    
        # Generar PDF
        doc.build(story)
    
        # Preparar respuesta
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{factura.documento_interno or factura_id}.pdf"'
    
        return response

