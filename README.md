# 🏥 DocLink - Sistema de Gestión Médica

[![Django](https://img.shields.io/badge/Django-5.2.1-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 🚀 **Sistema integral de gestión médica** desarrollado con Django que permite la administración completa de citas médicas, perfiles de médicos y pacientes, con integración de mapas, pagos y notificaciones por email.

## ✨ Características Principales

- 👨‍⚕️ **Gestión de Médicos**: Perfiles completos, agendas, especialidades y precios configurables
- 🏥 **Gestión de Pacientes**: Historial médico, citas, pagos y seguimientos
- 📅 **Sistema de Citas**: Agendamiento en línea con confirmación automática
- 💳 **Pagos Integrados**: Soporte para efectivo y tarjetas de crédito/débito
- 📧 **Notificaciones**: Emails automáticos de confirmación y recordatorios
- 🗺️ **Mapas Interactivos**: Localización de clínicas y médicos cercanos
- 📊 **Facturación**: Generación automática de PDFs con códigos fiscales
- 🔐 **Seguridad**: Autenticación 2FA opcional y encriptación de datos
- 📱 **Responsive**: Interfaz moderna y adaptativa para todos los dispositivos

## 📋 Requisitos Previos

| Requisito | Versión | Uso |
|-----------|---------|-----|
| 🐍 **Python** | 3.11+ | Lenguaje de programación principal |
| 🐘 **PostgreSQL** | 15+ | Base de datos de producción |
| 🐳 **Docker** | Latest | Contenedorización (opcional) |
| 📝 **Git** | Latest | Control de versiones |
| 🗺️ **SerpApi Key** | - | Mapas y geocoding |
| 📧 **Gmail/SMTP** | - | Envío de correos electrónicos |

## 🚀 Instalación Rápida

### 🐑 Clonación y Configuración Inicial

```bash
# 1. Clonar repositorio
git clone https://github.com/Andi7110/Proyecto-doclink.git
cd Proyecto-doclink

# 2. Configurar entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env  # Copiar template
# Editar .env con tus configuraciones

# 5. Ejecutar migraciones
python manage.py migrate

# 6. Crear superusuario (opcional)
python manage.py createsuperuser

# 7. Ejecutar servidor
python manage.py runserver
```

🌐 **Accede a la aplicación**: `http://127.0.0.1:8000`

### ⚙️ Variables de Entorno (.env)

```env
# Configuración Django
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=False  # False para producción
ALLOWED_HOSTS=doclink-djangoapp.softwar.me,127.0.0.1,localhost
PORT=8000

# Base de datos
DATABASE_URL=postgresql://postgres:doclink2025@doclink-database-qqcj42:5432/doclinkdb

# Seguridad
CSRF_TRUSTED_ORIGINS=https://doclink-djangoapp.softwar.me
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email (SMTP - Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=soportedoclink@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
EMAIL_TIMEOUT=30

# APIs Externas
SERPAPI_KEY=tu-serpapi-key-aqui
BASE_URL=https://doclink-djangoapp.softwar.me
```

### 🔧 Configuración de APIs Externas

#### 📧 **Configuración de Email (Gmail SMTP)**
1. ✅ **Ya configurado** - Usa Gmail SMTP (gratuito)
2. 🔐 Genera un "App Password" en tu cuenta Gmail
3. 📝 Agrega las credenciales al `.env`

#### 🗺️ **Configuración de SerpApi (Mapas)**
1. 🌐 Regístrate en [SerpApi](https://serpapi.com/)
2. 🔑 Obtén tu API key gratuita
3. 📝 Agrega `SERPAPI_KEY=tu-api-key` al `.env`

#### 🔐 **Autenticación 2FA**
- ✅ **Implementado** - Los usuarios pueden activar 2FA opcional
- 📱 Compatible con Google Authenticator y similares

## 🐳 Despliegue con Docker

### 🚀 Despliegue Rápido

```bash
# Construir imagen
docker build -t doclink .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file .env doclink

# O usando Docker Compose (recomendado)
docker-compose up -d
```

### 📋 Dockerfile Optimizado

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🔗 APIs y Servicios Integrados

| Servicio | Estado | Uso | Configuración |
|----------|--------|-----|---------------|
| 📧 **Gmail SMTP** | ✅ **Activo** | Emails de registro y notificaciones | `EMAIL_*` variables |
| 🗺️ **SerpApi** | ✅ **Activo** | Mapas y geocoding de clínicas | `SERPAPI_KEY` |

## 📁 Estructura del Proyecto

```
📦 Proyecto-doclink/
├── 🏠 Donlink/              # ⚙️ Configuración principal de Django
├── 🔐 inicio/               # 👤 Autenticación y registro con emails
├── 👨‍⚕️ medico/              # 🏥 Dashboard médico, consultas, facturas
├── 🏥 paciente/             # 📅 Dashboard paciente, citas, mapas
├── 🗄️ bd/                   # 💾 Modelos de datos y base de datos
├── 🎨 static/               # 🎭 Archivos estáticos (CSS, JS, imágenes)
├── 📄 templates/            # 🏗️ Plantillas HTML por aplicación
├── 🔄 migrations/           # 📊 Migraciones de base de datos
├── 🧪 fixtures/             # 📋 Datos de prueba iniciales
├── 📋 requirements.txt      # 📦 Dependencias Python
├── 🐳 Dockerfile           # 🐳 Configuración de contenedor
├── ⚙️ .env                 # 🔐 Variables de entorno (local)
└── 📖 README.md            # 📚 Esta documentación
```

## 🎯 Funcionalidades Principales

### 👨‍⚕️ **Para Médicos**
- 📊 **Dashboard Personalizado** con estadísticas y agenda
- 📅 **Gestión de Citas** con calendario interactivo
- 💰 **Facturación Automática** con PDFs fiscales
- 📋 **Recetas Médicas** con dosis y tratamientos
- 🔄 **Seguimientos Clínicos** programables
- 💵 **Gastos Adicionales** por consulta
- ⭐ **Sistema de Calificaciones** de pacientes

### 🏥 **Para Pacientes**
- 📱 **Dashboard Intuitivo** con historial completo
- 🗓️ **Agendamiento en Línea** 24/7
- 💳 **Pagos Seguros** (efectivo/tarjeta)
- 🗺️ **Mapas Interactivos** de médicos cercanos
- 📄 **Historial de Facturas** y pagos
- ⭐ **Ranking de Médicos** por calificaciones
- 📞 **Contactos de Emergencia** configurables

### 🔧 **Características Técnicas**
- 📧 **Emails Automáticos** de confirmación y bienvenida
- 🔐 **Autenticación 2FA** opcional
- 📸 **Fotos de Perfil** en base64
- 💾 **Base de Datos PostgreSQL** para producción
- 🐳 **Docker Ready** para despliegue fácil
- 📱 **Responsive Design** para móviles y desktop

### 📊 **Sistema de Pagos y Facturación**
- 💳 **Múltiples Métodos**: Efectivo y tarjetas
- 📄 **PDFs Automáticos** con códigos fiscales
- 📈 **Historial Completo** con filtros por fecha
- 💰 **Precios Configurables** por médico
- 🧾 **Gastos Adicionales** por consulta

### 🗺️ **Integraciones Externas**
- 🗺️ **SerpApi**: Mapas y geocoding de clínicas
- 📧 **Gmail SMTP**: Emails gratuitos y confiables
- 🔒 **Seguridad**: CSRF, sesiones seguras, HTTPS

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Para contribuir:

1. 🍴 **Fork** el proyecto
2. 🌿 **Crea** una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. 💾 **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. 📤 **Push** a la rama (`git push origin feature/AmazingFeature`)
5. 🔄 **Abre** un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Soporte

¿Necesitas ayuda? Contacta al equipo de desarrollo o abre un issue en GitHub.

---

<div align="center">

**Desarrollado con ❤️ para la comunidad médica de El Salvador**

⭐ **Si te gusta el proyecto, ¡dale una estrella!**

[📧 Email](mailto:soportedoclink@gmail.com) • [🐛 Reportar Bug](https://github.com/Andi7110/Proyecto-doclink/issues) • [💡 Solicitar Feature](https://github.com/Andi7110/Proyecto-doclink/issues)

</div>
