from django.shortcuts import render

# Create your views here.
from .models import Cliente, Empleado, Mesa, Plato, Orden, Factura

def inicio(request):
    context = {
        'Total_Clientes': Cliente.objects.count(),
        'Total_Empleados': Empleado.objects.count(),
        'Total_Mesas': Mesa.objects.count(),
        'Total_Platos': Plato.objects.count(),
        'Total_Ordenes': Orden.objects.count(),
        'Total_Facturas': Factura.objects.count(),
    }
    return render(request, 'Gestion/inicio.html', context)

def clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'Gestion/clientes.html', {'clientes': clientes})

def empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'Gestion/empleados.html', {'empleados': empleados})

def mesas(request):
    mesas = Mesa.objects.all()
    return render(request, 'Gestion/mesas.html', {'mesas': mesas})

def platos(request):
    platos = Plato.objects.all()
    return render(request, 'Gestion/platos.html', {'platos': platos})

def ordenes(request):
    ordenes = Orden.objects.all()
    return render(request, 'Gestion/ordenes.html', {'ordenes': ordenes})

def facturas(request):
    facturas = Factura.objects.all()
    return render(request, 'Gestion/facturas.html', {'facturas': facturas})