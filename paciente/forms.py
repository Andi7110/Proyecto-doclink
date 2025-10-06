from django import forms
from bd.models import PolizaSeguro
from bd.models import ContactoEmergencia

class PolizaSeguroForm(forms.ModelForm):
    fecha_vigencia = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = PolizaSeguro
        fields = ['compania_aseguradora', 'numero_poliza', 'fecha_vigencia', 'tipo_cobertura']
        widgets = {
            'compania_aseguradora': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_poliza': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_cobertura': forms.TextInput(attrs={'class': 'form-control'}),
        }



class ContactoEmergenciaForm(forms.ModelForm):
    class Meta:
        model = ContactoEmergencia
        fields = ['nombre_completo', 'parentesco', 'telefono', 'direccion']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'parentesco': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+503XXXXXXXX'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }