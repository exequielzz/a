from django import forms
from .models import Pedido

class SolicitudPedidoForm(forms.ModelForm):
    descripcion_solicitada = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Describe tu solicitud en detalle...'
        }),
        label="Descripción de lo solicitado"
    )

    imagenes_referencia = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'multiple': True,
            'class': 'form-control'
        }),
        required=False,
        label="Imágenes de referencia (máx. 3)"
    )

    class Meta:
        model = Pedido
        fields = [
            'nombre_cliente',
            'email_cliente',
            'telefono_cliente',
            'red_social_cliente',
            'descripcion_solicitada',
            'fecha_necesidad',
        ]

        widgets = {
            'nombre_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre'
            }),
            'email_cliente': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
            'telefono_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: +56 9 1234 5678'
            }),
            'red_social_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@tuusuario o link'
            }),
            'fecha_necesidad': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
