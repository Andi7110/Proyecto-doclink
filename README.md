# Proyecto-doclink

Sistema de gestión médica DocLink, una aplicación web desarrollada con Django que permite la gestión de citas médicas, perfiles de médicos y pacientes.

## Requisitos Previos

- Python 3.11 o superior
- PostgreSQL (para producción) o SQLite (para desarrollo local)
- Docker (opcional, para contenedorización)
- Git

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

## Estructura del Proyecto

- `Donlink/`: Configuración principal de Django
- `inicio/`: App de autenticación y registro
- `medico/`: App para médicos
- `paciente/`: App para pacientes
- `bd/`: App de base de datos y modelos
- `static/`: Archivos estáticos
- `templates/`: Plantillas HTML

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

### Almacenamiento de Documentos
- Los documentos médicos (PDFs, imágenes) se almacenan automáticamente en OneDrive.
- Ruta por defecto: `C:\Users\[Usuario]\OneDrive\consultas-documentacion\`
- Se puede personalizar la ruta mediante la variable de entorno `MEDIA_ROOT` en el archivo `.env`.
- Los archivos se sincronizan automáticamente con la nube de OneDrive.
- **Nota**: Ya no se utiliza almacenamiento local en el proyecto.
