from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps

def paciente_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        usuario = request.user
        if not hasattr(usuario, 'fk_paciente') or usuario.fk_paciente is None:
            messages.error(request, "No tienes permisos para acceder. Solo los pacientes pueden ingresar a esta sección.")
            return redirect('dashboard_paciente')  # o cualquier página que tengas de destino
        return view_func(request, *args, **kwargs)
    return _wrapped_view
