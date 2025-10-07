from django import forms
from datetime import date, datetime
from bd.models import CitasMedicas, ConsultaMedica, Usuario, Medico, SeguimientoClinico, ConsultaSeguimiento
from django import forms
from bd.models import CitasMedicas, ConsultaMedica, Usuario, Medico


class CitaConsultaForm(forms.ModelForm):
    class Meta:
        model = CitasMedicas
        fields = ['des_motivo_consulta_paciente', 'diagnostico', 'notas_medicas']
        widgets = {
            'des_motivo_consulta_paciente': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'diagnostico': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notas_medicas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class ConsultaMedicaForm(forms.ModelForm):
    class Meta:
        model = ConsultaMedica
        fields = ['sintomas', 'diagnostico', 'tratamiento', 'observaciones', 'documentos_adjuntos']
        widgets = {
            'sintomas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PerfilMedicoForm(forms.Form):
    # Campos de Usuario
    nombre = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellido = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    correo = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    departamento = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    municipio = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    # Campos de Medico
    especialidad = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sub_especialidad_1 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sub_especialidad_2 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
class SeguimientoClinicoForm(forms.ModelForm):
    class Meta:
        model = SeguimientoClinico
        fields = ['diagnostico_final', 'observaciones', 'tratamiento', 'medicamento', 'dosis', 'frecuencia', 'duracion', 'archivos_receta', 'programar_nueva_consulta', 'fecha_nueva_consulta', 'hora_nueva_consulta', 'notas_nueva_consulta']
        widgets = {
            'diagnostico_final': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medicamento': forms.TextInput(attrs={'class': 'form-control'}),
            'dosis': forms.TextInput(attrs={'class': 'form-control'}),
            'frecuencia': forms.TextInput(attrs={'class': 'form-control'}),
            'duracion': forms.TextInput(attrs={'class': 'form-control'}),
            'notas_nueva_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'fecha_nueva_consulta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_nueva_consulta': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

class ProgramarCitaSeguimientoForm(forms.Form):
    fecha_nueva_cita = forms.DateField(
        label="Fecha de la Cita",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    hora_nueva_cita = forms.TimeField(
        label="Hora de la Cita",
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        required=True
    )
    motivo_nueva_cita = forms.CharField(
        label="Motivo de la Cita de Seguimiento",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Consulta de seguimiento'}),
        required=True
    )

    def clean_fecha_nueva_cita(self):
        fecha = self.cleaned_data.get('fecha_nueva_cita')
        if fecha and fecha < date.today():
            raise forms.ValidationError("La fecha de la cita debe ser futura.")
        return fecha
    no_jvpm = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dui = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
