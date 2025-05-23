from django.urls import path
from .views import login_view
from .views import inicio_view
from .views import seleccion_view

urlpatterns = [
    path('', inicio_view, name='inicio'),
    path('login/', login_view, name='login'),
    path('seleccion_registro/', seleccion_view, name='seleccion'),
]
