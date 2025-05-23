from django.shortcuts import render

def inicio_view(request):
    return render(request, 'inicio/inicial.html')

def login_view(request):
    return render(request, 'inicio/login.html')

def seleccion_view(request):
    return render(request, 'inicio/seleccion_registro.html')
