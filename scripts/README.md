# Scripts de instalación

Estos scripts automatizan la instalación y configuración mínima del proyecto Django.

- `scripts/install.ps1` — Script para PowerShell (Windows).
- `scripts/install.sh` — Script para sistemas Unix (macOS, Linux).

Cómo usar

Windows (PowerShell):

1. Abrir PowerShell en la raíz del proyecto.
2. Permitir ejecución temporal y ejecutar:

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\scripts\install.ps1
```

Unix (macOS / Linux):

```
bash scripts/install.sh
```

Notas

- Ambos scripts crearán un virtualenv en `.venv`, instalarán dependencias desde `requirements.txt` (si existe), aplicarán migraciones y ejecutarán `collectstatic`.
- Si no existe `requirements.txt`, se instalará `django` por defecto; es recomendable crear un `requirements.txt` con las dependencias reales del proyecto.
- Después de la instalación puede crear un superusuario con `python manage.py createsuperuser`.
