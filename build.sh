#!/usr/bin/env bash
set -o errexit

echo "🔧 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔄 Checking database connection..."
sleep 3

echo "🗃️ Creating migrations..."
# Hacer migraciones para cada app específicamente
python manage.py makemigrations usuarios --noinput
python manage.py makemigrations alumnos --noinput
python manage.py makemigrations scraper --noinput
python manage.py makemigrations --noinput

echo "🗃️ Applying migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!"