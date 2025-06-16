from django import forms
from bd.models import CitasMedicas
from bd.models import ConsultaMedica


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
        fields = ['diagnostico', 'tratamiento', 'prescripcion', 'observaciones', 'adjunto']
        widgets = {
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prescripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
