#!/usr/bin/env bash
set -euo pipefail

echo "Instalador automático del proyecto Django"

PYTHON=$(command -v python3 || command -v python || true)
if [ -z "${PYTHON}" ]; then
  echo "Python no encontrado. Instale Python 3.8+." >&2
  exit 1
fi

if [ ! -d ".venv" ]; then
  "$PYTHON" -m venv .venv
fi
source .venv/bin/activate

pip install --upgrade pip setuptools wheel

if [ -f requirements.txt ]; then
  echo "Instalando dependencias desde requirements.txt..."
  pip install -r requirements.txt
else
  echo "requirements.txt no encontrado — instalando Django por defecto..."
  pip install django
fi

echo "Aplicando migraciones..."
python manage.py migrate

echo "Recolectando archivos estáticos (collectstatic)..."
python manage.py collectstatic --noinput

echo "Instalación completada. Para crear superusuario: python manage.py createsuperuser"
