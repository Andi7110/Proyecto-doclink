from django.urls import path
from . import views
from .views import views_home
from .views import receta_medica
from .views import ubicacion_doctor
from .views import clinica_doctor
from .views import config_clinica
from .views import config_horario
from .views import config_perfildoc



urlpatterns = [
    path('home/', views_home, name='home'),
    path('dashboard_doctor/', views.dashboard_doctor, name='dashboard_doctor'),
    path('receta_medica/', views.receta_medica, name='receta_medica'),
    path('ubicacion_doctor/', views.ubicacion_doctor, name='ubicacion_doctor'),
    path('clinica_doctor/', views.clinica_doctor, name='clinica_doctor'),
    path('config_clinica/', views.config_clinica, name='config_clinica'),
    path('config_horario/', views.config_horario, name='config_horario'),
    path('config_perfildoc/', views.config_perfildoc, name='config_perfildoc'),
]

