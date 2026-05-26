from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings

from .forms import ClienteForm, DetalleOrdenForm, EmpleadoForm, MesaForm, PlatoForm
from .models import Administrador, Cliente, DetalleOrden, Empleado, Mesa, Orden, Plato
from .role_utils import get_user_role


@override_settings(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
)
class RoleAccessTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_user_role_returns_mesero_role(self):
        user = User.objects.create_user(
            username="mesero1",
            email="mesero1@restaurante.com",
            password="ClaveSegura123",
            first_name="María",
            last_name="López",
        )
        Empleado.objects.create(
            nombre="María López",
            cargo="Mesero",
            telefono="3000000000",
            correo=user.email,
        )

        self.assertEqual(get_user_role(user), "Mesero")

    def test_mesero_can_access_clientes_and_facturas_for_cajero_only(self):
        mesero = User.objects.create_user(
            username="mesero2",
            email="mesero2@restaurante.com",
            password="ClaveSegura123",
            first_name="Carlos",
            last_name="Pérez",
        )
        Empleado.objects.create(
            nombre="Carlos Pérez",
            cargo="Mesero",
            telefono="3000000001",
            correo=mesero.email,
        )

        self.client.force_login(mesero)

        clientes_response = self.client.get("/clientes/")
        self.assertEqual(clientes_response.status_code, 200)

        facturas_response = self.client.get("/facturas/")
        self.assertEqual(facturas_response.status_code, 302)

    def test_cajero_can_access_facturas_and_is_restricted_from_empleados(self):
        cajero = User.objects.create_user(
            username="cajero1",
            email="cajero1@restaurante.com",
            password="ClaveSegura123",
            first_name="Lucía",
            last_name="Gómez",
        )
        Empleado.objects.create(
            nombre="Lucía Gómez",
            cargo="Cajero",
            telefono="3000000002",
            correo=cajero.email,
        )

        self.client.force_login(cajero)

        facturas_response = self.client.get("/facturas/")
        self.assertEqual(facturas_response.status_code, 200)

        empleados_response = self.client.get("/empleados/")
        self.assertEqual(empleados_response.status_code, 302)

    def test_cajero_sees_orders_navigation_and_pending_orders(self):
        cajero = User.objects.create_user(
            username="cajero2",
            email="cajero2@restaurante.com",
            password="ClaveSegura123",
            first_name="Lucía",
            last_name="Gómez",
        )
        Empleado.objects.create(
            nombre="Lucía Gómez",
            cargo="Cajero",
            telefono="3000000005",
            correo=cajero.email,
        )

        mesero = User.objects.create_user(
            username="mesero3",
            email="mesero3@restaurante.com",
            password="ClaveSegura123",
            first_name="Mateo",
            last_name="Díaz",
        )
        mesero_empleado = Empleado.objects.create(
            nombre="Mateo Díaz",
            cargo="Mesero",
            telefono="3000000006",
            correo=mesero.email,
        )
        cliente = Cliente.objects.create(
            nombre="Ana Rivera",
            telefono="3000000007",
            correo="ana@restaurante.com",
        )
        mesa = Mesa.objects.create(numero_mesa=88, capacidad=4, estado_mesa="Disponible")
        orden = Orden.objects.create(
            cliente=cliente,
            empleado=mesero_empleado,
            mesa=mesa,
            estado_orden="Entregada",
            total=0,
        )

        self.client.force_login(cajero)

        response = self.client.get("/ordenes/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/ordenes/"')
        self.assertContains(response, f'/ordenes/{orden.id}/facturar/')

    def test_empleado_form_creates_user_and_role(self):
        form = EmpleadoForm(
            data={
                "nombre": "Diego Torres",
                "cargo": "Mesero",
                "telefono": "3000000003",
                "correo": "diego@restaurante.com",
                "username": "diego",
                "password1": "ClaveSegura123",
                "password2": "ClaveSegura123",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        empleado = form.save()

        user = User.objects.get(username="diego")
        self.assertTrue(user.check_password("ClaveSegura123"))
        self.assertEqual(user.email, "diego@restaurante.com")
        self.assertEqual(get_user_role(user), "Mesero")
        self.assertEqual(empleado.correo, user.email)
        self.assertFalse(Administrador.objects.filter(usuario=user).exists())

    def test_crud_forms_reject_invalid_numeric_fields(self):
        cliente_form = ClienteForm(
            data={
                "nombre": "  Ana Rivera  ",
                "telefono": "abc123",
                "correo": "ana@restaurante.com",
            }
        )
        self.assertFalse(cliente_form.is_valid())
        self.assertIn("telefono", cliente_form.errors)

        empleado_form = EmpleadoForm(
            data={
                "nombre": "Carlos Pérez",
                "cargo": "Mesero",
                "telefono": "12A34",
                "correo": "carlos@restaurante.com",
                "username": "carlos",
                "password1": "ClaveSegura123",
                "password2": "ClaveSegura123",
            }
        )
        self.assertFalse(empleado_form.is_valid())
        self.assertIn("telefono", empleado_form.errors)

        mesa_form = MesaForm(
            data={
                "numero_mesa": "0",
                "capacidad": "-2",
                "estado_mesa": "Disponible",
            }
        )
        self.assertFalse(mesa_form.is_valid())
        self.assertIn("numero_mesa", mesa_form.errors)
        self.assertIn("capacidad", mesa_form.errors)

        plato = Plato.objects.create(
            nombre_plato="Pasta",
            descripcion="Test",
            precio=1000,
            categoria="Principal",
            disponible=True,
        )
        plato_form = PlatoForm(
            data={
                "nombre_plato": "  Pasta Al Pesto  ",
                "descripcion": "  Sabor italiano  ",
                "precio": "abc",
                "categoria": "  Principal  ",
                "disponible": True,
            }
        )
        self.assertFalse(plato_form.is_valid())
        self.assertIn("precio", plato_form.errors)

        detalle_form = DetalleOrdenForm(
            data={
                "plato": plato.pk,
                "cantidad": "0",
            }
        )
        self.assertFalse(detalle_form.is_valid())
        self.assertIn("cantidad", detalle_form.errors)

    def test_empleado_form_creates_admin_account_when_role_is_administrador(self):
        form = EmpleadoForm(
            data={
                "nombre": "Sofía Ruiz",
                "cargo": "Administrador",
                "telefono": "3000000004",
                "correo": "sofia@restaurante.com",
                "username": "sofia",
                "password1": "ClaveSegura123",
                "password2": "ClaveSegura123",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        user = User.objects.get(username="sofia")
        self.assertEqual(get_user_role(user), "Administrador")
        self.assertTrue(Administrador.objects.filter(usuario=user).exists())
