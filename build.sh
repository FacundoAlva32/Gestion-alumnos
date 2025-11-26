#!/usr/bin/env bash
set -o errexit

echo "🔧 Installing dependencies..."
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo "🗃️ Creating migrations..."
python manage.py makemigrations --noinput

echo "🗃️ Applying migrations..."
python manage.py migrate --noinput

echo "✅ Build completed successfully!"