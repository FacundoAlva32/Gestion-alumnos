#!/usr/bin/env bash
set -o errexit

echo "🔧 Instalando dependencias..."
pip install -r requirements.txt

echo "📁 Colectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "🗃️ Aplicando migraciones..."
python manage.py migrate

echo "✅ Build completado!"