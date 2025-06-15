from django.db import models
from django.conf import settings
from paciente.models import Paciente

# Create your models here.
class Consulta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    diagnostico = models.TextField()
    tratamiento = models.TextField()
    prescripcion = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    documentos = models.FileField(upload_to='consultas_documentos/', blank=True, null=True)  # para adjuntar un archivo (si quieres múltiples, usa otro modelo)

    consulta_completada = models.BooleanField(default=False)

    def __str__(self):
        return f'Consulta {self.id} - {self.paciente.nombre} - {self.fecha.strftime("%Y-%m-%d")}'