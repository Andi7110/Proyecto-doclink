from django.urls import path
from . import views
from .views import views_home



urlpatterns = [
    path('home/', views_home, name='home'),
    path('dashboard_paciente/', views.dashboard_paciente, name='dashboard_paciente'),
    path('agendar_cita/', views.agendar_cita, name='agendar_cita'),
    path('agenda/', views.ver_agenda, name='agenda'),
    
]