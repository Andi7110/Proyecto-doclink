from django.db import models
from django.conf import settings

# Create your models here.
class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    # otros campos

    def __str__(self):
        return self.nombre