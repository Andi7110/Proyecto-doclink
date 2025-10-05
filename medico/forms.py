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
    no_jvpm = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dui = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
