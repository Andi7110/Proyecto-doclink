from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect


def views_home(request):  
    return render(request, 'paciente/home.html')

def dashboard_paciente(request):
    return render(request, 'dashboard_paciente.html')