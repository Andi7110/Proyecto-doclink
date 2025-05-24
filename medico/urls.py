from django.urls import path
from . import views
from .views import views_home



urlpatterns = [
    path('home/', views_home, name='home'),
    # ... otras URLs específicas de médicos
]