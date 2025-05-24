from django.shortcuts import render

def inicio_view(request):
    return render(request, 'inicio/inicial.html')

def login_view(request):
    return render(request, 'inicio/login.html')

def seleccion_view(request):
    return render(request, 'inicio/seleccion_registro.html')

def registroDoctor_view(request):
    return render(request, 'inicio/registro_docto1.html')

def registroDoctor2_view(request):
    return render(request, 'inicio/registro_docto2.html')

def registroDoctor3_view(request):
    return render(request, 'inicio/registro_docto3.html')

def registroDoctor4_view(request):
    return render(request, 'inicio/registro_docto4.html')

def registroPaciente1_view(request):
    return render(request, 'inicio/registro_paciente1.html')

def registroPaciente2_view(request):
    return render(request, 'inicio/registro_paciente2.html')

def registroPaciente3_view(request):
    return render(request, 'inicio/registro_paciente3.html')

def registroPaciente4_view(request):
    return render(request, 'inicio/registro_paciente4.html')

def contraOlvidada_view(request):
    return render(request, 'inicio/contra_olvidada.html')

def autenticacion_view(request):
    return render(request, 'inicio/autenticacion.html')
