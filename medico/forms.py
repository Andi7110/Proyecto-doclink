from django import forms
from bd.models import CitasMedicas

class CitaConsultaForm(forms.ModelForm):
    class Meta:
        model = CitasMedicas
        fields = ['des_motivo_consulta_paciente', 'diagnostico', 'notas_medicas']
        widgets = {
            'des_motivo_consulta_paciente': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'diagnostico': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notas_medicas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
