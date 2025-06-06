from django.urls import path
from . import views
from .views import views_home



urlpatterns = [
    path('home/', views_home, name='home'),
    path('dashboard_doctor/', views.dashboard_doctor, name='dashboard_doctor'),
]