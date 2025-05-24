from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

@login_required
def views_home(request):
    return render(request, 'medico/home.html')

