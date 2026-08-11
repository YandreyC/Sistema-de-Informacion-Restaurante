from .models import Administrador, Empleado


def get_user_role(user):
    if not user or not user.is_authenticated:
        return None

    if Administrador.objects.filter(usuario=user).exists():
        return "Administrador"

    empleado = Empleado.objects.filter(correo=user.email).first()
    if empleado:
        role_map = {
            "Mesera": "Mesero",
            "Cajera": "Cajero",
        }
        return role_map.get(empleado.cargo, empleado.cargo)

    return None


def user_is_authorized(user):
    return get_user_role(user) in {"Administrador", "Mesero", "Cajero"}


def user_can_access(user, *roles):
    role = get_user_role(user)
    return role == "Administrador" or role in roles
