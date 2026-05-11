from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Cliente, Empleado, Mesa, Plato, Orden, Factura, Administrador
from .forms import RegistroAdminForm, LoginForm, ValidarEmailForm, CambiarContraseñaForm
from django.contrib.auth.models import User

@require_http_methods(["GET", "POST"])
def login_admin(request):
    """Vista de login para administrador"""
    if request.user.is_authenticated:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            # Verificar que sea administrador
            if user is not None:
                try:
                    administrador = Administrador.objects.get(usuario=user)
                    login(request, user)
                    messages.success(request, f'¡Bienvenido {user.first_name}!')
                    return redirect('inicio')
                except Administrador.DoesNotExist:
                    messages.error(request, 'Solo administradores pueden acceder.')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'Gestion/login.html', {'form': form})

@require_http_methods(["GET", "POST"])
def registro_admin(request):
    """Vista para registro de nuevo administrador"""
    if request.user.is_authenticated:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = RegistroAdminForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido al sistema.')
            return redirect('inicio')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistroAdminForm()
    
    return render(request, 'Gestion/registro.html', {'form': form})

@login_required(login_url='login_admin')
def logout_admin(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login_admin')

@require_http_methods(["GET", "POST"])
def recuperar_contraseña(request):
    """Vista para recuperar contraseña validando email"""
    if request.user.is_authenticated:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = ValidarEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.session['email_recuperacion'] = email
            return redirect('cambiar_contraseña')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, str(error))
    else:
        form = ValidarEmailForm()
    
    return render(request, 'Gestion/recuperar_contraseña.html', {'form': form})

@require_http_methods(["GET", "POST"])
def cambiar_contraseña(request):
    """Vista para cambiar contraseña después de validar email"""
    if request.user.is_authenticated:
        return redirect('inicio')
    
    email_recuperacion = request.session.get('email_recuperacion')
    if not email_recuperacion:
        messages.error(request, 'Por favor, ingresa tu correo primero.')
        return redirect('recuperar_contraseña')
    
    if request.method == 'POST':
        form = CambiarContraseñaForm(request.POST)
        if form.is_valid():
            nueva_contraseña = form.cleaned_data['nueva_contraseña']
            try:
                usuario = User.objects.get(email=email_recuperacion, administrador__isnull=False)
                usuario.set_password(nueva_contraseña)
                usuario.save()
                messages.success(request, '¡Contraseña cambiada exitosamente! Ahora puedes iniciar sesión.')
                del request.session['email_recuperacion']
                return redirect('login_admin')
            except User.DoesNotExist:
                messages.error(request, 'Error al cambiar la contraseña.')
                return redirect('recuperar_contraseña')
    else:
        form = CambiarContraseñaForm()
    
    return render(request, 'Gestion/cambiar_contraseña.html', {'form': form, 'email': email_recuperacion})

@login_required(login_url='login_admin')
def inicio(request):
    # Verificar que sea administrador
    try:
        administrador = Administrador.objects.get(usuario=request.user)
    except Administrador.DoesNotExist:
        return redirect('login_admin')
    
    context = {
        'Total_Clientes': Cliente.objects.count(),
        'Total_Empleados': Empleado.objects.count(),
        'Total_Mesas': Mesa.objects.count(),
        'Total_Platos': Plato.objects.count(),
        'Total_Ordenes': Orden.objects.count(),
        'Total_Facturas': Factura.objects.count(),
    }
    return render(request, 'Gestion/inicio.html', context)

@login_required(login_url='login_admin')
def clientes(request):
    # Verificar que sea administrador
    try:
        administrador = Administrador.objects.get(usuario=request.user)
    except Administrador.DoesNotExist:
        return redirect('login_admin')
    
    clientes = Cliente.objects.all()
    return render(request, 'Gestion/clientes.html', {'clientes': clientes})

@login_required(login_url='login_admin')
def empleados(request):
    # Verificar que sea administrador
    try:
        administrador = Administrador.objects.get(usuario=request.user)
    except Administrador.DoesNotExist:
        return redirect('login_admin')
    
    empleados = Empleado.objects.all()
    return render(request, 'Gestion/empleados.html', {'empleados': empleados})

@login_required(login_url='login_admin')
def mesas(request):
    # Verificar que sea administrador
    try:
        administrador = Administrador.objects.get(usuario=request.user)
    except Administrador.DoesNotExist:
        return redirect('login_admin')
    
    mesas = Mesa.objects.all()
    return render(request, 'Gestion/mesas.html', {'mesas': mesas})

@login_required(login_url='login_admin')
def platos(request):
    # Verificar que sea administrador
    try:
        administrador = Administrador.objects.get(usuario=request.user)
    except Administrador.DoesNotExist:
        return redirect('login_admin')
    
    platos = Plato.objects.all()
    return render(request, 'Gestion/platos.html', {'platos': platos})

@login_required(login_url='login_admin')
def ordenes(request):
    # Verificar que sea administrador
    try:
        administrador = Administrador.objects.get(usuario=request.user)
    except Administrador.DoesNotExist:
        return redirect('login_admin')
    
    ordenes = Orden.objects.all()
    return render(request, 'Gestion/ordenes.html', {'ordenes': ordenes})

@login_required(login_url='login_admin')
def facturas(request):
    # Verificar que sea administrador
    try:
        administrador = Administrador.objects.get(usuario=request.user)
    except Administrador.DoesNotExist:
        return redirect('login_admin')
    
    facturas = Factura.objects.all()
    return render(request, 'Gestion/facturas.html', {'facturas': facturas})