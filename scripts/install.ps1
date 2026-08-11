<#
Instalador automático para Windows (PowerShell) del proyecto Django.

Uso:
  En PowerShell:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
    .\scripts\install.ps1

Opciones:
  -NoVenv  Evita crear/activar el virtualenv y usa el Python del sistema.
#>

param(
    [switch]$NoVenv
)

Write-Host "Instalador automático del proyecto Django"

# localizar python
$pyCmd = (Get-Command python -ErrorAction SilentlyContinue).Path
if (-not $pyCmd) {
    $pyCmd = (Get-Command py -ErrorAction SilentlyContinue).Path
}
if (-not $pyCmd) {
    Write-Error "Python no encontrado en PATH. Instale Python 3.8+ y vuelva a intentar."
    exit 1
}

if (-not $NoVenv) {
    if (-not (Test-Path ".venv")) {
        & $pyCmd -m venv .venv
    }
    Write-Host "Activando virtualenv..."
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
    . .\venv\Scripts\Activate.ps1
}

Write-Host "Actualizando pip y herramientas..."
pip install --upgrade pip setuptools wheel

if (Test-Path "requirements.txt") {
    Write-Host "Instalando dependencias desde requirements.txt..."
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt no encontrado — instalando Django por defecto..."
    pip install django
}

Write-Host "Aplicando migraciones..."
python manage.py migrate

if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "Recolectando archivos estáticos (collectstatic)..."
    python manage.py collectstatic --noinput
}

Write-Host "Instalación completada. Para crear superusuario, ejecute: python manage.py createsuperuser"
