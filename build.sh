#!/usr/bin/env bash
set -o errexit

echo "🔧 Installing dependencies..."
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo "🗃️ Applying ALL migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "👤 Creating superuser if needed..."
python manage.py crear_superusuario

echo "✅ Build completed successfully!"