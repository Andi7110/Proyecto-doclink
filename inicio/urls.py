from django.urls import path
from .views import login_view
from .views import inicio_view
from .views import seleccion_view
from .views import registroDoctor_view
from .views import registroDoctor2_view
from .views import registroDoctor3_view
from .views import registroDoctor4_view
from .views import registroPaciente1_view
from .views import registroPaciente2_view
from .views import registroPaciente3_view
from .views import registroPaciente4_view
from .views import contraOlvidada_view
from .views import autenticacion_view
from .views import custom_logout
from django.contrib import admin
from .views import vistaMedico_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio_view, name='inicio'),
    path('login/', login_view, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('seleccion_registro/', seleccion_view, name='seleccion'),
    path('registro_doctor/', registroDoctor_view, name='registro_doctor'),
    path('registro_doctor2/', registroDoctor2_view, name='registro_doctor2'),
    path('registro_doctor3/', registroDoctor3_view, name='registro_doctor3'),
    path('registro_doctor4/', registroDoctor4_view, name='registro_doctor4'),
    path('registro_paciente1/', registroPaciente1_view, name='registro_paciente1'),
    path('registro_paciente2/', registroPaciente2_view, name='registro_paciente2'),
    path('registro_paciente3/', registroPaciente3_view, name='registro_paciente3'),
    path('registro_paciente4/', registroPaciente4_view, name='registro_paciente4'),
    path('contra_olvidada/', contraOlvidada_view, name='contra_olvidada'),
    path('autenticacion/', autenticacion_view, name='autenticacion'),
    path('medico/dashboard_doctor/', vistaMedico_view, name='vista_medico'),
]
