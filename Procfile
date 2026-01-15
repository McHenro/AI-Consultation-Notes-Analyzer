web: python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A config worker -l info
