import re
from django import forms
from .models import Cajero

class CajeroForm(forms.ModelForm):
    class Meta:
        model = Cajero
        fields = ['id_cajero', 'rut', 'nombre', 'nombre_cajero', 'estado']
        widgets = {
            'id_cajero': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 70}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.123.123-1'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_cajero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre o Empresa'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    # Método de validación específico para el campo 'rut'
    def clean_rut(self):
        rut_raw = self.cleaned_data.get('rut')
        
        # 1. Limpiar el RUT (quitar puntos, guiones y espacios) y pasarlo a mayúsculas
        rut_clean = re.sub(r'[^0-9kK]', '', str(rut_raw)).upper()
        
        # 2. Validar largo mínimo y máximo aceptable (ej: entre 7 y 9 caracteres)
        if len(rut_clean) < 7 or len(rut_clean) > 9:
            raise forms.ValidationError("El RUT no tiene un largo válido.")
        
        # 3. Separar el cuerpo numérico del dígito verificador (DV)
        cuerpo = rut_clean[:-1]
        dv_ingresado = rut_clean[-1]
        
        # Asegurarse de que el cuerpo sean solo números
        if not cuerpo.isdigit():
            raise forms.ValidationError("El formato del RUT es incorrecto.")
            
        # 4. Calcular el Dígito Verificador Teórico (Módulo 11)
        suma = 0
        multiplicador = 2
        for d in reversed(cuerpo):
            suma += int(d) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1
            
        dv_esperado = 11 - (suma % 11)
        
        if dv_esperado == 11:
            dv_esperado = '0'
        elif dv_esperado == 10:
            dv_esperado = 'K'
        else:
            dv_esperado = str(dv_esperado)
            
        # 5. Comparar el DV ingresado con el esperado
        if dv_ingresado != dv_esperado:
            raise forms.ValidationError("El RUT ingresado no es válido.")
            
        # Formatear el RUT antes de guardarlo en la base de datos (ej: 12.111.111-6)
        rut_formateado = f"{int(cuerpo):,}".replace(",", ".") + f"-{dv_ingresado}"
        
        return rut_formateado
