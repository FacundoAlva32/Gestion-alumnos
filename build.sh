#!/usr/bin/env bash
set -o errexit

echo "🔧 Installing dependencies..."
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo "🗃️ Applying database migrations..."
python manage.py migrate

echo "👤 Creating superuser..."
python manage.py crear_superusuario

echo "✅ Build completed successfully!"