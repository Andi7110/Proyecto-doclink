from django.urls import path
from . import views
from .views import views_home


urlpatterns = [
    path('home/', views.views_home, name='home'),  # Página principal
    path('dashboard_doctor/', views.vistaMedico_view, name='dashboard_doctor'),  # Dashboard con pacientes
    path('consulta/realizar/<int:paciente_id>/', views.realizar_consulta, name='realizar_consulta'),  # Crear consulta para paciente
]