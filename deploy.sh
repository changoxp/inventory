#!/bin/bash

echo "--- Bajando cambios de GitHub ---"
git pull origin main

echo "--- Asegurando permisos de ejecución ---"
chmod +x /var/www/inventory/venv/bin/gunicorn
chmod +x /var/www/inventory/venv/bin/python

echo "--- Actualizando dependencias y estáticos ---"
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

echo "--- Reiniciando Gunicorn ---"
sudo systemctl restart gunicorn

echo "¡Despliegue finalizado con éxito!"
