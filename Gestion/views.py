from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import (
    CambiarContraseñaForm,
    ClienteForm,
    EmpleadoForm,
    FacturaForm,
    LoginForm,
    MesaForm,
    OrdenForm,
    PlatoForm,
    RegistroAdminForm,
    UsuarioForm,
    ValidarEmailForm,
)
from .models import Administrador, Cliente, DetalleOrden, Empleado, Factura, Mesa, Orden, Plato
from .role_utils import get_user_role, user_is_authorized


@require_http_methods(["GET", "POST"])
def login_admin(request):
    """Vista de login para administrador, mesero o cajero."""
    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None and user_is_authorized(user):
                login(request, user)
                messages.success(request, f"¡Bienvenido {user.first_name}!")
                return redirect("inicio")

            if user is not None:
                messages.error(request, "La cuenta no tiene un rol autorizado en el sistema.")
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()

    return render(request, "Gestion/login.html", {"form": form})


@require_http_methods(["GET", "POST"])
def registro_admin(request):
    """Vista para registro de nuevo administrador."""
    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":
        form = RegistroAdminForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Registro exitoso! Bienvenido al sistema.")
            return redirect("inicio")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    else:
        form = RegistroAdminForm()

    return render(request, "Gestion/registro.html", {"form": form})


@login_required(login_url="login_admin")
def logout_admin(request):
    """Vista para cerrar sesión."""
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("login_admin")


@require_http_methods(["GET", "POST"])
def recuperar_contraseña(request):
    """Vista para recuperar contraseña validando el correo del usuario."""
    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":
        form = ValidarEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            request.session["email_recuperacion"] = email
            return redirect("cambiar_contraseña")

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, str(error))
    else:
        form = ValidarEmailForm()

    return render(request, "Gestion/recuperar_contraseña.html", {"form": form})


@require_http_methods(["GET", "POST"])
def cambiar_contraseña(request):
    """Vista para cambiar contraseña después de validar el correo."""
    if request.user.is_authenticated:
        return redirect("inicio")

    email_recuperacion = request.session.get("email_recuperacion")
    if not email_recuperacion:
        messages.error(request, "Por favor, ingresa tu correo primero.")
        return redirect("recuperar_contraseña")

    if request.method == "POST":
        form = CambiarContraseñaForm(request.POST)
        if form.is_valid():
            nueva_contraseña = form.cleaned_data["nueva_contraseña"]
            try:
                usuario = User.objects.get(email=email_recuperacion)
                usuario.set_password(nueva_contraseña)
                usuario.save()
                messages.success(request, "¡Contraseña cambiada exitosamente! Ahora puedes iniciar sesión.")
                del request.session["email_recuperacion"]
                return redirect("login_admin")
            except User.DoesNotExist:
                messages.error(request, "Error al cambiar la contraseña.")
                return redirect("recuperar_contraseña")
    else:
        form = CambiarContraseñaForm()

    return render(request, "Gestion/cambiar_contraseña.html", {"form": form, "email": email_recuperacion})


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login_admin")
        if not Administrador.objects.filter(usuario=request.user).exists():
            messages.error(request, "Acceso restringido a administradores.")
            return redirect("inicio")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login_admin")

            role = get_user_role(request.user)
            if not role:
                messages.error(request, "La cuenta no tiene un rol autorizado en el sistema.")
                return redirect("login_admin")

            if role == "Administrador" or role in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(request, "No tienes permisos para acceder a esta sección.")
            return redirect("inicio")

        return _wrapped_view

    return decorator


@login_required(login_url="login_admin")
def inicio(request):
    role = get_user_role(request.user)

    if role == "Administrador":
        context = {
            "role": role,
            "total_clientes": Cliente.objects.count(),
            "total_empleados": Empleado.objects.count(),
            "total_mesas": Mesa.objects.count(),
            "total_platos": Plato.objects.count(),
            "total_ordenes": Orden.objects.count(),
            "total_facturas": Factura.objects.count(),
        }
    elif role == "Mesero":
        context = {
            "role": role,
            "mesas_disponibles": Mesa.objects.filter(estado_mesa="Disponible").count(),
            "mesas_ocupadas": Mesa.objects.filter(estado_mesa="Ocupada").count(),
            "ordenes_activas": Orden.objects.filter(estado_orden__in=["Activa", "En preparación"]).count(),
            "total_clientes": Cliente.objects.count(),
        }
    elif role == "Cajero":
        total_ventas = Factura.objects.aggregate(total=Sum("total_factura"))["total"] or 0
        context = {
            "role": role,
            "ordenes_pendientes": Orden.objects.filter(estado_orden="Entregada").count(),
            "facturas_emitidas": Factura.objects.count(),
            "total_ventas": total_ventas,
        }
    else:
        context = {"role": role}

    return render(request, "Gestion/inicio.html", context)


@login_required(login_url="login_admin")
@role_required("Administrador", "Mesero")
def clientes(request):
    clientes = Cliente.objects.all()
    return render(request, "Gestion/clientes.html", {"clientes": clientes})


@login_required(login_url="login_admin")
@admin_required
def empleados(request):
    empleados = Empleado.objects.all()
    return render(request, "Gestion/empleados.html", {"empleados": empleados})


@login_required(login_url="login_admin")
@role_required("Administrador", "Mesero")
def mesas(request):
    mesas = Mesa.objects.all()
    return render(request, "Gestion/mesas.html", {"mesas": mesas})


@login_required(login_url="login_admin")
@role_required("Administrador", "Mesero")
def platos(request):
    platos = Plato.objects.all()
    return render(request, "Gestion/platos.html", {"platos": platos})


@login_required(login_url="login_admin")
@role_required("Administrador", "Mesero", "Cajero")
def ordenes(request):
    role = get_user_role(request.user)
    if role == "Cajero":
        ordenes = Orden.objects.filter(estado_orden__in=["Entregada", "Facturada"])
    else:
        ordenes = Orden.objects.all()

    return render(request, "Gestion/ordenes.html", {"ordenes": ordenes})


@login_required(login_url="login_admin")
@role_required("Administrador", "Mesero")
def ordenes_crear(request):
    platos = Plato.objects.filter(disponible=True)
    if request.method == "POST":
        form = OrdenForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.estado_orden = "Activa"
            orden.total = 0
            orden.save()

            platos_ids = request.POST.getlist("plato_id")
            cantidades = request.POST.getlist("cantidad")

            total_orden = 0
            detalles_creados = False

            for plato_id, cantidad in zip(platos_ids, cantidades):
                if plato_id and cantidad:
                    try:
                        plato = Plato.objects.get(id=int(plato_id))
                        cantidad = int(cantidad)
                        if cantidad > 0:
                            detalle = DetalleOrden.objects.create(orden=orden, plato=plato, cantidad=cantidad)
                            total_orden += detalle.subtotal
                            detalles_creados = True
                    except (Plato.DoesNotExist, ValueError):
                        continue

            if detalles_creados:
                orden.total = total_orden
                orden.save()
                orden.mesa.estado_mesa = "Ocupada"
                orden.mesa.save(update_fields=["estado_mesa"])
                messages.success(request, "Orden creada correctamente con los platos seleccionados.")
                return redirect("ordenes")

            orden.delete()
            messages.error(request, "Debes agregar al menos un plato a la orden.")
            return redirect("ordenes_crear")
    else:
        form = OrdenForm()

    return render(
        request,
        "Gestion/crear_orden.html",
        {
            "form": form,
            "platos": platos,
            "titulo": "📋 Nueva Orden",
            "submit_text": "✓ Crear Orden",
            "detalles": [],
        },
    )


@login_required(login_url="login_admin")
@role_required("Administrador", "Mesero")
def ordenes_editar(request, pk):
    orden = get_object_or_404(Orden, pk=pk)

    if orden.estado_orden == "Facturada":
        messages.warning(request, "No se puede editar una orden que ya está facturada.")
        return redirect("ordenes")

    original_mesa = orden.mesa
    platos = Plato.objects.filter(Q(disponible=True) | Q(id__in=orden.detalles.values_list("plato", flat=True))).distinct()

    if request.method == "POST":
        form = OrdenForm(request.POST, instance=orden)
        if form.is_valid():
            orden = form.save(commit=False)

            platos_ids = request.POST.getlist("plato_id")
            cantidades = request.POST.getlist("cantidad")
            total_orden = 0
            detalles_creados = False
            detalles_data = []

            for plato_id, cantidad in zip(platos_ids, cantidades):
                if plato_id and cantidad:
                    try:
                        plato = Plato.objects.get(id=int(plato_id))
                        cantidad = int(cantidad)
                        if cantidad > 0:
                            detalles_data.append((plato, cantidad))
                            total_orden += plato.precio * cantidad
                            detalles_creados = True
                    except (Plato.DoesNotExist, ValueError):
                        continue

            if detalles_creados:
                if orden.mesa != original_mesa:
                    original_mesa.estado_mesa = "Disponible"
                    original_mesa.save(update_fields=["estado_mesa"])
                    orden.mesa.estado_mesa = "Ocupada"
                    orden.mesa.save(update_fields=["estado_mesa"])

                orden.total = total_orden
                orden.save()
                DetalleOrden.objects.filter(orden=orden).delete()

                for plato, cantidad in detalles_data:
                    DetalleOrden.objects.create(orden=orden, plato=plato, cantidad=cantidad)

                messages.success(request, "Orden actualizada correctamente.")
                return redirect("ordenes")

            messages.error(request, "Debes agregar al menos un plato a la orden.")
    else:
        form = OrdenForm(instance=orden)

    return render(
        request,
        "Gestion/crear_orden.html",
        {
            "form": form,
            "platos": platos,
            "titulo": "✏️ Editar Orden",
            "submit_text": "✓ Guardar cambios",
            "detalles": orden.detalles.all(),
        },
    )


@login_required(login_url="login_admin")
@role_required("Administrador", "Mesero")
def orden_atender(request, pk):
    orden = get_object_or_404(Orden, pk=pk)
    orden.estado_orden = "Entregada"
    orden.save()
    messages.success(request, "Orden marcada como entregada.")
    return redirect("ordenes")


@login_required(login_url="login_admin")
@role_required("Administrador", "Cajero")
def orden_facturar(request, pk):
    orden = get_object_or_404(Orden, pk=pk)

    if Factura.objects.filter(orden=orden).exists():
        messages.warning(request, "Esta orden ya tiene una factura.")
        return redirect("ordenes")

    if request.method == "POST":
        metodo_pago = request.POST.get("metodo_pago", "Efectivo")

        orden.update_total()
        factura = Factura.objects.create(orden=orden, metodo_pago=metodo_pago)

        orden.estado_orden = "Facturada"
        orden.save(update_fields=["estado_orden"])
        orden.mesa.estado_mesa = "Disponible"
        orden.mesa.save(update_fields=["estado_mesa"])

        messages.success(request, f"Factura #{factura.id} creada exitosamente.")
        return redirect("ordenes")

    return render(request, "Gestion/facturar_orden.html", {"orden": orden})


@login_required(login_url="login_admin")
@role_required("Administrador", "Cajero")
def facturas(request):
    facturas = Factura.objects.all()
    return render(request, "Gestion/facturas.html", {"facturas": facturas})


@login_required(login_url="login_admin")
@admin_required
def clientes_crear(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente creado correctamente.")
            return redirect("clientes")
    else:
        form = ClienteForm()

    return render(request, "Gestion/formulario.html", {"form": form, "titulo": "Crear Cliente"})


@login_required(login_url="login_admin")
@admin_required
def clientes_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente actualizado correctamente.")
            return redirect("clientes")
    else:
        form = ClienteForm(instance=cliente)

    return render(request, "Gestion/formulario.html", {"form": form, "titulo": "Editar Cliente"})


@login_required(login_url="login_admin")
@admin_required
def clientes_eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        cliente.delete()
        messages.success(request, "Cliente eliminado correctamente.")
        return redirect("clientes")

    return render(
        request,
        "Gestion/confirmar_eliminar.html",
        {
            "objeto": cliente,
            "titulo": "Eliminar Cliente",
            "ruta_cancelar": "clientes",
        },
    )


@login_required(login_url="login_admin")
@admin_required
def empleados_crear(request):
    if request.method == "POST":
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Empleado creado correctamente.")
            return redirect("empleados")
    else:
        form = EmpleadoForm()

    return render(request, "Gestion/formulario.html", {"form": form, "titulo": "Crear Empleado"})


@login_required(login_url="login_admin")
@admin_required
def empleados_editar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == "POST":
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, "Empleado actualizado correctamente.")
            return redirect("empleados")
    else:
        form = EmpleadoForm(instance=empleado)

    return render(request, "Gestion/formulario.html", {"form": form, "titulo": "Editar Empleado"})


@login_required(login_url="login_admin")
@admin_required
def empleados_eliminar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == "POST":
        empleado.delete()
        messages.success(request, "Empleado eliminado correctamente.")
        return redirect("empleados")

    return render(
        request,
        "Gestion/confirmar_eliminar.html",
        {
            "objeto": empleado,
            "titulo": "Eliminar Empleado",
            "ruta_cancelar": "empleados",
        },
    )


@login_required(login_url="login_admin")
@admin_required
def usuarios(request):
    usuarios = []
    for user in User.objects.all().order_by("username"):
        usuarios.append(
            {
                "user": user,
                "role": get_user_role(user) or "Sin rol",
            }
        )

    return render(request, "Gestion/usuarios.html", {"usuarios": usuarios})


@login_required(login_url="login_admin")
@admin_required
def usuarios_crear(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect("usuarios")
    else:
        form = UsuarioForm()

    return render(request, "Gestion/formulario.html", {"form": form, "titulo": "Crear usuario"})


@login_required(login_url="login_admin")
@admin_required
def mesas_crear(request):
    if request.method == "POST":
        form = MesaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mesa creada correctamente.")
            return redirect("mesas")
    else:
        form = MesaForm()

    return render(request, "Gestion/formulario.html", {"form": form, "titulo": "Crear Mesa"})


@login_required(login_url="login_admin")
@admin_required
def mesas_editar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == "POST":
        form = MesaForm(request.POST, instance=mesa)
        if form.is_valid():
            form.save()
            messages.success(request, "Mesa actualizada correctamente.")
            return redirect("mesas")
    else:
        form = MesaForm(instance=mesa)

    return render(request, "Gestion/formulario.html", {"form": form, "titulo": "Editar Mesa"})


@login_required(login_url="login_admin")
@admin_required
def mesas_eliminar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == "POST":
        mesa.delete()
        messages.success(request, "Mesa eliminada correctamente.")
        return redirect("mesas")

    return render(
        request,
        "Gestion/confirmar_eliminar.html",
        {
            "objeto": mesa,
            "titulo": "Eliminar Mesa",
            "ruta_cancelar": "mesas",
        },
    )


@login_required(login_url="login_admin")
@admin_required
def platos_crear(request):
    if request.method == "POST":
        form = PlatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Plato creado correctamente.")
            return redirect("platos")
    else:
        form = PlatoForm()

    return render(request, "Gestion/formulario.html", {"form": form, "titulo": "Crear Plato"})


@login_required(login_url="login_admin")
@admin_required
def platos_editar(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == "POST":
        form = PlatoForm(request.POST, instance=plato)
        if form.is_valid():
            form.save()
            messages.success(request, "Plato actualizado correctamente.")
            return redirect("platos")
    else:
        form = PlatoForm(instance=plato)

    return render(request, "Gestion/formulario.html", {"form": form, "titulo": "Editar Plato"})


@login_required(login_url="login_admin")
@admin_required
def platos_eliminar(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == "POST":
        plato.delete()
        messages.success(request, "Plato eliminado correctamente.")
        return redirect("platos")

    return render(
        request,
        "Gestion/confirmar_eliminar.html",
        {
            "objeto": plato,
            "titulo": "Eliminar Plato",
            "ruta_cancelar": "platos",
        },
    )

