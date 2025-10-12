from django import forms
from bd.models import PolizaSeguro, ContactoEmergencia, Usuario, MetodosPago

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

class PerfilPacienteForm(forms.Form):
    # Campos de Usuario
    nombre = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellido = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    correo = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    departamento = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    municipio = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    sexo = forms.ChoiceField(
        choices=[('', 'Selecciona el sexo'), ('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Campo para foto de perfil
    foto_perfil = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

class MetodoPagoForm(forms.Form):
    metodo_pago = forms.ChoiceField(
        choices=[('efectivo', 'Efectivo'), ('tarjeta', 'Tarjeta')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Método de pago"
    )
    monto_consulta = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="Monto de la consulta"
    )

    # Campos para tarjeta (se mostrarán dinámicamente con JavaScript)
    numero_tarjeta = forms.CharField(
        max_length=16,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567890123456'}),
        label="Número de tarjeta"
    )
    fecha_expiracion = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'}),
        label="Fecha de expiración"
    )
    cvv = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123'}),
        label="CVV"
    )
    nombre_titular = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Nombre del titular"
    )
    tipo_tarjeta = forms.ChoiceField(
        choices=[('debito', 'Débito'), ('credito', 'Crédito')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Tipo de tarjeta"
    )

    def clean(self):
        cleaned_data = super().clean()
        metodo_pago = cleaned_data.get('metodo_pago')

        if metodo_pago == 'tarjeta':
            # Validar campos de tarjeta
            required_fields = ['numero_tarjeta', 'fecha_expiracion', 'cvv', 'nombre_titular', 'tipo_tarjeta']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f"Este campo es obligatorio para pago con tarjeta.")

            # Validar formato de número de tarjeta (16 dígitos)
            numero_tarjeta = cleaned_data.get('numero_tarjeta')
            if numero_tarjeta and not numero_tarjeta.isdigit() or len(numero_tarjeta) != 16:
                self.add_error('numero_tarjeta', "El número de tarjeta debe tener 16 dígitos.")

            # Validar formato de fecha de expiración (MM/YY)
            fecha_expiracion = cleaned_data.get('fecha_expiracion')
            if fecha_expiracion:
                import re
                if not re.match(r'^\d{2}/\d{2}$', fecha_expiracion):
                    self.add_error('fecha_expiracion', "Formato inválido. Use MM/YY.")

        return cleaned_data