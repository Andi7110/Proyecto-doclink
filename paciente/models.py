from django.db import models
from datetime import date
from bd.models import Usuario  # Asegúrate de que esta es la ruta correcta

class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    @property
    def edad(self):
        if self.usuario.fecha_nacimiento:
            today = date.today()
            nacimiento = self.usuario.fecha_nacimiento
            return today.year - nacimiento.year - ((today.month, today.day) < (nacimiento.month, nacimiento.day))
        return None

    @property
    def sexo(self):
        return self.usuario.sexo