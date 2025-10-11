from django.urls import path
from django.contrib.auth import views as auth_views
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
from .views import vistaMedico_view
from .views import vistaPacienteview
from .views import two_factor_setup_view
from .views import two_factor_verify_view
from .views import verify_email
from .views import cambiar_password_view
from .views import reset_password_view
from medico import views

urlpatterns = [
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
    path('reset_password/', reset_password_view, name='reset_password'),
    path('cambiar_password/', cambiar_password_view, name='cambiar_password'),
    path('autenticacion/', autenticacion_view, name='autenticacion'),
    path('dashboard_doctor/', vistaMedico_view, name='dashboard_doctor'),
    path('paciente/dashboard_paciente/', vistaPacienteview, name='vista_paciente'),
    # 2FA URLs
    path('two-factor/setup/', two_factor_setup_view, name='two_factor_setup'),
    path('two-factor/verify/', two_factor_verify_view, name='two_factor_verify'),
    # Email verification
    path('verificar-email/<str:token>/', verify_email, name='verify_email'),
    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='inicio/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='inicio/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='inicio/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='inicio/password_reset_complete.html'), name='password_reset_complete'),
]
