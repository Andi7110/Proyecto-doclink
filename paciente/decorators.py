from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps

def paciente_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        usuario = request.user
        es_paciente = hasattr(usuario, 'fk_paciente') and usuario.fk_paciente is not None
        es_doctor = hasattr(usuario, 'fk_doctor') and usuario.fk_doctor is not None

        if not es_paciente or es_doctor:
            messages.error(request, "No tienes permisos para acceder. Solo los pacientes pueden ingresar a esta sección.")
            return redirect('dashboard_doctor')  # O redirecciona a home o login si prefieres
        return view_func(request, *args, **kwargs)
    return _wrapped_view
