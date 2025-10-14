# Proyecto-doclink

Sistema de gestión médica DocLink, una aplicación web desarrollada con Django que permite la gestión de citas médicas, perfiles de médicos y pacientes.

## Requisitos Previos

- Python 3.11 o superior
- PostgreSQL (para producción) o SQLite (para desarrollo local)
- Docker (opcional, para contenedorización)
- Git
- SerpApi Key (para funcionalidades de mapas y geocoding)
- SendGrid API Key (para envío de correos electrónicos)

## Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Andi7110/Proyecto-doclink.git
cd Proyecto-doclink
```

### 2. Configuración del Entorno Virtual

Crea y activa un entorno virtual:

```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependencias

Instala las dependencias desde requirements.txt:

```bash
pip install -r requirements.txt
```

### 4. Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3  # Para desarrollo local con SQLite
# O para PostgreSQL: DATABASE_URL=postgresql://usuario:password@localhost:5432/doclink
MEDIA_ROOT=C:\Users\[TuUsuario]\OneDrive\consultas-documentacion  # Ruta personalizada para archivos (opcional)

# APIs Externas (requeridas para funcionalidades avanzadas)
SERPAPI_KEY=tu-serpapi-key-aqui  # Para mapas y geocoding
SENDGRID_API_KEY=tu-sendgrid-api-key-aqui  # Para envío de correos
```

### 5. Aplicar Migraciones de Base de Datos

```bash
python manage.py migrate
```

### 6. Crear Roles Iniciales (Opcional)

Los roles se crean automáticamente al iniciar el servidor, pero puedes verificarlos manualmente:

```bash
python manage.py shell -c "
from bd.models import Rol
roles = [('medico', 'Rol para médicos'), ('paciente', 'Rol para pacientes'), ('admin', 'Rol para administradores')]
for nombre, desc in roles:
    Rol.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
"
```

### 7. Crear Superusuario (Opcional)

```bash
python manage.py createsuperuser
```

### 8. Recopilar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 9. Ejecutar el Servidor de Desarrollo

```bash
python manage.py runserver
```

Accede a la aplicación en `http://127.0.0.1:8000`

### 10. Configuración Adicional (Opcional)

#### Configurar SerpApi para Mapas
1. Regístrate en [SerpApi](https://serpapi.com/)
2. Obtén tu API key
3. Agrega `SERPAPI_KEY=tu-api-key` al archivo `.env`

#### Configurar SendGrid para Emails
1. Registra una cuenta en [SendGrid](https://sendgrid.com/)
2. Crea una API key
3. Agrega `SENDGRID_API_KEY=tu-api-key` al archivo `.env`

#### Configurar OneDrive para Almacenamiento
1. Asegúrate de tener OneDrive instalado y configurado
2. La ruta por defecto es `C:\Users\[Usuario]\OneDrive\consultas-documentacion\`
3. Personaliza con `MEDIA_ROOT=ruta-personalizada` en `.env`

#### Autenticación de Dos Factores (2FA)
- Los usuarios pueden activar 2FA desde su perfil
- Compatible con aplicaciones autenticadoras como Google Authenticator
- Opcional pero recomendado para mayor seguridad

## Uso con Docker

### Construir la Imagen

```bash
docker build -t doclink .
```

### Ejecutar el Contenedor

```bash
docker run -p 8000:8000 --env-file .env doclink
```

Asegúrate de configurar las variables de entorno en el archivo `.env` y montar volúmenes si es necesario para la base de datos.

## APIs y Servicios Externos

### SerpApi
- **Uso**: Geocoding y búsqueda de lugares médicos en mapas
- **Configuración**: `SERPAPI_KEY` en archivo `.env`
- **Funcionalidades**: Mapa interactivo de médicos, búsqueda de clínicas cercanas
- **Documentación**: https://serpapi.com/

### SendGrid
- **Uso**: Envío de correos electrónicos de verificación y notificaciones
- **Configuración**: `SENDGRID_API_KEY` en archivo `.env`
- **Funcionalidades**: Emails de verificación de cuenta, emails de bienvenida
- **Documentación**: https://sendgrid.com/docs/

### OneDrive
- **Uso**: Almacenamiento de documentos médicos
- **Configuración**: `MEDIA_ROOT` en archivo `.env`
- **Funcionalidades**: Almacenamiento automático de PDFs e imágenes médicas
- **Nota**: Sincronización automática con la nube

## Estructura del Proyecto

- `Donlink/`: Configuración principal de Django
- `inicio/`: App de autenticación y registro (emails, formularios, vistas de login/registro)
- `medico/`: App para médicos (dashboard, agenda, consultas, facturas, seguimientos)
- `paciente/`: App para pacientes (dashboard, agenda, citas, mapas, facturas)
- `bd/`: App de base de datos y modelos (todos los modelos de datos)
- `static/`: Archivos estáticos (CSS, JS, imágenes)
- `staticfiles/`: Archivos estáticos recopilados
- `templates/`: Plantillas HTML organizadas por app
- `migrations/`: Migraciones de base de datos
- `fixtures/`: Datos iniciales para pruebas

## Funcionalidades

### Ranking de Médicos
Los pacientes pueden visualizar un ranking de médicos basado en las calificaciones promedio de las consultas. Incluye filtros por especialidad y ubicación (municipio de la clínica). Accesible desde el dashboard del paciente en la sección "Ranking de Médicos".

### Sistema de Calificaciones y Reseñas
- Los pacientes pueden calificar a los médicos después de completar una consulta.
- Las calificaciones van de 1 a 5 estrellas.
- Se pueden incluir reseñas opcionales para proporcionar feedback detallado.
- Las calificaciones se muestran en el ranking de médicos y ayudan a otros pacientes en su elección.
- Accesible desde la agenda del paciente, en las citas anteriores completadas.

### Sistema de Métodos de Pago
- Los pacientes pueden seleccionar entre dos métodos de pago al agendar citas: efectivo o tarjeta.
- Para pagos con tarjeta, se requiere información segura: número de tarjeta (16 dígitos), fecha de expiración (MM/YY), CVV (3-4 dígitos), nombre del titular y tipo de tarjeta (débito/crédito).
- Los datos de pago se almacenan de forma segura en la base de datos.
- Para pagos en efectivo, se informa al paciente que debe realizar el pago al momento de la cita.
- El método de pago se registra en la factura correspondiente a cada cita médica.

### Historial de Facturas
- **Para Médicos**: Pueden visualizar un historial completo de todas las facturas emitidas por sus consultas.
- **Para Pacientes**: Pueden ver el historial de sus propias facturas con información detallada de pagos realizados.
- Cada factura muestra: número de factura, fecha de emisión, nombre del médico/paciente, fecha de la cita, método de pago, estado del pago y monto.
- Incluye filtros por rango de fechas para facilitar la búsqueda.
- Muestra estadísticas totales: número de facturas y monto total acumulado.
- Mejora la auditoría y transparencia en el sistema de pagos.
- Accesible desde los dashboards respectivos en la sección "Historial de Facturas" / "Mis Facturas".

### Historial de Pagos
- **Para Médicos**: Vista completa de todos los pagos recibidos, incluyendo consultas y gastos adicionales.
- **Para Pacientes**: Historial detallado de todos los pagos realizados por consultas y gastos adicionales.
- Incluye filtros por rango de fechas.
- Muestra estadísticas totales por tipo de pago y montos acumulados.
- Accesible desde los dashboards respectivos en la sección "Historial de Pagos".

### Sistema de Seguimiento Clínico
- Los médicos pueden crear seguimientos clínicos para pacientes después de consultas.
- Permite programar nuevas consultas de seguimiento automáticamente.
- Incluye campos para diagnóstico final, observaciones, tratamientos y recetas médicas.
- Los pacientes pueden ver sus seguimientos desde su dashboard.
- Soporta consultas de seguimiento con comparación de síntomas y evolución.

### Gastos Adicionales
- Los médicos pueden agregar gastos adicionales a las citas médicas (exámenes, medicamentos, procedimientos).
- Soporta diferentes métodos de pago para cada gasto adicional.
- Los pacientes pueden pagar gastos adicionales pendientes con tarjeta.
- Se incluyen en las facturas generadas automáticamente.
- Gestión completa desde el dashboard del médico.

### Sistema de Pólizas de Seguro
- Los pacientes pueden registrar múltiples pólizas de seguro médico.
- Incluye información de compañía aseguradora, número de póliza, fecha de vigencia y tipo de cobertura.
- Integración con el perfil del paciente para facilitar el acceso a información médica.

### Contactos de Emergencia
- Los pacientes pueden registrar contactos de emergencia con información completa.
- Incluye nombre, parentesco, teléfono y dirección.
- Validación de formato de número telefónico internacional.

### Mapa Interactivo de Médicos
- Integración con SerpApi para mostrar clínicas y médicos en mapas interactivos.
- Búsqueda de médicos cercanos usando coordenadas GPS del usuario.
- Filtros por departamento y especialidad.
- Vista de clínicas registradas con coordenadas geográficas.

### Generación de PDFs de Facturas
- Generación automática de facturas en formato PDF usando ReportLab.
- Cumple con estándares de facturación electrónica salvadoreña.
- Incluye códigos de generación, sellos de recepción y números de control.
- Disponible tanto para médicos como pacientes.

### Sistema de Recetas Médicas
- Los médicos pueden prescribir medicamentos con dosis, frecuencia y duración.
- Soporte para archivos adjuntos (imágenes, PDFs) en base64.
- Las recetas se almacenan en las consultas médicas y seguimientos.
- Los pacientes pueden descargar sus recetas desde su dashboard.

### Autenticación de Dos Factores (2FA)
- Sistema opcional de autenticación de dos factores para mayor seguridad.
- Generación de códigos secretos para aplicaciones autenticadoras.
- Configurable por usuario desde su perfil.

### Fotos de Perfil
- Los usuarios pueden subir fotos de perfil que se almacenan en base64.
- Disponible para médicos y pacientes.
- Se muestran en dashboards y perfiles.

### Precios de Consulta Configurables
- Los médicos pueden configurar precios personalizados para sus consultas.
- Los precios se muestran al paciente durante el agendamiento de citas.
- Integración con el sistema de facturación.

### Almacenamiento de Documentos
- Los documentos médicos (PDFs, imágenes) se almacenan automáticamente en OneDrive.
- Ruta por defecto: `C:\Users\[Usuario]\OneDrive\consultas-documentacion\`
- Se puede personalizar la ruta mediante la variable de entorno `MEDIA_ROOT` en el archivo `.env`.
- Los archivos se sincronizan automáticamente con la nube de OneDrive.
- **Nota**: Ya no se utiliza almacenamiento local en el proyecto.
