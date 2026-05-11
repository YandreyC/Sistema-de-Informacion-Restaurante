from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Cliente, Empleado, Mesa, Plato, Orden, Factura, Administrador
from .forms import (
    RegistroAdminForm,
    LoginForm,
    ValidarEmailForm,
    CambiarContraseñaForm,
    ClienteForm,
    EmpleadoForm,
    MesaForm,
    PlatoForm,
    OrdenForm,
    FacturaForm,
)
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

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_admin')
        if not Administrador.objects.filter(usuario=request.user).exists():
            messages.error(request, 'Acceso restringido a administradores.')
            return redirect('login_admin')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required(login_url='login_admin')
@admin_required
def inicio(request):
    context = {
        'total_clientes': Cliente.objects.count(),
        'total_empleados': Empleado.objects.count(),
        'total_mesas': Mesa.objects.count(),
        'total_platos': Plato.objects.count(),
        'total_ordenes': Orden.objects.count(),
        'total_facturas': Factura.objects.count(),
    }
    return render(request, 'Gestion/inicio.html', context)

@login_required(login_url='login_admin')
@admin_required
def clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'Gestion/clientes.html', {'clientes': clientes})

@login_required(login_url='login_admin')
@admin_required
def empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'Gestion/empleados.html', {'empleados': empleados})

@login_required(login_url='login_admin')
@admin_required
def mesas(request):
    mesas = Mesa.objects.all()
    return render(request, 'Gestion/mesas.html', {'mesas': mesas})

@login_required(login_url='login_admin')
@admin_required
def platos(request):
    platos = Plato.objects.all()
    return render(request, 'Gestion/platos.html', {'platos': platos})

@login_required(login_url='login_admin')
@admin_required
def ordenes(request):
    ordenes = Orden.objects.all()
    return render(request, 'Gestion/ordenes.html', {'ordenes': ordenes})

@login_required(login_url='login_admin')
@admin_required
def ordenes_crear(request):
    if request.method == 'POST':
        form = OrdenForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Orden creada correctamente.')
            return redirect('ordenes')
    else:
        form = OrdenForm()
    return render(request, 'Gestion/formulario.html', {'form': form, 'titulo': 'Crear Orden'})

@login_required(login_url='login_admin')
@admin_required
def ordenes_editar(request, pk):
    orden = get_object_or_404(Orden, pk=pk)
    if request.method == 'POST':
        form = OrdenForm(request.POST, instance=orden)
        if form.is_valid():
            form.save()
            messages.success(request, 'Orden actualizada correctamente.')
            return redirect('ordenes')
    else:
        form = OrdenForm(instance=orden)
    return render(request, 'Gestion/formulario.html', {'form': form, 'titulo': 'Editar Orden'})

@login_required(login_url='login_admin')
@admin_required
def ordenes_eliminar(request, pk):
    orden = get_object_or_404(Orden, pk=pk)
    if request.method == 'POST':
        orden.delete()
        messages.success(request, 'Orden eliminada correctamente.')
        return redirect('ordenes')
    return render(request, 'Gestion/confirmar_eliminar.html', {
        'objeto': orden,
        'titulo': 'Eliminar Orden',
        'ruta_cancelar': 'ordenes',
    })

@login_required(login_url='login_admin')
@admin_required
def facturas(request):
    facturas = Factura.objects.all()
    return render(request, 'Gestion/facturas.html', {'facturas': facturas})

@login_required(login_url='login_admin')
@admin_required
def facturas_crear(request):
    if request.method == 'POST':
        form = FacturaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Factura creada correctamente.')
            return redirect('facturas')
    else:
        form = FacturaForm()
    return render(request, 'Gestion/formulario.html', {'form': form, 'titulo': 'Crear Factura'})

@login_required(login_url='login_admin')
@admin_required
def facturas_editar(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == 'POST':
        form = FacturaForm(request.POST, instance=factura)
        if form.is_valid():
            form.save()
            messages.success(request, 'Factura actualizada correctamente.')
            return redirect('facturas')
    else:
        form = FacturaForm(instance=factura)
    return render(request, 'Gestion/formulario.html', {'form': form, 'titulo': 'Editar Factura'})

@login_required(login_url='login_admin')
@admin_required
def facturas_eliminar(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == 'POST':
        factura.delete()
        messages.success(request, 'Factura eliminada correctamente.')
        return redirect('facturas')
    return render(request, 'Gestion/confirmar_eliminar.html', {
        'objeto': factura,
        'titulo': 'Eliminar Factura',
        'ruta_cancelar': 'facturas',
    })

@login_required(login_url='login_admin')
@admin_required
def clientes_crear(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado correctamente.')
            return redirect('clientes')
    else:
        form = ClienteForm()
    return render(request, 'Gestion/formulario.html', {'form': form, 'titulo': 'Crear Cliente'})

@login_required(login_url='login_admin')
@admin_required
def clientes_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado correctamente.')
            return redirect('clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'Gestion/formulario.html', {'form': form, 'titulo': 'Editar Cliente'})

@login_required(login_url='login_admin')
@admin_required
def clientes_eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado correctamente.')
        return redirect('clientes')
    return render(request, 'Gestion/confirmar_eliminar.html', {
        'objeto': cliente,
        'titulo': 'Eliminar Cliente',
        'ruta_cancelar': 'clientes',
    })

@login_required(login_url='login_admin')
@admin_required
def empleados_crear(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado creado correctamente.')
            return redirect('empleados')
    else:
        form = EmpleadoForm()
    return render(request, 'Gestion/formulario.html', {'form': form, 'titulo': 'Crear Empleado'})

@login_required(login_url='login_admin')
@admin_required
def empleados_editar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado actualizado correctamente.')
            return redirect('empleados')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'Gestion/formulario.html', {'form': form, 'titulo': 'Editar Empleado'})

@login_required(login_url='login_admin')
@admin_required
def empleados_eliminar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.delete()
        messages.success(request, 'Empleado eliminado correctamente.')
        return redirect('empleados')
    return render(request, 'Gestion/confirmar_eliminar.html', {
        'objeto': empleado,
        'titulo': 'Eliminar Empleado',
        'ruta_cancelar': 'empleados',
    })

@login_required(login_url='login_admin')
@admin_required
def mesas_crear(request):
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mesa creada correctamente.')
            return redirect('mesas')
    else:
        form = MesaForm()
    return render(request, 'Gestion/formulario.html', {'form': form, 'titulo': 'Crear Mesa'})

@login_required(login_url='login_admin')
@admin_required
def mesas_editar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        form = MesaForm(request.POST, instance=mesa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mesa actualizada correctamente.')
            return redirect('mesas')
    else:
        form = MesaForm(instance=mesa)
    return render(request, 'Gestion/formulario.html', {'form': form, 'titulo': 'Editar Mesa'})

@login_required(login_url='login_admin')
@admin_required
def mesas_eliminar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        mesa.delete()
        messages.success(request, 'Mesa eliminada correctamente.')
        return redirect('mesas')
    return render(request, 'Gestion/confirmar_eliminar.html', {
        'objeto': mesa,
        'titulo': 'Eliminar Mesa',
        'ruta_cancelar': 'mesas',
    })

@login_required(login_url='login_admin')
@admin_required
def platos_crear(request):
    if request.method == 'POST':
        form = PlatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plato creado correctamente.')
            return redirect('platos')
    else:
        form = PlatoForm()
    return render(request, 'Gestion/formulario.html', {'form': form, 'titulo': 'Crear Plato'})

@login_required(login_url='login_admin')
@admin_required
def platos_editar(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == 'POST':
        form = PlatoForm(request.POST, instance=plato)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plato actualizado correctamente.')
            return redirect('platos')
    else:
        form = PlatoForm(instance=plato)
    return render(request, 'Gestion/formulario.html', {'form': form, 'titulo': 'Editar Plato'})

@login_required(login_url='login_admin')
@admin_required
def platos_eliminar(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == 'POST':
        plato.delete()
        messages.success(request, 'Plato eliminado correctamente.')
        return redirect('platos')
    return render(request, 'Gestion/confirmar_eliminar.html', {
        'objeto': plato,
        'titulo': 'Eliminar Plato',
        'ruta_cancelar': 'platos',
    })

@login_required(login_url='login_admin')
@admin_required
def ordenes(request):
    ordenes = Orden.objects.all()
    return render(request, 'Gestion/ordenes.html', {'ordenes': ordenes})

