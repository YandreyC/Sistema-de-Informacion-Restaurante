import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Administrador, Cliente, Empleado, Mesa, Plato, Orden, Factura, DetalleOrden


def normalize_text(value):
    return (value or "").strip()


def validate_only_digits(value):
    value = normalize_text(value)
    if value and not re.fullmatch(r"\d+", value):
        raise forms.ValidationError("Este campo solo puede contener números.")
    return value


class RegistroAdminForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono (opcional)'
        })
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Usuario'
            }),
        }

    def clean_email(self):
        email = normalize_text(self.cleaned_data.get('email')).lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_username(self):
        username = normalize_text(self.cleaned_data.get('username'))
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este usuario ya existe.")
        return username

    def clean_telefono(self):
        return validate_only_digits(self.cleaned_data.get('telefono'))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            telefono = self.cleaned_data.get('telefono', '')
            Administrador.objects.create(usuario=user, telefono=telefono)
        return user


class UsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    cargo = forms.ChoiceField(
        choices=[
            ('Administrador', 'Administrador'),
            ('Mesero', 'Mesero'),
            ('Cajero', 'Cajero'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono (opcional)'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'cargo', 'telefono', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Usuario'
            }),
        }

    def clean_email(self):
        email = normalize_text(self.cleaned_data.get('email')).lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        if Empleado.objects.filter(correo=email).exists():
            raise forms.ValidationError('Ya existe un empleado con este correo electrónico.')
        return email

    def clean_username(self):
        username = normalize_text(self.cleaned_data.get('username'))
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este usuario ya existe.')
        return username

    def clean_telefono(self):
        return validate_only_digits(self.cleaned_data.get('telefono'))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            nombre_completo = f"{user.first_name} {user.last_name}".strip()
            telefono = self.cleaned_data.get('telefono', '')
            Empleado.objects.create(
                nombre=nombre_completo,
                cargo=self.cleaned_data['cargo'],
                telefono=telefono,
                correo=user.email,
            )

            if self.cleaned_data['cargo'] == 'Administrador':
                Administrador.objects.get_or_create(usuario=user, defaults={'telefono': telefono})

        return user


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'correo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
        }

    def clean_correo(self):
        return normalize_text(self.cleaned_data.get('correo')).lower()

    def clean_telefono(self):
        return validate_only_digits(self.cleaned_data.get('telefono'))


class EmpleadoForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario'
        })
    )
    password1 = forms.CharField(
        label='Contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    )

    class Meta:
        model = Empleado
        fields = ['nombre', 'cargo', 'telefono', 'correo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'cargo': forms.Select(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linked_user = None

        if self.instance and self.instance.pk:
            self.linked_user = User.objects.filter(email=self.instance.correo).first()
            if self.linked_user:
                self.fields['username'].initial = self.linked_user.username
                self.fields['correo'].initial = self.linked_user.email

        if not self.instance or not self.instance.pk:
            self.fields['password1'].required = True
            self.fields['password2'].required = True

    def _split_nombre(self, nombre):
        partes = [parte for parte in str(nombre or '').split() if parte]
        if not partes:
            return '', ''
        if len(partes) == 1:
            return partes[0], ''
        return partes[0], ' '.join(partes[1:])

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        queryset = User.objects.filter(username=username)
        if self.linked_user is not None:
            queryset = queryset.exclude(pk=self.linked_user.pk)

        if queryset.exists():
            raise forms.ValidationError('Este usuario ya existe.')
        return username

    def clean_correo(self):
        correo = normalize_text(self.cleaned_data['correo']).lower()
        queryset = Empleado.objects.filter(correo=correo)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError('Ya existe otro empleado con este correo electrónico.')

        user_queryset = User.objects.filter(email=correo)
        if self.linked_user is not None:
            user_queryset = user_queryset.exclude(pk=self.linked_user.pk)

        if user_queryset.exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado en otro usuario.')

        return correo

    def clean_telefono(self):
        return validate_only_digits(self.cleaned_data.get('telefono'))

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if self.instance and self.instance.pk and not password1 and not password2:
            return cleaned_data

        if password1 != password2:
            raise forms.ValidationError({'password2': 'Las contraseñas no coinciden.'})

        if password1 and len(password1) < 8:
            raise forms.ValidationError({'password1': 'La contraseña debe tener al menos 8 caracteres.'})

        return cleaned_data

    def save(self, commit=True):
        empleado = super().save(commit=False)

        if commit:
            empleado.save()

            first_name, last_name = self._split_nombre(empleado.nombre)
            user = self.linked_user

            if user is None:
                user = User.objects.create_user(
                    username=self.cleaned_data['username'],
                    email=empleado.correo,
                    password=self.cleaned_data['password1'],
                )
            else:
                user.username = self.cleaned_data['username']
                user.email = empleado.correo
                if self.cleaned_data.get('password1'):
                    user.set_password(self.cleaned_data['password1'])

            user.first_name = first_name
            user.last_name = last_name
            user.save()

            if empleado.cargo == 'Administrador':
                admin, created = Administrador.objects.get_or_create(usuario=user)
                admin.telefono = empleado.telefono
                admin.save()
            else:
                Administrador.objects.filter(usuario=user).delete()

        return empleado


class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['numero_mesa', 'capacidad', 'estado_mesa']
        widgets = {
            'numero_mesa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número de mesa'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Capacidad'}),
            'estado_mesa': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_numero_mesa(self):
        numero_mesa = self.cleaned_data.get('numero_mesa')
        if numero_mesa is None or numero_mesa <= 0:
            raise forms.ValidationError('El número de mesa debe ser mayor que cero.')
        return numero_mesa

    def clean_capacidad(self):
        capacidad = self.cleaned_data.get('capacidad')
        if capacidad is None or capacidad <= 0:
            raise forms.ValidationError('La capacidad debe ser mayor que cero.')
        return capacidad


class PlatoForm(forms.ModelForm):
    class Meta:
        model = Plato
        fields = ['nombre_plato', 'descripcion', 'precio', 'categoria', 'disponible']
        widgets = {
            'nombre_plato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del plato'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Precio'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoría'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is None or precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor que cero.')
        return precio

    def clean_nombre_plato(self):
        return normalize_text(self.cleaned_data.get('nombre_plato'))

    def clean_descripcion(self):
        return normalize_text(self.cleaned_data.get('descripcion'))

    def clean_categoria(self):
        return normalize_text(self.cleaned_data.get('categoria'))


class OrdenForm(forms.ModelForm):
    class Meta:
        model = Orden
        fields = ['cliente', 'empleado', 'mesa']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'empleado': forms.Select(attrs={'class': 'form-control'}),
            'mesa': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['mesa'].queryset = Mesa.objects.filter(
                Q(estado_mesa='Disponible') | Q(pk=self.instance.mesa.pk)
            )
        else:
            self.fields['mesa'].queryset = Mesa.objects.filter(estado_mesa='Disponible')


class DetalleOrdenForm(forms.ModelForm):
    class Meta:
        model = DetalleOrden
        fields = ['plato', 'cantidad']
        widgets = {
            'plato': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1',
                'placeholder': 'Cantidad'
            }),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None or cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor que cero.')
        return cantidad


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['orden', 'subtotal', 'impuesto', 'total_factura', 'metodo_pago']
        widgets = {
            'orden': forms.Select(attrs={'class': 'form-control'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Subtotal'}),
            'impuesto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Impuesto'}),
            'total_factura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Total'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
        }


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )


class ValidarEmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico registrado',
            'autofocus': True
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No hay un usuario registrado con este correo.")
        return email


class CambiarContraseñaForm(forms.Form):
    nueva_contraseña = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        })
    )
    confirmar_contraseña = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        nueva_contraseña = cleaned_data.get('nueva_contraseña')
        confirmar_contraseña = cleaned_data.get('confirmar_contraseña')

        if nueva_contraseña and confirmar_contraseña:
            if nueva_contraseña != confirmar_contraseña:
                raise forms.ValidationError("Las contraseñas no coinciden.")
            if len(nueva_contraseña) < 8:
                raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")

        return cleaned_data


